from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("course/<int:course_id>/", views.course_details, name="course_details"),
    path("lesson/<int:lesson_id>/exam/", views.take_exam, name="take_exam"),
    path("lesson/<int:lesson_id>/submit/", views.submit, name="submit"),
    path("exam-result/<int:submission_id>/", views.show_exam_result, name="show_exam_result"),
]
