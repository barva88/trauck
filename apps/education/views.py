from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import ConversationalExamSession, ExamSessionTag, ExamTemplate, ExamAttempt, Question, Topic
from .serializers import (
    RetellExamCompletedSerializer,
    ConversationalExamSessionListSerializer,
    ConversationalExamSessionDetailSerializer,
    ExamTemplateSerializer,
    StartAttemptResponseSerializer,
    SubmitAttemptRequestSerializer,
    SubmitAttemptResponseSerializer,
    AttemptListSerializer,
    AttemptDetailSerializer,
)
from .utils import verify_hmac_signature
from .services import start_attempt, submit_attempt
from .selectors import get_active_templates, get_user_attempts, stats_user
from .permissions import IsStaff

from apps.my_profile.models import Profile

# -------------------- Retell webhook and session APIs (existing) --------------------
class RetellExamCompletedView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        signature = request.headers.get('X-Retell-Signature') or request.headers.get('x-retell-signature')
        if not verify_hmac_signature(request.body, signature, getattr(settings, 'RETELL_WEBHOOK_SECRET', '')):
            return Response({'detail':'invalid signature'}, status=401)
        serializer = RetellExamCompletedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        allowed = getattr(settings, 'RETELL_ALLOWED_AGENT_IDS', '')
        if allowed:
            allowed_set = {a.strip() for a in allowed.split(',') if a.strip()}
            if data['agent_id'] not in allowed_set:
                return Response({'detail':'agent not allowed'}, status=403)
        user = None
        profile = None
        ext_id = data['user_external_id']
        try:
            profile = Profile.objects.get(external_id=ext_id)
            user = profile.user
        except Profile.DoesNotExist:
            # Fallback: try to match by username or email
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.filter(username=ext_id).first() or User.objects.filter(email=ext_id).first()
            if user:
                profile, _ = Profile.objects.get_or_create(user=user)
                if not profile.external_id:
                    profile.external_id = ext_id
                    profile.save(update_fields=['external_id'])
        if not user:
            return Response({'detail':'user not found'}, status=404)
        if ConversationalExamSession.objects.filter(retell_session_id=data['session_id']).exists():
            existing = ConversationalExamSession.objects.get(retell_session_id=data['session_id'])
            return Response({'id': str(existing.id)}, status=200)
        exam = data['exam']
        artifacts = data.get('artifacts') or {}
        comm = data.get('communication') or {}
        with transaction.atomic():
            session = ConversationalExamSession.objects.create(
                user=user,
                profile=profile,
                retell_session_id=data['session_id'],
                agent_id=data['agent_id'],
                channel=data['channel'],
                started_at=data['started_at'],
                ended_at=data['ended_at'],
                duration_seconds=data['duration_seconds'],
                exam_type=exam['type'],
                score_total=exam['score_total'],
                score_scale=exam['score_scale'],
                strengths=exam.get('strengths', []),
                weaknesses=exam.get('weaknesses', []),
                section_breakdown=exam.get('section_breakdown', []),
                transcript_url=artifacts.get('transcript_url',''),
                recording_url=artifacts.get('recording_url',''),
                raw_payload=request.data,
                communication_thread_id=comm.get('thread_id','')
            )
            for tag in serializer.validated_data.get('tags', []) or []:
                ExamSessionTag.objects.create(session=session, key=tag['key'], value=tag['value'])
        return Response({'id': str(session.id)}, status=201)

class MySessionsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        qs = ConversationalExamSession.objects.filter(user=request.user).order_by('-created_at')
        serializer = ConversationalExamSessionListSerializer(qs, many=True)
        return Response(serializer.data)

class SessionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id):
        session = get_object_or_404(ConversationalExamSession, pk=id, user=request.user)
        serializer = ConversationalExamSessionDetailSerializer(session)
        return Response(serializer.data)

# -------------------- Web Views --------------------
from config.menu_config import MENU_ITEMS
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    s = stats_user(request.user)
    templates = get_active_templates()
    recent = get_user_attempts(request.user)[:10]

    # Conversational sessions (legacy)
    conv_qs = ConversationalExamSession.objects.filter(user=request.user).order_by('-created_at')
    conv_sessions = list(conv_qs[:10])

    # Submitted attempts
    attempts_qs = ExamAttempt.objects.filter(user=request.user, status=ExamAttempt.STATUS_SUBMITTED).order_by('-finished_at', '-started_at')
    attempts_list = list(attempts_qs[:10])

    # Build table rows: prefer conversational; if none, use attempts
    sessions = conv_sessions
    if not sessions and attempts_list:
        rows = []
        for a in attempts_list:
            dur = 0
            if a.finished_at and a.started_at:
                dur = int((a.finished_at - a.started_at).total_seconds())
            rows.append({
                'created_at': a.finished_at or a.started_at,
                'exam_type': a.exam_template.name,
                'score_total': float(a.score_pct or 0),
                'score_scale': 'percentage',
                'duration_seconds': dur,
                'transcript_url': '',
                'recording_url': '',
            })
        sessions = rows

    # Totals and last score
    if conv_sessions:
        total_sessions = conv_qs.count()
        total_time_minutes = sum((s.duration_seconds or 0) for s in conv_qs) // 60
        try:
            last_score = float(conv_sessions[0].score_total)
        except Exception:
            last_score = 0.0
    else:
        total_sessions = attempts_qs.count()
        total_time_minutes = 0
        for a in attempts_qs:
            if a.finished_at and a.started_at:
                total_time_minutes += int((a.finished_at - a.started_at).total_seconds()) // 60
        last_attempt = attempts_qs.first()
        last_score = float(last_attempt.score_pct) if last_attempt and last_attempt.score_pct is not None else 0.0

    # Chart breakdown
    last_breakdown = []
    if conv_sessions and getattr(conv_sessions[0], 'section_breakdown', None):
        last_breakdown = conv_sessions[0].section_breakdown
    elif attempts_list:
        la = attempts_list[0]
        if la.items:
            correct = sum(1 for it in la.items if it.get('correct') is True)
            total = len(la.items)
            last_breakdown = [
                {'label': 'Correctas', 'value': correct},
                {'label': 'Incorrectas', 'value': max(0, total - correct)},
            ]

    # Latest in-progress attempt for Continue button
    in_progress = (
        ExamAttempt.objects.filter(user=request.user, status=ExamAttempt.STATUS_IN_PROGRESS)
        .order_by('-started_at')
        .first()
    )

    context = {
        'menu_items': MENU_ITEMS,
        'segment': 'education',
        'stats': s,
        'templates': templates,
        'recent_attempts': recent,
        'sessions': sessions,
        'total_sessions': total_sessions,
        'last_score': last_score,
        'total_time_minutes': total_time_minutes,
        'last_breakdown': last_breakdown,
        'in_progress': in_progress,
    }
    return render(request, 'education/dashboard.html', context)

