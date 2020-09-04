from django import forms

class ContactForm(forms.Form):
    from_Email = forms.EmailField(required=True, max_length=50)
    subject = forms.CharField(required=True, max_length=100)
    message = forms.CharField(widget=forms.Textarea, required=True)

