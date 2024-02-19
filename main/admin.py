from django.contrib import admin
from .models import Student, Faculty, Course, Department, Announcement,Material

class StudentAdmin(admin.ModelAdmin):
    readonly_fields = ('student_id','role')

class FacultyAdmin(admin.ModelAdmin):
    readonly_fields = ('faculty_id','role')

class CourseAdmin(admin.ModelAdmin):
    readonly_fields = ('code',)

class DepartmentAdmin(admin.ModelAdmin):
    readonly_fields = ('department_id',)

admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Course,CourseAdmin)
admin.site.register(Department,DepartmentAdmin)
admin.site.register(Announcement)
admin.site.register(Material)