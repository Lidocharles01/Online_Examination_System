from django.db import models
from main.models import Student, Course

class Quiz(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    publish_status = models.BooleanField(default=False, null=True, blank=True)
    started = models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Quizzes"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def duration(self):
        return self.end - self.start

    def duration_in_seconds(self):
        return (self.end - self.start).total_seconds()

    def total_questions(self):
        return Question.objects.filter(quiz=self).count()

    def question_sl(self):
        return Question.objects.filter(quiz=self).count() + 1

    def total_marks(self):
        return Question.objects.filter(quiz=self).aggregate(total_marks=models.Sum('marks'))['total_marks']

    def starts(self):
        return self.start.strftime("%a, %d-%b-%y at %I:%M %p")

    def ends(self):
        return self.end.strftime("%a, %d-%b-%y at %I:%M %p")

    def attempted_students(self):
        return Student.objects.filter(studentanswer__quiz=self).distinct().count()

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.TextField()
    marks = models.IntegerField(default=0, null=False)
    explanation = models.TextField(null=True, blank=True)

    QUESTION_FORMAT_CHOICES = [
        ('TF', 'True/False'),
        ('MCQ', 'Multiple Choice Question'),
        ('FIB', 'Fill in the Blank'),
    ]
    format = models.CharField(max_length=3, choices=QUESTION_FORMAT_CHOICES, default='MCQ')

    # Fields specific to True/False
    is_true = models.BooleanField(default=True)

    # Fields specific to MCQ
    option1 = models.TextField(null=True, blank=True)
    option2 = models.TextField(null=True, blank=True)
    option3 = models.TextField(null=True, blank=True)
    option4 = models.TextField(null=True, blank=True)

    # Fields specific to Fill in the Blank
    correct_answer = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.question

    def get_answer(self):
        if self.format == 'TF':
            return 'True' if self.is_true else 'False'
        elif self.format == 'MCQ':
            return self.correct_answer
        elif self.format == 'FIB':
            return self.correct_answer

    def total_correct_answers(self):
        return StudentAnswer.objects.filter(question=self, answer=self.get_answer()).count()

    def total_wrong_answers(self):
        return StudentAnswer.objects.filter(question=self).exclude(answer=self.get_answer()).count()

class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255, null=True, blank=True)
    marks = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.student.name} - {self.quiz.title} - {self.question.question}"

    class Meta:
        unique_together = ('student', 'quiz', 'question')
