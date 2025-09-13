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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make correct_answer required for short answer questions
        self.fields['correct_answer'].required = False

    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get('question_type')
        
        if question_type == 'mcq':
            # Validate that options are provided for MCQ
            if not all([cleaned_data.get('option_a'), cleaned_data.get('option_b')]):
                raise forms.ValidationError("At least options A and B are required for multiple choice questions.")
            if not cleaned_data.get('correct_option'):
                raise forms.ValidationError("Please select the correct option for multiple choice questions.")
        
        elif question_type == 'true_false':
            # For true/false, we'll use option_a as True and option_b as False
            if not cleaned_data.get('correct_option'):
                raise forms.ValidationError("Please select the correct option for true/false questions.")
        
        elif question_type == 'short_answer':
            if not cleaned_data.get('correct_answer'):
                raise forms.ValidationError("Please provide the correct answer for short answer questions.")
        
        return cleaned_data