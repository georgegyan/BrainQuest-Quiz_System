from django.db import models
from django.contrib.auth import get_user_model
from quizzes.models import Quiz, Question

User = get_user_model()

class QuizSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_submissions')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    score = models.FloatField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}%"
    
    def calculate_score(self):
        """Calculate the score based on user answers"""
        user_answers = self.user_answers.all()
        correct_count = 0
        total_questions = self.quiz.questions.count()
        
        for answer in user_answers:
            if answer.is_correct:
                correct_count += 1
        
        self.correct_answers = correct_count
        self.total_questions = total_questions
        self.score = (correct_count / total_questions * 100) if total_questions > 0 else 0
        self.save()
        
        return self.score

class UserAnswer(models.Model):
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    chosen_option = models.CharField(max_length=1, blank=True)  # For MCQ/TrueFalse
    answer_text = models.TextField(blank=True)  # For short answers
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['answered_at']
    
    def __str__(self):
        return f"{self.submission.user.username} - {self.question.question_text[:50]}"
    
    def check_answer(self):
        """Check if the user's answer is correct"""
        if self.question.question_type in ['mcq', 'true_false']:
            self.is_correct = (self.chosen_option.lower() == self.question.correct_option.lower())
        elif self.question.question_type == 'short_answer':
            # Simple case-insensitive comparison for short answers
            self.is_correct = (self.answer_text.strip().lower() == self.question.correct_answer.strip().lower())
        
        self.save()
        return self.is_correct