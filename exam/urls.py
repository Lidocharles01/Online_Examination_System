from django.urls import path
from . import views

urlpatterns = [
    path('quiz/<int:code>', views.quiz, name='quiz'),
    path('addQuestion/<int:code>/<int:quiz_id>', views.addQuestion, name='addQuestion'),
    # Add new URLs for additional functionalities
    path('allQuizzes/<int:code>', views.allQuizzes, name='allQuizzes'),
    path('quizSummary/<int:code>/<int:quiz_id>', views.quizSummary, name='quizSummary'),
    path('myQuizzes/<int:code>', views.myQuizzes, name='myQuizzes'),
    path('startQuiz/<int:code>/<int:quiz_id>', views.startQuiz, name='startQuiz'),
    path('studentAnswer/<int:code>/<int:quiz_id>', views.studentAnswer, name='studentAnswer'),
    path('quizResult/<int:code>/<int:quiz_id>', views.quizResult, name='quizResult'),
    path('editQuiz/<int:code>/<int:quiz_id>', views.editQuiz, name='editQuiz'),
    path('deleteQuiz/<int:code>/<int:quiz_id>', views.deleteQuiz, name='deleteQuiz'),
    path('editQuestion/<int:code>/<int:quiz_id>/<int:question_id>', views.editQuestion, name='editQuestion'),
]
