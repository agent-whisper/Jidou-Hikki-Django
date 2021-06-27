from django import forms


class JidouHikkiUserCreationForm(forms.Form):
    username = forms.CharField(label="Username")


class NotebookForm(forms.Form):
    title = forms.CharField(label="Book's Title", max_length=100)
    description = forms.CharField(widget=forms.Textarea)


class NotePageForm(forms.Form):
    title = forms.CharField(label="Page's Title")
    content = forms.CharField(widget=forms.Textarea)


class AnalysisForm(forms.Form):
    content = forms.CharField(
        label="",
        widget=forms.Textarea(
            attrs={
                "placeholder": "Japanese text (max 100 characters)",
                "maxlength": 100,
            }
        ),
    )
