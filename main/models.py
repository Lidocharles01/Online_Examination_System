from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, EmailValidator
from froala_editor.fields import FroalaField
from django.db import models
import re

def validate_custom_email(value):
    # Define your custom email format using a regular expression
    pattern = r'^[a-z][^@\s]+@gmail\.com$'
    if not re.match(pattern, value):
        raise ValidationError('Please enter a valid email address with the domain "abcd@gmail.com".')

def validate_custom_password(value):
    # Ensure the password contains at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError('Password must contain at least one special character.')

class Student(models.Model):
    student_id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=100, unique=True, null=False)
    email = models.EmailField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        validators=[EmailValidator(message='Enter a valid email address.'), validate_custom_email]
    )
    password = models.CharField(max_length=255, null=False, validators=[MinLengthValidator(8), validate_custom_password])
    role = models.CharField(default="Student", max_length=100, null=False, blank=True,)
    course = models.ManyToManyField('Course', related_name='students', blank=True)
    photo = models.ImageField(upload_to='profile_pics', blank=True, null=False, default='profile_pics/default_student.png')
    department = models.ForeignKey('Department', on_delete=models.CASCADE, null=False, blank=False, related_name='students')

    def clean(self):
        if len(self.password) < 8:
            raise ValidationError({'password': 'Password must be at least 8 characters long.'})

    def delete(self, *args, **kwargs):
        if self.photo != 'profile_pics/default_student.png':
            self.photo.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Students'

    def __str__(self):
        return self.name

    def clean(self):
        # Check if a Department with the same name already exists
        existing_Student = Student.objects.filter(name__iexact=self.name).exclude(student_id=self.student_id)
        if existing_Student.exists():
            raise ValidationError({'name': 'A Student with this name already exists.'})
        if not all(char.isalpha() or char.isspace() or char == '_' for char in self.name):
            raise ValidationError({'name': 'Student Name must contain only alphabetic characters.'})

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate before saving
        self.name = self.name.upper()
        super().save(*args, **kwargs)


class Faculty(models.Model):
    faculty_id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=100, unique=True, null=False)
    email = models.EmailField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        validators=[EmailValidator(message='Enter a valid email address.'), validate_custom_email]
    )
    password = models.CharField(max_length=255, null=False, validators=[MinLengthValidator(8), validate_custom_password])
    department = models.ForeignKey('Department', on_delete=models.CASCADE, null=False, related_name='faculty')
    role = models.CharField(default="Faculty", max_length=100, null=False, blank=True)
    photo = models.ImageField(upload_to='profile_pics', blank=True, null=False, default='profile_pics/default_faculty.png')

    def clean(self):
        if len(self.password) < 8:
            raise ValidationError({'password': 'Password must be at least 8 characters long.'})

    def delete(self, *args, **kwargs):
        if self.photo != 'profile_pics/default_faculty.png':
            self.photo.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Faculty'

    def __str__(self):
        return self.name

    def clean(self):
        # Check if a Department with the same name already exists
        existing_faculty = Faculty.objects.filter(name__iexact=self.name).exclude(faculty_id=self.faculty_id)
        if existing_faculty.exists():
            raise ValidationError({'name': 'A Faculty with this name already exists.'})
        if not all(char.isalpha() or char.isspace() or char == '_' for char in self.name):
            raise ValidationError({'name': 'Faculty Name must contain only alphabetic characters.'})

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate before saving
        self.name = self.name.upper()
        super().save(*args, **kwargs)

class Department(models.Model):
    department_id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=100, unique=True, null=False)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.name

    def student_count(self):
        return self.students.count()

    def faculty_count(self):
        return self.faculty.count()

    def course_count(self):
        return self.courses.count()

    def clean(self):
        # Check if a Department with the same name already exists
        existing_department = Department.objects.filter(name__iexact=self.name).exclude(department_id=self.department_id)
        if existing_department.exists():
            raise ValidationError({'name': 'A department with this name already exists.'})
        if not all(char.isalpha() or char.isspace() or char == '_' for char in self.name):
            raise ValidationError({'name': 'Department Name must contain only alphabetic characters.'})

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate before saving
        self.name = self.name.upper()
        super().save(*args, **kwargs)


class Course(models.Model):
    code = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=255, null=False, unique=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=False, related_name='courses')
    faculty = models.ForeignKey(
        Faculty, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('code', 'department', 'name')
        verbose_name_plural = "Courses"

    def __str__(self):
        return self.name

    def clean(self):
        # Check if a Department with the same name already exists
        existing_Course = Course.objects.filter(name__iexact=self.name).exclude(code=self.code)
        if existing_Course.exists():
            raise ValidationError({'name': 'A Course with this name already exists.'})
        if not all(char.isalpha() or char.isspace() or char == '_' for char in self.name):
            raise ValidationError({'name': 'Course Name must contain only alphabetic characters.'})

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate before saving
        self.name = self.name.upper()
        super().save(*args, **kwargs)


class Announcement(models.Model):
    course_code = models.ForeignKey(
        Course, on_delete=models.CASCADE, null=False)
    datetime = models.DateTimeField(auto_now_add=True, null=False)
    description = FroalaField()

    class Meta:
        verbose_name_plural = "Announcements"
        ordering = ['-datetime']

    def __str__(self):
        return self.datetime.strftime("%d-%b-%y, %I:%M %p")

    def post_date(self):
        return self.datetime.strftime("%d-%b-%y, %I:%M %p")

class Material(models.Model):
    course_code = models.ForeignKey(
        Course, on_delete=models.CASCADE, null=False)
    description = models.TextField(max_length=2000, null=False)
    datetime = models.DateTimeField(auto_now_add=True, null=False)
    file = models.FileField(upload_to='materials/', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Materials"
        ordering = ['-datetime']

    def __str__(self):
        return self.description

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    def post_date(self):
        return self.datetime.strftime("%d-%b-%y, %I:%M %p")