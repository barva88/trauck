from django.utils import timezone
from django.db import transaction
from django.conf import settings
from .models import ExamTemplate, ExamAttempt, Question
from .selectors import get_random_questions
from apps.billing.services.stripe_service import debit_credits, can_consume


DEFAULT_PASS_THRESHOLD = float(getattr(settings, 'EDU_PASS_THRESHOLD', 70))
EXPIRE_MINUTES = int(getattr(settings, 'EDU_EXPIRE_MINUTES', 120))
EXAM_COST_DEFAULT = int(getattr(settings, 'BILLING_DEFAULT_EXAM_COST_CREDITS', 1))


def start_attempt(user, template_id):
    template = ExamTemplate.objects.get(id=template_id, is_active=True)
    # Check for sufficient credits before starting
    if not can_consume(user, 'exam', 1):
        return {'status': 'INSUFFICIENT_CREDITS'}

    # Resume if there is a recent IN_PROGRESS
    cutoff = timezone.now() - timezone.timedelta(minutes=EXPIRE_MINUTES)
    existing = ExamAttempt.objects.filter(user=user, exam_template=template, status=ExamAttempt.STATUS_IN_PROGRESS, started_at__gte=cutoff).first()
    if existing:
        return {'status': 'OK', 'attempt_id': existing.id, 'items': existing.items}

    ids = get_random_questions(template)
    items = []
    q_map = {q.id: q for q in Question.objects.filter(id__in=ids)}
    for qid in ids:
        q = q_map[qid]
        items.append({
            'question_id': q.id,
            'type': q.type,
            'text': q.text,
            'image': q.image.url if q.image else None,
            'choices': q.choices if q.type == Question.TYPE_SC else [],
        })

    attempt = ExamAttempt.objects.create(user=user, exam_template=template, items=items)
    return {'status': 'OK', 'attempt_id': attempt.id, 'items': items}


@transaction.atomic
def submit_attempt(user, attempt_id, answers_payload):
    attempt = ExamAttempt.objects.select_for_update().get(id=attempt_id, user=user)
    if attempt.status == ExamAttempt.STATUS_SUBMITTED:
        # idempotent return
        return {'status': 'OK', 'attempt_id': attempt.id, 'score_pct': float(attempt.score_pct or 0), 'passed': attempt.passed}
    if attempt.status != ExamAttempt.STATUS_IN_PROGRESS:
        return {'status': 'INVALID_STATE'}

    # Validate answers and require complete set
    ans_map = {}
    for item in answers_payload:
        try:
            qid = int(item.get('question_id'))
        except Exception:
            continue
        sel = item.get('selected')
        ans_map[qid] = sel

    q_ids = [i['question_id'] for i in attempt.items]
    q_map = {q.id: q for q in Question.objects.filter(id__in=q_ids)}

    # Detect missing or invalid answers (do not submit if incomplete)
    missing_indices = []
    for idx, it in enumerate(attempt.items):
        q = q_map.get(it['question_id'])
        if not q:
            continue
        sel = ans_map.get(q.id, None)
        if q.type == Question.TYPE_TF:
            valid = isinstance(sel, str) and sel.lower() in ('true', 'false')
        else:
            keys = {str(o.get('key')) for o in (q.choices or [])}
            valid = sel in keys
        if not valid:
            missing_indices.append(idx)
    if missing_indices:
        # Keep IN_PROGRESS, do not change attempt
        return {
            'status': 'INCOMPLETE',
            'missing_indices': missing_indices,
            'missing_count': len(missing_indices),
            'attempt_id': attempt.id,
        }

    # Grade server-side (all answers present)
    correct = 0
    evaluated_items = []

    for it in attempt.items:
        q = q_map[it['question_id']]
        sel = ans_map.get(q.id)
        if q.type == Question.TYPE_TF:
            is_correct = str(sel).lower() == str(q.correct_answer).lower()
        else:
            is_correct = str(sel) == str(q.correct_answer)
        if is_correct:
            correct += 1
        evaluated_items.append({
            'question_id': q.id,
            'type': q.type,
            'text': q.text,
            'selected': sel,
            'correct': is_correct,
            'correct_answer': q.correct_answer if getattr(settings, 'EDU_REVEAL_CORRECT_ANSWERS', False) else None,
        })

    total = len(evaluated_items) or 1
    score_pct = round((correct / total) * 100.0, 2)
    passed = score_pct >= DEFAULT_PASS_THRESHOLD

    attempt.items = evaluated_items
    attempt.score_pct = score_pct
    attempt.passed = passed
    attempt.status = ExamAttempt.STATUS_SUBMITTED
    attempt.finished_at = timezone.now()

    # debit credits exactly once
    if attempt.credits_spent == 0:
        cost = int(getattr(settings, 'BILLING_DEFAULT_EXAM_COST_CREDITS', EXAM_COST_DEFAULT))
        debit_credits(user, 'exam', cost, {'source': 'education', 'attempt_id': attempt.id})
        attempt.credits_spent = cost

    attempt.save(update_fields=['items', 'score_pct', 'passed', 'status', 'finished_at', 'credits_spent'])
    return {'status': 'OK', 'attempt_id': attempt.id, 'score_pct': float(score_pct), 'passed': passed}


def expire_attempts():
    cutoff = timezone.now() - timezone.timedelta(minutes=EXPIRE_MINUTES)
    stale = ExamAttempt.objects.filter(status=ExamAttempt.STATUS_IN_PROGRESS, started_at__lt=cutoff)
    count = stale.update(status=ExamAttempt.STATUS_EXPIRED)
    return count
