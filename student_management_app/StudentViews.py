from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from student_management_app.models import Students, Courses, Subjects, CustomUser, Attendance, AttendanceReport, \
    LeaveReportStudent, FeedbackStudents
from datetime import datetime

@login_required
def student_home(request):
    student_obj = Students.objects.get(admin=request.user.id)
    attendance_count = AttendanceReport.objects.filter(student_id=student_obj).count()
    attendance_present_count = AttendanceReport.objects.filter(student_id=student_obj,status=True).count()
    attendance_absent_count = AttendanceReport.objects.filter(student_id=student_obj, status=False).count()

    course = Courses.objects.get(id=student_obj.course_id.id)
    subjects_count = Subjects.objects.filter(course_id=course).count()

    subject_name = []
    data_present = []
    data_abesent = []
    subject_data = Subjects.objects.filter(course_id=student_obj.course_id)
    for subject in subject_data:
        attendance=Attendance.objects.filter(subject_id=subject.id)
        attendance_present_bar_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=True).count()
        attendance_absent_bar_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=False).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_bar_count)
        data_abesent.append(attendance_absent_bar_count)

    return render(request, "student_template/student_home_template.html",
                  {"attendance_count" : attendance_count,
                   "attendance_present_count" : attendance_present_count,
                   "attendance_absent_count" : attendance_absent_count,
                   "subjects_count" : subjects_count,
                   "data_name" : subject_name,
                   "data1" : data_present,
                   "data2" : data_abesent})

@login_required
def student_view_attendance(request):
    student  = Students.objects.get(admin=request.user.id)
    course   = student.course_id
    subjects = Subjects.objects.filter(course_id=course)
    return render(request, "student_template/student_view_attendance_template.html", {"subjects" : subjects})

@login_required
def student_view_attendance_post(request):
    subject_id = request.POST.get("subject")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    start_date_parse = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_parse   = datetime.strptime(end_date, "%Y-%m-%d").date()
    subject_model = Subjects.objects.get(id=subject_id)
    user_model    = CustomUser.objects.get(id=request.user.id)
    student_model = Students.objects.get(admin=user_model)

    attendance = Attendance.objects.filter(attendance_date__range=(start_date_parse, end_date_parse), subject_id=subject_model)
    attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendance, student_id=student_model)

    # for attendance_report in attendance_reports:
    #     print("Date : "+str(attendance_report.attendance_id.attendance_date), "status : "+str(attendance_report.status))

    return render(request, "student_template/student_data_attendance_template.html", {"attendance_reports" : attendance_reports})

@login_required
def student_apply_leave(request):
    student_obj = Students.objects.get(admin=request.user.id)
    leave_data = LeaveReportStudent.objects.filter(student_id=student_obj)
    return render(request, "student_template/student_apply_leave_template.html", {"leave_data": leave_data})

@login_required
def student_apply_leave_save(request):
    if request.method != "POST":
        return HttpResponseRedirect("/student_apply_leave")
    else:
        leave_date = request.POST.get("leave_date")
        leave_message = request.POST.get("leave_message")

        # As LeaveReport has staff as foreign key so staff model to be passed
        student_model = Students.objects.get(admin=request.user.id)

    try:
        leave_report = LeaveReportStudent(student_id=student_model,
                                        leave_date=leave_date,
                                        leave_message=leave_message,
                                        leave_status=0)
        leave_report.save()
        messages.success(request, f"Successfully applied for leave by student")
        return HttpResponseRedirect("/student_apply_leave")
    except Exception as e:
        messages.error(request, f"Failed to apply for leave by student with reason {e}")
        return HttpResponseRedirect("/student_apply_leave")

@login_required
def student_feedback(request):
    student_obj = Students.objects.get(admin=request.user.id)
    feedback_data = FeedbackStudents.objects.filter(student_id=student_obj)
    return render(request, "student_template/student_feedback_template.html", {"feedback_data": feedback_data})

@login_required
def student_feedback_save(request):
    if request.method != "POST":
        return HttpResponseRedirect("/student_feedback")
    else:
        feedback_message = request.POST.get("feedback_message")

        # As LeaveReport has staff as foreign key so staff model to be passed
        student_model = Students.objects.get(admin=request.user.id)

    try:
        feedback = FeedbackStudents(student_id=student_model,
                                  feedback_message=feedback_message,
                                  feedback_reply="Reply awaited from admin")
        feedback.save()
        messages.success(request, f"Successfully provided feedback by student")
        return HttpResponseRedirect("/student_feedback")
    except Exception as e:
        messages.error(request, f"Failed to provide feedback by student with reason {e}")
        return HttpResponseRedirect("/student_feedback")