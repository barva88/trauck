from django import forms


class RefundRequestForm(forms.Form):
    purchase_id = forms.IntegerField()
    reason_text = forms.CharField(required=False, widget=forms.Textarea)
