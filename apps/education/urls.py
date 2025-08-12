from django.urls import path
from .views import (
    RetellExamCompletedView, MySessionsView, SessionDetailView,
    dashboard, exams_list, attempt_take, attempt_submit, attempt_result, history,
    TemplatesAPI, StartAttemptAPI, SubmitAttemptAPI, AttemptsHistoryAPI,
)

app_name = 'education'

urlpatterns = [
    # Web
    path('', dashboard, name='dashboard'),
    path('bank', exams_list, name='bank'),
    path('attempt/<int:id>', attempt_take, name='attempt_take'),
    path('attempt/<int:id>/submit', attempt_submit, name='attempt_submit'),
    path('attempt/<int:id>/result', attempt_result, name='attempt_result'),
    path('history', history, name='history'),

    # API
    path('api/templates/', TemplatesAPI.as_view(), name='api_templates'),
    path('api/attempts/', StartAttemptAPI.as_view(), name='api_start_attempt'),
    path('api/attempts/<int:id>/submit', SubmitAttemptAPI.as_view(), name='api_submit_attempt'),
    path('api/attempts/history', AttemptsHistoryAPI.as_view(), name='api_attempts_history'),

    # Conversational hooks (existing)
    path('retell/exam/session-completed', RetellExamCompletedView.as_view(), name='retell_exam_completed'),
    path('my-sessions', MySessionsView.as_view(), name='my_sessions'),
    path('session/<uuid:id>', SessionDetailView.as_view(), name='session_detail'),
]
