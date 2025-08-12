from django.db.models import Count, Q, Avg
from django.utils import timezone
from .models import ExamTemplate, Question, ExamAttempt, Topic
import random
import math


def get_active_templates():
    return ExamTemplate.objects.filter(is_active=True).select_related('topic')


def _pick_by_difficulty(qs_base, difficulty, n):
    ids = list(qs_base.filter(difficulty=difficulty).values_list('id', flat=True))
    random.shuffle(ids)
    return ids[:max(0, n)]


def get_random_questions(template: ExamTemplate):
    qs_base = Question.objects.filter(is_active=True)
    if template.topic_id:
        qs_base = qs_base.filter(topic_id=template.topic_id)
    total = template.num_questions or 20
    buckets = {'easy': 0, 'medium': 0, 'hard': 0}
    if template.difficulty_mix:
        buckets = {
            'easy': round(total * (int(template.difficulty_mix.get('easy', 0)) / 100.0)),
            'medium': round(total * (int(template.difficulty_mix.get('medium', 0)) / 100.0)),
            'hard': round(total * (int(template.difficulty_mix.get('hard', 0)) / 100.0)),
        }
        # Adjust rounding to match total
        diff = total - sum(buckets.values())
        for k in ['medium','easy','hard']:
            if diff == 0:
                break
            buckets[k] += 1 if diff > 0 else -1
            diff = total - sum(buckets.values())
    else:
        # Even mix if not specified
        per = total // 3
        buckets = {'easy': per, 'medium': per, 'hard': total - 2 * per}

    selected_ids = []
    for level in ['easy','medium','hard']:
        selected_ids.extend(_pick_by_difficulty(qs_base, level, buckets[level]))

    # If shortage in any bucket, fill from remaining pool regardless of difficulty
    if len(selected_ids) < total:
        remaining = list(qs_base.exclude(id__in=selected_ids).values_list('id', flat=True))
        random.shuffle(remaining)
        selected_ids.extend(remaining[: total - len(selected_ids)])

    # Shuffle final selection and ensure max total
    random.shuffle(selected_ids)
    return selected_ids[:total]


def get_user_attempts(user, start=None, end=None):
    qs = ExamAttempt.objects.filter(user=user)
    if start:
        qs = qs.filter(started_at__gte=start)
    if end:
        qs = qs.filter(started_at__lte=end)
    return qs.select_related('exam_template', 'exam_template__topic')


def stats_user(user):
    qs = ExamAttempt.objects.filter(user=user, status='SUBMITTED')
    total = qs.count()
    passed = qs.filter(passed=True).count()
    last = qs.order_by('-started_at').first()
    by_topic = (
        qs.values('exam_template__topic__name')
        .annotate(cnt=Count('id'), avg_score=Avg('score_pct'))
        .order_by('-cnt')
    )
    return {
        'total_attempts': total,
        'pass_rate': (passed / total) * 100 if total else 0,
        'last_score': float(last.score_pct) if last and last.score_pct is not None else None,
        'by_topic': list(by_topic),
    }
