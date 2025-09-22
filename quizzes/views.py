from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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