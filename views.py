from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from .models import Course, Lesson, Question, Choice, Submission


def index(request):
    courses = Course.objects.prefetch_related("lessons").all()
    return render(request, "onlinecourse/index.html", {"courses": courses})


def course_details(request, course_id):
    course = get_object_or_404(Course.objects.prefetch_related("lessons"), pk=course_id)
    return render(request, "onlinecourse/course_details_bootstrap.html", {"course": course})


@login_required
def take_exam(request, lesson_id):
    lesson = get_object_or_404(Lesson.objects.prefetch_related("questions__choices"), pk=lesson_id)
    questions = lesson.questions.all()
    if not questions.exists():
        messages.warning(request, "This lesson does not have any exam questions yet.")
    return render(request, "onlinecourse/take_exam.html", {"lesson": lesson, "questions": questions})


@login_required
def submit(request, lesson_id):
    if request.method != "POST":
        return HttpResponseBadRequest("Exam answers must be submitted with POST.")
    lesson = get_object_or_404(Lesson.objects.prefetch_related("questions__choices"), pk=lesson_id)
    questions = list(lesson.questions.all())
    if not questions:
        messages.error(request, "There are no questions to grade.")
        return redirect("course_details", course_id=lesson.course_id)

    score = 0
    results = []
    for question in questions:
        selected_id = request.POST.get(f"question_{question.id}")
        selected = question.choices.filter(pk=selected_id).first() if selected_id else None
        correct = question.choices.filter(is_correct=True).first()
        is_correct = bool(selected and selected.is_correct)
        score += int(is_correct)
        results.append({
            "question": question,
            "selected": selected,
            "correct": correct,
            "is_correct": is_correct,
        })

    submission = Submission.objects.create(
        student=request.user,
        lesson=lesson,
        score=score,
        total_questions=len(questions),
    )
    return render(request, "onlinecourse/exam_result.html", {
        "lesson": lesson,
        "submission": submission,
        "results": results,
    })


@login_required
def show_exam_result(request, submission_id):
    submission = get_object_or_404(
        Submission.objects.select_related("lesson", "lesson__course", "student"),
        pk=submission_id,
        student=request.user,
    )
    questions = submission.lesson.questions.prefetch_related("choices").all()
    results = []
    for question in questions:
        # Result details are reconstructed from the correct answer and stored score;
        # detailed selected choices are shown on the immediate submission result page.
        results.append({"question": question, "correct": question.choices.filter(is_correct=True).first()})
    return render(request, "onlinecourse/saved_exam_result.html", {
        "lesson": submission.lesson,
        "submission": submission,
        "results": results,
    })
