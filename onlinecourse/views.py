from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from .models import Course, Enrollment, Question, Choice, Submission


def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, "onlinecourse/course_details_bootstrap.html", {
        "course": course,
    })


@login_required
def submit(request, course_id):
    """Save the student's selected answers for the course exam."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    course = get_object_or_404(Course, pk=course_id)
    enrollment = get_object_or_404(
        Enrollment, course=course, user=request.user
    )

    questions = Question.objects.filter(lesson__course=course)
    valid_choices = Choice.objects.filter(question__in=questions)
    selected_ids = []

    for question in questions:
        for raw_id in request.POST.getlist(f"question_{question.id}"):
            try:
                selected_ids.append(int(raw_id))
            except (TypeError, ValueError):
                continue

    selected_choices = valid_choices.filter(pk__in=selected_ids)
    submission = Submission.objects.create(enrollment=enrollment)
    submission.choices.set(selected_choices)

    return redirect(
        "onlinecourse:show_exam_result",
        course_id=course.id,
        submission_id=submission.id,
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    """Calculate the score and show the result of an exam submission."""
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(
        Submission,
        pk=submission_id,
        enrollment__course=course,
        enrollment__user=request.user,
    )

    questions = list(
        Question.objects.filter(lesson__course=course)
        .prefetch_related("choices")
    )
    selected_ids = set(submission.choices.values_list("id", flat=True))
    total_score = sum(question.grade for question in questions)
    earned_score = 0
    question_results = []

    for question in questions:
        choices = list(question.choices.all())
        correct_ids = {choice.id for choice in choices if choice.is_correct}
        chosen_ids = {choice.id for choice in choices if choice.id in selected_ids}
        is_correct = chosen_ids == correct_ids and bool(correct_ids)
        if is_correct:
            earned_score += question.grade

        question_results.append({
            "question": question,
            "choices": choices,
            "selected_ids": chosen_ids,
            "correct_ids": correct_ids,
            "is_correct": is_correct,
        })

    percentage = (earned_score / total_score * 100) if total_score else 0
    passed = total_score > 0 and percentage >= 70

    return render(request, "onlinecourse/exam_result.html", {
        "course": course,
        "submission": submission,
        "question_results": question_results,
        "earned_score": earned_score,
        "total_score": total_score,
        "percentage": percentage,
        "passed": passed,
    })
