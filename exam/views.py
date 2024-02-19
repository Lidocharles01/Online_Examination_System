import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .models import Quiz, Question, StudentAnswer
from main.models import Student, Course, Faculty
from main.views import is_faculty_authorised, is_student_authorised
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, F, FloatField, Q, Prefetch
from django.db.models.functions import Cast
def quiz(request, code):
    try:
        course = Course.objects.get(code=code)
        if is_faculty_authorised(request, code):
            if request.method == 'POST':
                # Handle form submission for creating a quiz
                title = request.POST.get('title')
                description = request.POST.get('description')
                start = request.POST.get('start')
                end = request.POST.get('end')
                publish_status = request.POST.get('checkbox')
                quiz = Quiz(title=title, description=description, start=start,
                            end=end, publish_status=publish_status, course=course)
                quiz.save()
                # Redirect to the 'addQuestion' view with the new quiz ID
                return redirect('addQuestion', code=code, quiz_id=quiz.id)
            else:
                return render(request, 'quiz/quiz.html', {'course': course, 'faculty': Faculty.objects.get(
                    faculty_id=request.session['faculty_id'])})

        else:
            return redirect('std_login')
    except:
        return render(request, 'error.html')

def addQuestion(request, code, quiz_id):
    try:
        course = Course.objects.get(code=code)
        if is_faculty_authorised(request, code):
            quiz = Quiz.objects.get(id=quiz_id)
            if request.method == 'POST':
                # Handle form submission for adding a question
                question_text = request.POST.get('question')
                marks = request.POST.get('marks')
                explanation = request.POST.get('explanation')
                question_format = request.POST.get('question_format')

                # Create a new question based on the selected format
                if question_format == 'TF':
                    is_true = request.POST.get('is_true') == 'True'
                    question = Question(question=question_text, marks=marks, explanation=explanation,
                                        quiz=quiz, format=question_format, is_true=is_true)
                elif question_format == 'MCQ':
                    option1 = request.POST.get('option1')
                    option2 = request.POST.get('option2')
                    option3 = request.POST.get('option3')
                    option4 = request.POST.get('option4')
                    correct_answer = request.POST.get('correct_answer')
                    question = Question(question=question_text, marks=marks, explanation=explanation,
                                        quiz=quiz, format=question_format, option1=option1, option2=option2,
                                        option3=option3, option4=option4, correct_answer=correct_answer)
                elif question_format == 'FIB':
                    correct_answer_fib = request.POST.get('correct_answer_fib')
                    question = Question(question=question_text, marks=marks, explanation=explanation,
                                        quiz=quiz, format=question_format, correct_answer=correct_answer_fib)
                else:
                    # Handle other question formats as needed
                    pass

                question.save()
                # Display success message
                messages.success(request, 'Question added successfully')
                if 'saveOnly' in request.POST:
                    return redirect('allQuizzes', code=code)
                else:
                    return redirect('addQuestion', code=code, quiz_id=quiz.id)

            return render(request, 'quiz/addQuestion.html', {'course': course, 'quiz': quiz,
                                                             'faculty': Faculty.objects.get(
                                                                 faculty_id=request.session['faculty_id'])})

        else:
            return redirect('std_login')
    except:
        return render(request, 'error.html')


def allQuizzes(request, code):
    if is_faculty_authorised(request, code):
        course = Course.objects.get(code=code)
        quizzes = Quiz.objects.filter(course=course)
        for quiz in quizzes:
            quiz.total_questions = Question.objects.filter(quiz=quiz).count()
            if quiz.start < datetime.datetime.now():
                quiz.started = True
            else:
                quiz.started = False
            quiz.save()
        return render(request, 'quiz/allQuizzes.html', {'course': course, 'quizzes': quizzes,
                                                        'faculty': Faculty.objects.get(
                                                            faculty_id=request.session['faculty_id'])})
    else:
        return redirect('std_login')


def myQuizzes(request, code):
    if is_student_authorised(request, code):
        course = Course.objects.get(code=code)
        quizzes = Quiz.objects.filter(course=course)
        student = Student.objects.get(student_id=request.session['student_id'])

        # Determine which quizzes are active and which are previous
        active_quizzes = []
        previous_quizzes = []
        for quiz in quizzes:
            if quiz.end < timezone.now() or quiz.studentanswer_set.filter(student=student).exists():
                previous_quizzes.append(quiz)
            else:
                active_quizzes.append(quiz)

        # Add attempted flag to quizzes
        for quiz in quizzes:
            quiz.attempted = quiz.studentanswer_set.filter(
                student=student).exists()

        # Add total marks obtained, percentage, and total questions for previous quizzes
        for quiz in previous_quizzes:
            student_answers = quiz.studentanswer_set.filter(student=student)
            total_marks_obtained = sum([student_answer.marks for student_answer in student_answers])
            quiz.total_marks_obtained = total_marks_obtained
            quiz.total_marks = sum(
                [question.marks for question in quiz.question_set.all()])
            quiz.percentage = round(
                total_marks_obtained / quiz.total_marks * 100, 2) if quiz.total_marks != 0 else 0
            quiz.total_questions = quiz.question_set.count()

        # Add total questions for active quizzes
        for quiz in active_quizzes:
            quiz.total_questions = quiz.question_set.count()

        return render(request, 'quiz/myQuizzes.html', {
            'course': course,
            'quizzes': quizzes,
            'active_quizzes': active_quizzes,
            'previous_quizzes': previous_quizzes,
            'student': student,
        })
    else:
        return redirect('std_login')


