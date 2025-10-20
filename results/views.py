from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Max, Min
from django.utils import timezone
from datetime import timedelta
from quizzes.models import Quiz  # Only import Quiz from quizzes
from results.models import QuizSubmission  # Import QuizSubmission from results
from users.models import CustomUser

@login_required
def dashboard(request):
    """Main dashboard for users and admins"""
    if request.user.is_staff or getattr(request.user, 'role', None) == 'admin':
        return admin_dashboard(request)
    else:
        return user_dashboard(request)

def user_dashboard(request):
    """Dashboard for regular users"""
    # Get user's quiz submissions
    user_submissions = QuizSubmission.objects.filter(user=request.user).select_related('quiz')
    
    # Calculate statistics
    total_quizzes_taken = user_submissions.filter(is_completed=True).count()
    average_score = user_submissions.filter(is_completed=True).aggregate(Avg('score'))['score__avg'] or 0
    best_score = user_submissions.filter(is_completed=True).aggregate(Max('score'))['score__max'] or 0
    
    # Recent activity (last 5 submissions)
    recent_submissions = user_submissions.order_by('-started_at')[:5]
    
    # Quiz performance by category (you can extend this later)
    quiz_performance = []
    for submission in user_submissions.filter(is_completed=True):
        quiz_performance.append({
            'quiz': submission.quiz,
            'score': submission.score,
            'date': submission.completed_at
        })
    
    context = {
        'total_quizzes_taken': total_quizzes_taken,
        'average_score': round(average_score, 1),
        'best_score': round(best_score, 1),
        'recent_submissions': recent_submissions,
        'quiz_performance': quiz_performance[:5],  # Last 5 quizzes
    }
    
    return render(request, 'results/dashboard.html', context)

def admin_dashboard(request):
    """Dashboard for administrators"""
    # Overall statistics
    total_quizzes = Quiz.objects.filter(is_active=True).count()
    total_users = CustomUser.objects.count()
    total_submissions = QuizSubmission.objects.count()
    completed_submissions = QuizSubmission.objects.filter(is_completed=True).count()
    
    # Recent activity
    recent_submissions = QuizSubmission.objects.select_related('user', 'quiz').order_by('-started_at')[:10]
    
    # Quiz statistics
    quiz_stats = Quiz.objects.filter(is_active=True).annotate(
        submission_count=Count('submissions'),
        avg_score=Avg('submissions__score'),
        best_score=Max('submissions__score')
    ).order_by('-created_at')[:5]
    
    # User activity (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_users = CustomUser.objects.filter(date_joined__gte=seven_days_ago).count()
    recent_submissions_count = QuizSubmission.objects.filter(started_at__gte=seven_days_ago).count()
    
    context = {
        'total_quizzes': total_quizzes,
        'total_users': total_users,
        'total_submissions': total_submissions,
        'completed_submissions': completed_submissions,
        'recent_submissions': recent_submissions,
        'quiz_stats': quiz_stats,
        'recent_users': recent_users,
        'recent_submissions_count': recent_submissions_count,
    }
    
    return render(request, 'results/admin_dashboard.html', context)

@login_required
def submission_history(request):
    """User's submission history"""
    submissions = QuizSubmission.objects.filter(user=request.user).select_related('quiz').order_by('-started_at')
    
    context = {
        'submissions': submissions
    }
    
    return render(request, 'results/submission_history.html', context)

@login_required
def submission_detail(request, submission_id):
    """Detailed view of a specific submission"""
    submission = get_object_or_404(QuizSubmission, id=submission_id, user=request.user)
    user_answers = submission.user_answers.all().select_related('question')
    
    context = {
        'submission': submission,
        'user_answers': user_answers
    }
    
    return render(request, 'results/submission_detail.html', context)

@login_required
def quiz_analytics(request, quiz_id):
    """Detailed analytics for a specific quiz (admin only)"""
    if not request.user.is_staff and getattr(request.user, 'role', None) != 'admin':
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You don't have permission to view this page.")
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    submissions = QuizSubmission.objects.filter(quiz=quiz, is_completed=True)
    
    # Basic statistics
    total_attempts = submissions.count()
    average_score = submissions.aggregate(Avg('score'))['score__avg'] or 0
    best_score = submissions.aggregate(Max('score'))['score__max'] or 0
    worst_score = submissions.aggregate(Min('score'))['score__min'] or 0
    
    # Score distribution
    score_ranges = {
        '90-100': submissions.filter(score__gte=90).count(),
        '80-89': submissions.filter(score__gte=80, score__lt=90).count(),
        '70-79': submissions.filter(score__gte=70, score__lt=80).count(),
        '60-69': submissions.filter(score__gte=60, score__lt=70).count(),
        '0-59': submissions.filter(score__lt=60).count(),
    }
    
    # Question analysis
    question_stats = []
    for question in quiz.questions.all():
        correct_answers = question.useranswer_set.filter(is_correct=True).count()
        total_answers = question.useranswer_set.count()
        accuracy = (correct_answers / total_answers * 100) if total_answers > 0 else 0
        
        question_stats.append({
            'question': question,
            'correct_answers': correct_answers,
            'total_answers': total_answers,
            'accuracy': round(accuracy, 1)
        })
    
    context = {
        'quiz': quiz,
        'total_attempts': total_attempts,
        'average_score': round(average_score, 1),
        'best_score': round(best_score, 1),
        'worst_score': round(worst_score, 1),
        'score_ranges': score_ranges,
        'question_stats': question_stats,
        'submissions': submissions.order_by('-score')[:10]  # Top 10 performances
    }
    
    return render(request, 'results/quiz_analytics.html', context)