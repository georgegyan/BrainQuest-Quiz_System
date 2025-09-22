from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from results.models import QuizSubmission, UserAnswer
from results.forms import QuizAnswerForm
from .models import Quiz, Question
from .forms import QuizForm, QuestionForm

@login_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(is_active=True)
    context = {'quizzes': quizzes}
    return render(request, 'quizzes/quiz_list.html', context)

@login_required
def quiz_create(request):
    if not request.user.is_staff and getattr(request.user, 'role', None) != 'admin':
        messages.error(request, 'You do not have permission to create quizzes.')
        return redirect('quizzes:quiz_list')
    
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()
            messages.success(request, 'Quiz created successfully!')
            return redirect('quizzes:quiz_detail', quiz_id=quiz.id)
    else:
        form = QuizForm()
    return render(request, 'quizzes/quiz_form.html', {'form': form, 'title': 'Create Quiz'})

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    questions = quiz.questions.all()
    return render(request, 'quizzes/quiz_detail.html', {'quiz': quiz, 'questions': questions})

@login_required
def question_create(request, quiz_id):
    if not request.user.is_staff and getattr(request.user, 'role', None) != 'admin':
        messages.error(request, 'You do not have permission to add questions.')
        return redirect('quizzes:quiz_list')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'Question added successfully!')
            return redirect('quizzes:quiz_detail', quiz_id=quiz.id)
    else:
        form = QuestionForm()
    
    return render(request, 'quizzes/question_form.html', {'form': form, 'quiz': quiz})

@login_required
def quiz_edit(request, quiz_id):
    if not request.user.is_staff and getattr(request.user, 'role', None) != 'admin':
        messages.error(request, 'You do not have permission to edit quizzes.')
        return redirect('quizzes:quiz_list')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated successfully!')
            return redirect('quizzes:quiz_detail', quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz)
    
    return render(request, 'quizzes/quiz_form.html', {'form': form, 'title': 'Edit Quiz', 'quiz': quiz})

@login_required
def quiz_delete(request, quiz_id):
    if not request.user.is_staff and getattr(request.user, 'role', None) != 'admin':
        messages.error(request, 'You do not have permission to delete quizzes.')
        return redirect('quizzes:quiz_list')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        quiz.is_active = False
        quiz.save()
        messages.success(request, 'Quiz deleted successfully!')
        return redirect('quizzes:quiz_list')
    return render(request, 'quizzes/quiz_confirm_delete.html', {'quiz': quiz})


@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check if user already has an active submission
    active_submission = QuizSubmission.objects.filter(
        user=request.user, 
        quiz=quiz, 
        is_completed=False
    ).first()
    
    if active_submission:
        # Resume existing quiz
        return redirect('quizzes:take_quiz', submission_id=active_submission.id)
    
    # Create new submission
    submission = QuizSubmission.objects.create(
        user=request.user,
        quiz=quiz,
        total_questions=quiz.questions.count()
    )
    
    return redirect('quizzes:take_quiz', submission_id=submission.id)

@login_required
def take_quiz(request, submission_id):
    submission = get_object_or_404(QuizSubmission, id=submission_id, user=request.user)
    
    if submission.is_completed:
        return redirect('quizzes:quiz_result', submission_id=submission.id)
    
    # Get all questions for this quiz
    questions = submission.quiz.questions.all()
    
    # Get questions that haven't been answered yet
    answered_questions = submission.user_answers.values_list('question_id', flat=True)
    current_question = questions.exclude(id__in=answered_questions).first()
    
    # If all questions answered, complete the quiz
    if not current_question:
        submission.is_completed = True
        submission.completed_at = timezone.now()
        submission.calculate_score()
        submission.save()
        return redirect('quizzes:quiz_result', submission_id=submission.id)
    
    # Calculate time remaining
    time_limit = submission.quiz.duration
    time_elapsed = (timezone.now() - submission.started_at).total_seconds() / 60
    time_remaining = max(0, time_limit - time_elapsed)
    
    # Check if time is up
    if time_remaining <= 0:
        submission.is_completed = True
        submission.completed_at = timezone.now()
        submission.calculate_score()
        submission.save()
        return redirect('quizzes:quiz_result', submission_id=submission.id)
    
    form = QuizAnswerForm(question=current_question)
    
    if request.method == 'POST':
        form = QuizAnswerForm(request.POST, question=current_question)
        if form.is_valid():
            answer_data = form.cleaned_data['answer']
            
            # Create user answer
            user_answer = UserAnswer.objects.create(
                submission=submission,
                question=current_question
            )
            
            if current_question.question_type in ['mcq', 'true_false']:
                user_answer.chosen_option = answer_data
            else: 
                user_answer.answer_text = answer_data
            
            user_answer.check_answer()
            user_answer.save()
            
            # Move to next question or complete quiz
            next_question = questions.exclude(id__in=submission.user_answers.values_list('question_id', flat=True)).first()
            if not next_question:
                submission.is_completed = True
                submission.completed_at = timezone.now()
                submission.calculate_score()
                submission.save()
                return redirect('quizzes:quiz_result', submission_id=submission.id)
            
            return redirect('quizzes:take_quiz', submission_id=submission.id)
    
    # Calculate progress
    progress = (answered_questions.count() / questions.count() * 100) if questions.count() > 0 else 0
    
    context = {
        'submission': submission,
        'question': current_question,
        'form': form,
        'time_remaining': int(time_remaining),
        'progress': int(progress),
        'current_question_number': answered_questions.count() + 1,
        'total_questions': questions.count(),
    }
    
    return render(request, 'quizzes/take_quiz.html', context)

@login_required
def quiz_result(request, submission_id):
    submission = get_object_or_404(QuizSubmission, id=submission_id, user=request.user)
    user_answers = submission.user_answers.all().select_related('question')
    
    context = {
        'submission': submission,
        'user_answers': user_answers,
    }
    
    return render(request, 'quizzes/quiz_result.html', context)