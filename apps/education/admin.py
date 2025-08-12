from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
import csv, io, json

from .models import ConversationalExamSession, ExamSessionTag, Topic, Question, ExamTemplate, ExamAttempt
from .forms import QuestionsImportForm

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name','slug','is_active')
    list_filter = ('is_active',)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id','short_text','topic','type','difficulty','is_active','created_at')
    list_filter = ('topic','type','difficulty','is_active','created_at')
    search_fields = ('text',)
    actions = ['make_active','make_inactive','export_csv']
    change_list_template = 'admin/education/question_changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv), name='education_question_import'),
        ]
        return custom + urls

    def short_text(self, obj):
        return (obj.text[:60] + '...') if len(obj.text) > 60 else obj.text

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = 'Activar seleccionadas'

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = 'Desactivar seleccionadas'

    def export_csv(self, request, queryset):
        response = render(request, 'admin/education/question_export.csv', {'rows': queryset}, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="questions.csv"'
        return response
    export_csv.short_description = 'Exportar CSV'

    def import_csv(self, request):
        if request.method == 'POST':
            form = QuestionsImportForm(request.POST, request.FILES)
            if form.is_valid():
                f = form.cleaned_data['file']
                data = f.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(data))
                created = 0
                for row in reader:
                    try:
                        topic_name = row.get('topic') or 'General'
                        topic, _ = Topic.objects.get_or_create(name=topic_name, defaults={'slug': topic_name.lower().replace(' ','-')})
                        qtype = row['type']
                        text = row['text']
                        difficulty = row.get('difficulty') or 'medium'
                        choices_raw = row.get('choices') or '[]'
                        choices = json.loads(choices_raw) if qtype == 'SC' else []
                        correct = row['correct_answer']
                        q = Question(topic=topic, type=qtype, text=text, difficulty=difficulty, choices=choices, correct_answer=correct)
                        q.full_clean()
                        q.save()
                        created += 1
                    except Exception as e:
                        messages.error(request, f"Error en fila: {row}. Detalle: {e}")
                messages.success(request, f"Importadas {created} preguntas correctamente.")
                return redirect('..')
        else:
            form = QuestionsImportForm()
        context = {'form': form, 'title':'Importar preguntas desde CSV'}
        return render(request, 'admin/education/question_import.html', context)

@admin.register(ExamTemplate)
class ExamTemplateAdmin(admin.ModelAdmin):
    list_display = ('name','topic','num_questions','is_active')
    list_filter = ('is_active','topic')

@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('id','user','exam_template','score_pct','passed','status','started_at','finished_at')
    list_filter = ('status','passed','exam_template__topic')
    readonly_fields = ('user','exam_template','started_at','finished_at','score_pct','passed','items','credits_spent','status')

@admin.register(ConversationalExamSession)
class ConversationalExamSessionAdmin(admin.ModelAdmin):
    list_display = ('id','user','agent_id','channel','exam_type','score_total','score_scale','created_at')
    list_filter = ('channel','exam_type','score_scale','agent_id','created_at')
    search_fields = ('retell_session_id','user__username','user__email')

@admin.register(ExamSessionTag)
class ExamSessionTagAdmin(admin.ModelAdmin):
    list_display = ('session','key','value')
    search_fields = ('key','value','session__retell_session_id')
