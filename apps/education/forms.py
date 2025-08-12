from django import forms

class QuestionsImportForm(forms.Form):
    file = forms.FileField(help_text='CSV con columnas: type, topic, text, difficulty, image(optional), choices(JSON para SC), correct_answer')
