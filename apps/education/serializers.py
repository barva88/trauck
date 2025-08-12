from rest_framework import serializers
from .models import ConversationalExamSession, ExamSessionTag, Topic, Question, ExamTemplate, ExamAttempt

class ExamSessionTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSessionTag
        fields = ['key', 'value']

class RetellExamCompletedSerializer(serializers.Serializer):
    session_id = serializers.CharField()
    agent_id = serializers.CharField()
    user_external_id = serializers.CharField()
    channel = serializers.ChoiceField(choices=['voice','web','phone','whatsapp'])
    started_at = serializers.DateTimeField()
    ended_at = serializers.DateTimeField()
    duration_seconds = serializers.IntegerField(min_value=0)
    exam = serializers.DictField()
    artifacts = serializers.DictField(required=False)
    communication = serializers.DictField(required=False)
    tags = ExamSessionTagSerializer(many=True, required=False)

    def validate_exam(self, value):
        required = ['type','score_total','score_scale','section_breakdown','strengths','weaknesses']
        for k in required:
            if k not in value:
                raise serializers.ValidationError(f"Missing exam.{k}")
        if value['score_scale'] not in ['percentage','points']:
            raise serializers.ValidationError('score_scale invalid')
        return value

class ConversationalExamSessionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationalExamSession
        fields = ['id','retell_session_id','agent_id','channel','started_at','ended_at','duration_seconds','exam_type','score_total','score_scale','section_breakdown','transcript_url','recording_url','created_at']

class ConversationalExamSessionDetailSerializer(serializers.ModelSerializer):
    tags = ExamSessionTagSerializer(many=True, read_only=True)
    class Meta:
        model = ConversationalExamSession
        fields = '__all__'

# --- New public serializers ---
class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id','name','slug']

class ExamTemplateSerializer(serializers.ModelSerializer):
    topic = TopicSerializer(read_only=True)
    class Meta:
        model = ExamTemplate
        fields = ['id','name','topic','num_questions','difficulty_mix']

class QuestionPublicSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=['TF','SC'])
    text = serializers.CharField()
    image = serializers.CharField(allow_null=True, required=False)
    choices = serializers.JSONField(required=False)

class StartAttemptResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    attempt_id = serializers.IntegerField(required=False)
    items = QuestionPublicSerializer(many=True, required=False)

class SubmitAttemptRequestSerializer(serializers.Serializer):
    answers = serializers.ListField(child=serializers.DictField(), allow_empty=False)

class SubmitAttemptResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    attempt_id = serializers.IntegerField()
    score_pct = serializers.FloatField()
    passed = serializers.BooleanField()

class AttemptListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttempt
        fields = ['id','exam_template','started_at','finished_at','score_pct','passed','status']

class AttemptDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttempt
        fields = ['id','exam_template','started_at','finished_at','score_pct','passed','status','items','credits_spent']
