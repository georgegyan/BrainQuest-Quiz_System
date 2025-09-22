from django import forms
from .models import Quiz, Question

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'duration']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'correct_answer', 'points']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-control', 'id': 'question-type'}),
            'option_a': forms.TextInput(attrs={'class': 'form-control'}),
            'option_b': forms.TextInput(attrs={'class': 'form-control'}),
            'option_c': forms.TextInput(attrs={'class': 'form-control'}),
            'option_d': forms.TextInput(attrs={'class': 'form-control'}),
            'correct_option': forms.Select(attrs={'class': 'form-control'}),
            'correct_answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'points': forms.NumberInput(attrs={'class': 'form-control'}),
        }