def startQuiz(request, code, quiz_id):
    if is_student_authorised(request, code):
        course = Course.objects.get(code=code)
        quiz = Quiz.objects.get(id=quiz_id)
        questions = Question.objects.filter(quiz=quiz)
        total_questions = questions.count()

        marks = 0
        for question in questions:
            marks += question.marks
        quiz.total_marks = marks

        return render(request, 'quiz/portalStdNew.html',
                      {'course': course, 'quiz': quiz, 'questions': questions, 'total_questions': total_questions,
                       'student': Student.objects.get(student_id=request.session['student_id'])})
    else:
        return redirect('std_login')

def studentAnswer(request, code, quiz_id):
    if is_student_authorised(request, code):
        course = Course.objects.get(code=code)
        quiz = Quiz.objects.get(id=quiz_id)
        questions = Question.objects.filter(quiz=quiz)
        student = Student.objects.get(student_id=request.session['student_id'])

        for question in questions:
            answer = request.POST.get(str(question.id))
            marks = 0

            if question.format == 'MCQ':
                # For MCQ, compare the selected answer with the correct answer
                marks = question.marks if answer == question.correct_answer else 0
            elif question.format == 'TF':
                # For True/False, compare the selected answer with 'True' or 'False'
                marks = question.marks if answer == str(question.is_true) else 0
            elif question.format == 'FIB':
                # For Fill in the Blank, compare the selected answer with the correct answer
                marks = question.marks if answer.lower() == question.correct_answer.lower() else 0

            student_answer = StudentAnswer(student=student, quiz=quiz, question=question, answer=answer, marks=marks)

            # prevent duplicate answers & multiple attempts
            try:
                student_answer.save()
            except:
                return redirect('myQuizzes', code=code)

        return redirect('myQuizzes', code=code)
    else:
        return redirect('std_login')

def quizResult(request, code, quiz_id):
    if is_student_authorised(request, code):
        course = Course.objects.get(code=code)
        quiz = Quiz.objects.get(id=quiz_id)
        questions = Question.objects.filter(quiz=quiz)

        try:
            student = Student.objects.get(student_id=request.session['student_id'])
            student_answers = StudentAnswer.objects.filter(student=student, quiz=quiz)
            total_marks_obtained = sum(student_answer.marks for student_answer in student_answers)

            quiz.total_marks_obtained = total_marks_obtained
            quiz.total_marks = sum(question.marks for question in questions)

            if quiz.total_marks != 0:
                quiz.percentage = (total_marks_obtained / quiz.total_marks) * 100
                quiz.percentage = round(quiz.percentage, 2)
            else:
                quiz.percentage = 0

        except Student.DoesNotExist:
            quiz.total_marks_obtained = 0
            quiz.total_marks = 0
            quiz.percentage = 0

        for question in questions:
            student_answer = StudentAnswer.objects.get(student=student, question=question)
            question.student_answer = student_answer.answer

            # Compare student's answer with correct answer based on question format
            if question.format == 'TF':
                question.correct_answer = 'True' if question.is_true else 'False'
            elif question.format == 'MCQ':
                question.correct_answer = question.correct_answer  # Use the stored correct answer directly
            elif question.format == 'FIB':
                question.correct_answer = question.correct_answer

        student_answers = StudentAnswer.objects.filter(student=student, quiz=quiz)

        for student_answer in student_answers:
            quiz.time_taken = student_answer.created_at - quiz.start
            quiz.time_taken = quiz.time_taken.total_seconds()
            quiz.time_taken = round(quiz.time_taken, 2)
            quiz.submission_time = student_answer.created_at.strftime("%a, %d-%b-%y at %I:%M %p")

        return render(request, 'quiz/quizResult.html',
                      {'course': course, 'quiz': quiz, 'questions': questions, 'student': student})
    else:
        return redirect('std_login')

