from django import forms
from quizzes.models import Question

class QuizAnswerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        
        self.question = question
        
        if question.question_type == 'mcq':
            choices = []
            if question.option_a:
                choices.append(('a', f"A) {question.option_a}"))
            if question.option_b:
                choices.append(('b', f"B) {question.option_b}"))
            if question.option_c:
                choices.append(('c', f"C) {question.option_c}"))
            if question.option_d:
                choices.append(('d', f"D) {question.option_d}"))
            
            self.fields['answer'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                label=question.question_text
            )
            
        elif question.question_type == 'true_false':
            self.fields['answer'] = forms.ChoiceField(
                choices=[('a', 'True'), ('b', 'False')],
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                label=question.question_text
            )
            
        elif question.question_type == 'short_answer':
            self.fields['answer'] = forms.CharField(
                widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Type your answer here...'}),
                label=question.question_text,
                required=False
            )