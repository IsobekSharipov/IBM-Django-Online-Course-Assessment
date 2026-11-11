from django.contrib import admin
from django.contrib.auth.models import User
from .models import Course, Lesson, Enrollment, Question, Choice, Submission


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "lesson", "grade")
    list_filter = ("lesson__course", "lesson")
    search_fields = ("question_text",)
    inlines = [ChoiceInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course")
    list_filter = ("course",)
    search_fields = ("title", "course__name")
    inlines = [QuestionInline]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "enrolled_at")
    list_filter = ("course",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "submitted_at")
    list_filter = ("submitted_at",)
    filter_horizontal = ("choices",)


# User is already registered by Django's authentication admin.