@login_required
def exams_list(request):
    templates = get_active_templates()
    in_progress = (
        ExamAttempt.objects.filter(user=request.user, status=ExamAttempt.STATUS_IN_PROGRESS)
        .order_by('-started_at')
        .first()
    )
    first_template = templates.first() if hasattr(templates, 'first') else None
    context = {
        'menu_items': MENU_ITEMS,
        'segment': 'education',
        'templates': templates,
        'in_progress': in_progress,
        'first_template': first_template,
    }
    return render(request, 'education/bank.html', context)

@login_required
def attempt_take(request, id):
    attempt = get_object_or_404(ExamAttempt, id=id, user=request.user)
    items = attempt.items or []
    items_count = len(items) if items else (attempt.exam_template.num_questions or 20)
    try:
        current_idx = int(request.GET.get('q', 0))
    except Exception:
        current_idx = 0
    current_idx = max(0, min(current_idx, max(items_count - 1, 0)))
    current_item = items[current_idx] if items and 0 <= current_idx < len(items) else None
    nav = [{'idx': i, 'qid': items[i].get('question_id') if i < len(items) else None} for i in range(items_count)]

    # Remaining time until expiration (client countdown)
    expire_minutes = int(getattr(settings, 'EDU_EXPIRE_MINUTES', 120))
    expire_at = attempt.started_at + timezone.timedelta(minutes=expire_minutes)
    remaining_seconds = int(max(0, (expire_at - timezone.now()).total_seconds()))

    context = {
        'menu_items': MENU_ITEMS,
        'segment': 'education',
        'attempt': attempt,
        'current_idx': current_idx,
        'items_count': items_count,
        'current_item': current_item,
        'nav': nav,
        'remaining_seconds': remaining_seconds,
    }
    return render(request, 'education/exam_take.html', context)

@login_required
def attempt_submit(request, id):
    if request.method != 'POST':
        return redirect('education:attempt_take', id=id)
    import json
    from django.contrib import messages
    is_json = request.headers.get('Content-Type', '').startswith('application/json') or \
              'application/json' in request.headers.get('Accept', '') or \
              request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    payload = {}
    if is_json:
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            payload = {}
    else:
        payload = request.POST
    answers = payload.get('answers') or []
    try:
        res = submit_attempt(request.user, id, answers)
    except Exception as e:
        if is_json:
            return JsonResponse({'status': 'ERROR', 'detail': str(e)}, status=400)
        messages.error(request, f'No se pudo enviar el examen: {e}')
        return redirect('education:attempt_take', id=id)
    if is_json:
        return JsonResponse(res)
    if res.get('status') == 'OK':
        return redirect('education:attempt_result', id=id)
    return redirect('education:attempt_take', id=id)

@login_required
def attempt_result(request, id):
    attempt = get_object_or_404(ExamAttempt, id=id, user=request.user)
    from django.conf import settings as djsettings
    context = {
        'menu_items': MENU_ITEMS,
        'segment': 'education',
        'attempt': attempt,
        'reveal_correct': getattr(djsettings, 'EDU_REVEAL_CORRECT_ANSWERS', False),
    }
    return render(request, 'education/exam_result.html', context)

@login_required
def history(request):
    qs = get_user_attempts(request.user)
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page') or 1)

    # Add latest in-progress attempt for quick continue action
    in_progress = (
        ExamAttempt.objects.filter(user=request.user, status=ExamAttempt.STATUS_IN_PROGRESS)
        .order_by('-started_at')
        .first()
    )

    context = {
        'menu_items': MENU_ITEMS,
        'segment': 'education',
        'page_obj': page_obj,
        'in_progress': in_progress,
    }
    return render(request, 'education/history.html', context)

# -------------------- API Endpoints --------------------
class TemplatesAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        data = ExamTemplateSerializer(get_active_templates(), many=True).data
        return Response(data)

class StartAttemptAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        template_id = request.data.get('template_id')
        r = start_attempt(request.user, template_id)
        return Response(r)

class SubmitAttemptAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id):
        s = SubmitAttemptRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        r = submit_attempt(request.user, id, s.validated_data['answers'])
        return Response(r)

class AttemptsHistoryAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        qs = get_user_attempts(request.user)
        ser = AttemptListSerializer(qs, many=True)
        return Response(ser.data)