def quizSummary(request, code, quiz_id):
    if is_faculty_authorised(request, code):
        course = Course.objects.get(code=code)
        quiz = Quiz.objects.get(id=quiz_id)

        questions = Question.objects.filter(quiz=quiz)
        time = datetime.datetime.now()
        total_students = Student.objects.filter(course=course).count()

        # Inside your view function

        for question in questions:
            if question.format == 'MCQ':
                question.A_count = StudentAnswer.objects.filter(question=question, answer='A').count()
                question.B_count = StudentAnswer.objects.filter(question=question, answer='B').count()
                question.C_count = StudentAnswer.objects.filter(question=question, answer='C').count()
                question.D_count = StudentAnswer.objects.filter(question=question, answer='D').count()
            elif question.format == 'TF':
                # Add logic for True/False questions
                question.True_count = StudentAnswer.objects.filter(question=question, answer='True').count()
                question.False_count = StudentAnswer.objects.filter(question=question, answer='False').count()
            elif question.format == 'FIB':
                # Add logic for Fill in the Blank questions
                # Assuming 'answer' is the attribute for storing the correct answer
                question.correct_answers_count = StudentAnswer.objects.filter(question=question,
                                                                              answer=question.correct_answer).count()
                question.incorrect_answers_count = StudentAnswer.objects.filter(question=question).exclude(
                    answer=question.correct_answer).count()

        # Students who have attempted the quiz and their marks
        students = Student.objects.filter(course=course)
        for student in students:
            student_answers = StudentAnswer.objects.filter(student=student, quiz=quiz)
            total_marks_obtained = 0
            for student_answer in student_answers:
                total_marks_obtained += student_answer.marks
            student.total_marks_obtained = total_marks_obtained

        if request.method == 'POST':
            quiz.publish_status = True
            quiz.save()
            return redirect('quizSummary', code=code, quiz_id=quiz.id)

        # Check if the student has attempted the quiz
        for student in students:
            student.attempted = StudentAnswer.objects.filter(student=student, quiz=quiz).count() > 0

        for student in students:
            student_answers = StudentAnswer.objects.filter(student=student, quiz=quiz)
            for student_answer in student_answers:
                student.submission_time = student_answer.created_at.strftime("%a, %d-%b-%y at %I:%M %p")

        context = {
            'course': course,
            'quiz': quiz,
            'questions': questions,
            'time': time,
            'total_students': total_students,
            'students': students,
            'faculty': Faculty.objects.get(faculty_id=request.session['faculty_id'])
        }
        return render(request, 'quiz/quizSummaryFaculty.html', context)

    else:
        return redirect('std_login')


# Add the following function to your views.py
def editQuiz(request, code, quiz_id):
    if is_faculty_authorised(request, code):
        course = Course.objects.get(code=code)
        quiz = get_object_or_404(Quiz, id=quiz_id)

        if request.method == 'POST':
            # Handle form submission to update quiz details
            title = request.POST.get('title')
            description = request.POST.get('description')
            start = request.POST.get('start')
            end = request.POST.get('end')
            publish_status = request.POST.get('checkbox')

            # Update quiz details
            quiz.title = title
            quiz.description = description
            quiz.start = start
            quiz.end = end
            quiz.publish_status = publish_status
            quiz.save()

            messages.success(request, 'Quiz updated successfully')
            return redirect('allQuizzes', code=code)

        return render(request, 'quiz/editQuiz.html', {'course': course, 'quiz': quiz, 'faculty': Faculty.objects.get(
            faculty_id=request.session['faculty_id'])})
    else:
        return redirect('std_login')


def deleteQuiz(request, code, quiz_id):
    if is_faculty_authorised(request, code):
        quiz = get_object_or_404(Quiz, id=quiz_id)

        if request.method == 'POST':
            # Delete the quiz
            quiz.delete()
            messages.success(request, 'Quiz deleted successfully')
            return redirect('allQuizzes', code=code)

        return render(request, 'quiz/deleteQuiz.html', {'quiz': quiz})
    else:
        return redirect('std_login')


def editQuestion(request, code, quiz_id, question_id):
    if is_faculty_authorised(request, code):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = quiz.question_set.all()

        if request.method == 'POST':
            for question in questions:
                question_id_str = str(question.id)

                # Retrieve values based on question type
                question_text = request.POST.get(f'question_{question_id_str}')
                marks = request.POST.get(f'marks_{question_id_str}')
                explanation = request.POST.get(f'explanation_{question_id_str}')

                if question.format == 'TF':
                    is_true = request.POST.get(f'is_true_{question_id_str}') == 'True'
                    question.is_true = is_true
                elif question.format == 'MCQ':
                    question.option1 = request.POST.get(f'option1_{question_id_str}')
                    question.option2 = request.POST.get(f'option2_{question_id_str}')
                    question.option3 = request.POST.get(f'option3_{question_id_str}')
                    question.option4 = request.POST.get(f'option4_{question_id_str}')
                    question.correct_answer = request.POST.get(f'correct_answer_{question_id_str}')
                elif question.format == 'FIB':
                    question.correct_answer = request.POST.get(f'correct_answer_fib_{question_id_str}')

                # Update common fields for all question types
                question.question = question_text
                question.marks = marks
                question.explanation = explanation

                question.save()

            messages.success(request, 'Questions updated successfully')
            return redirect('allQuizzes', code=code)

        return render(request, 'quiz/editQuestion.html', {'quiz': quiz, 'questions': questions})
    else:
        return redirect('std_login')