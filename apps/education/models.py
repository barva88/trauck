from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone
import uuid

# --- New domain models ---
class Topic(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Question(models.Model):
    TYPE_TF = 'TF'
    TYPE_SC = 'SC'
    TYPE_CHOICES = (
        (TYPE_TF, 'True/False'),
        (TYPE_SC, 'Single Choice'),
    )
    DIFF_EASY = 'easy'
    DIFF_MEDIUM = 'medium'
    DIFF_HARD = 'hard'
    DIFF_CHOICES = (
        (DIFF_EASY, 'Easy'),
        (DIFF_MEDIUM, 'Medium'),
        (DIFF_HARD, 'Hard'),
    )

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    text = models.TextField()
    image = models.ImageField(upload_to='education/questions/', null=True, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFF_CHOICES, default=DIFF_MEDIUM)
    # For SC: list of options e.g. [{"key":"A","text":"..."}, ...], max 6
    choices = models.JSONField(default=list, blank=True)
    # For TF: 'true' or 'false'; For SC: the key matching choices[i].key
    correct_answer = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['topic', 'type', 'difficulty', 'is_active']),
            models.Index(fields=['-created_at']),
        ]

    def clean(self):
        if self.type == self.TYPE_SC:
            if not isinstance(self.choices, list) or len(self.choices) < 2:
                raise ValidationError('Single Choice questions require at least 2 options.')
            if len(self.choices) > 6:
                raise ValidationError('Single Choice questions support at most 6 options.')
            keys = {str(o.get('key')) for o in self.choices}
            if self.correct_answer not in keys:
                raise ValidationError('correct_answer must be one of the option keys.')
        elif self.type == self.TYPE_TF:
            if str(self.correct_answer).lower() not in ('true', 'false'):
                raise ValidationError("TF correct_answer must be 'true' or 'false'.")
            # Ignore choices for TF
            self.choices = []
        else:
            raise ValidationError('Unsupported question type.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.get_type_display()}] {self.text[:60]}"


class ExamTemplate(models.Model):
    name = models.CharField(max_length=200)
    topic = models.ForeignKey(Topic, null=True, blank=True, on_delete=models.SET_NULL, related_name='exam_templates')
    num_questions = models.PositiveIntegerField(default=20)
    difficulty_mix = models.JSONField(null=True, blank=True, help_text='e.g. {"easy":40, "medium":40, "hard":20}')
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=['is_active'])]

    def clean(self):
        if self.difficulty_mix:
            total = int(self.difficulty_mix.get('easy', 0)) + int(self.difficulty_mix.get('medium', 0)) + int(self.difficulty_mix.get('hard', 0))
            if total != 100:
                raise ValidationError('difficulty_mix percentages must sum to 100.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ExamAttempt(models.Model):
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_SUBMITTED = 'SUBMITTED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_EXPIRED = 'EXPIRED'
    STATUS_CHOICES = (
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_EXPIRED, 'Expired'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exam_attempts')
    exam_template = models.ForeignKey(ExamTemplate, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    passed = models.BooleanField(default=False)
    items = models.JSONField(default=list, help_text='[{question_id, type, selected, correct, correct_answer}]')
    credits_spent = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_IN_PROGRESS, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['-started_at']),
        ]
        ordering = ['-started_at']

    def __str__(self):
        return f"Attempt #{self.id} - {self.user} - {self.exam_template.name} - {self.status}"


class ExamSessionLink(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='session_links')
    provider = models.CharField(max_length=50)
    conversation_id = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=['provider', 'conversation_id'])]


# --- Existing conversational session models (kept) ---
class ConversationalExamSession(models.Model):
    CHANNEL_CHOICES = (
        ('voice', 'voice'),
        ('web', 'web'),
        ('phone', 'phone'),
        ('whatsapp', 'whatsapp'),
    )
    SCORE_SCALE_CHOICES = (
        ('percentage', 'percentage'),
        ('points', 'points'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='education_sessions')
    profile = models.ForeignKey('my_profile.Profile', on_delete=models.SET_NULL, null=True, blank=True, related_name='education_sessions')
    retell_session_id = models.CharField(max_length=255, unique=True, db_index=True)
    agent_id = models.CharField(max_length=255)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    duration_seconds = models.PositiveIntegerField()
    exam_type = models.CharField(max_length=255)
    score_total = models.DecimalField(max_digits=6, decimal_places=2)
    score_scale = models.CharField(max_length=20, choices=SCORE_SCALE_CHOICES)
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    section_breakdown = models.JSONField(default=list)
    transcript_url = models.URLField(blank=True)
    recording_url = models.URLField(blank=True)
    raw_payload = models.JSONField(default=dict)
    communication_thread_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class ExamSessionTag(models.Model):
    session = models.ForeignKey(ConversationalExamSession, on_delete=models.CASCADE, related_name='tags')
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        indexes = [models.Index(fields=['key', 'value'])]
