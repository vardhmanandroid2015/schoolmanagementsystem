from django.core import serializers
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from student_management_app.models import Subjects, SessionYearModel, Students, Attendance, AttendanceReport, Staffs, \
    LeaveReportStaff, FeedbackStaffs, Courses

import json

@login_required
def staff_home(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    course_id_list = []

    for subject in subjects:
        course = Courses.objects.get(id=subject.course_id.id)
        course_id_list.append(course)
    unique_course_list = list(set(course_id_list))
    print(course_id_list)
    print(unique_course_list)
    student_counts   = Students.objects.filter(course_id__in=unique_course_list).count()

    attendance_count = Attendance.objects.filter(subject_id__in=subjects).count()

    staff = Staffs.objects.get(admin=request.user.id)
    leave_count = LeaveReportStaff.objects.filter(staff_id=staff.id,leave_status=1).count()

    subject_count = subjects.count()

#### Subject - Attendance for Bar Chart1

    subject_list = []
    attendance_subject_list = []
    for subject in subjects:
        attendance_count1 = Attendance.objects.filter(subject_id=subject.id).count()
        subject_list.append(subject.subject_name)
        attendance_subject_list.append(attendance_count1)

#### Student - Attendance for Bar Chart2

    student_attendance = Students.objects.filter(course_id__in=unique_course_list)
    student_list = []
    student_list_attendance_present = []
    student_list_attendance_abesent = []
    for student in student_attendance:
        attendance_present_count = AttendanceReport.objects.filter(status=True, student_id=student.id).count()
        attendance_abesent_count = AttendanceReport.objects.filter(status=False, student_id=student.id).count()
        student_list.append(student.admin.username)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_abesent.append(attendance_abesent_count)

    return render(request, "staff_template/staff_home_template.html",
                  {"student_counts" : student_counts,
                   "attendance_count" : attendance_count,
                   "leave_count": leave_count,
                   "subject_count" : subject_count,
                   "subject_list" : subject_list,
                   "attendance_subject_list" : attendance_subject_list,
                   "student_list" : student_list,
                   "student_list_attendance_present" : student_list_attendance_present,
                   "student_list_attendance_abesent" : student_list_attendance_abesent})

@login_required
def staff_take_attendance(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    sessions = SessionYearModel.objects.all()
    return render(request, "staff_template/staff_take_attendance_template.html", {"subjects" : subjects, "sessions" : sessions})

@csrf_exempt
def get_students(request):
    subject_id = request.POST.get("subject")
    session_id = request.POST.get("session")

    subject_model = Subjects.objects.get(id=subject_id)
    session_model = SessionYearModel.objects.get(id=session_id)

    students = Students.objects.filter(course_id=subject_model.course_id, session_id=session_model.id)
    print(students)
    # return students resulted into 500 Internal Server Error
    # Below line of code will handle this issue
    # return HttpResponse(students)
    # student_data = serializers.serialize("python", students)

    list_data = []

    for student in students:
        data_small = {"id" : student.admin.id, "name" : student.admin.first_name+" "+student.admin.last_name}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)

@csrf_exempt
def save_attendance_data(request):
    if request.method != "POST":
        return HttpResponse("Invalid method called from client due to dynamic HTML content")
    else:
        # Below line was extracting list however later JSON was stringify & forwards from POST to this method
        # student_ids = request.POST.getlist("student_ids[]")
        student_ids = request.POST.get("student_ids")
        attendance_date = request.POST.get("attendance_date")
        subject_id = request.POST.get("subject_id")
        session_id = request.POST.get("session_id")
        print(student_ids, attendance_date, subject_id, session_id)

        subject_model = Subjects.objects.get(id=subject_id)
        session_model = SessionYearModel.objects.get(id=session_id)
        json_student_data = json.loads(student_ids)

        print(json_student_data, attendance_date, subject_id, session_id)
        print(type(json_student_data), attendance_date, subject_id, session_id)

        #####
        ## Saving data into Attendance table
        ## 1. As Attendance has subject_id with Foreign key with model of Subject so need to pass subject_model in subject_id
        ## 2. As Attendance has session_id with Foreign key with model of SessionYearModel so need to pass session_model in
        #     session_id
        #####

        attendance = Attendance(subject_id=subject_model, session_id=session_model, attendance_date=attendance_date)
        attendance.save()

        #####
        ## Saving data into AttendanceReport table
        ## 1. As AttendanceReport has student_id with Foreign key with model of Students so need to pass student_model
        #     in studnet_id
        ## 2. As AttendanceReport has attendance_id with Foreign key with model of Attendance so need to pass
        #     attendance_model in attendance_id
        #####

        try:
            for stud in json_student_data:
                print(f'DEBUGGING - Saving {stud} into AttendanceReport at student level however there is only one record')
                student = Students.objects.get(admin=stud['id'])
                attendance_report = AttendanceReport(student_id=student, attendance_id=attendance, status=stud['status'])
                attendance_report.save()
            return HttpResponse("OK")
        except:
            return HttpResponse("ERR")

@login_required
def staff_update_attendance(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    sessions  = SessionYearModel.objects.all()
    return render(request, "staff_template/staff_update_attendance_template.html", {"subjects" : subjects, "sessions" : sessions})

@csrf_exempt
def get_attendance_dates(request):
    subject_id = request.POST.get("subject")
    subject_model = Subjects.objects.get(id=subject_id)
    session_id = request.POST.get("session")
    session_model = SessionYearModel.objects.get(id=session_id)
    attendance_model = Attendance.objects.filter(subject_id=subject_model, session_id=session_model)

    attendance_obj = []
    for attendance_single in attendance_model:
        # Without casting attendance_single.attendance_date, there was issue with JSON serializer
        data = {"id" : attendance_single.id,
                "attendance_date" : str(attendance_single.attendance_date),
                "session_id" : attendance_single.session_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj), safe=False)

@csrf_exempt
def get_attendance_for_student(request):
    attendance_date = request.POST.get("attendance_date")
    attendance_model = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance_model)

    list_data = []
    for student in attendance_data:
        data_small = {"id" : student.student_id.admin.id,
                      "name" : student.student_id.admin.first_name+" "+student.student_id.admin.last_name,
                      "status" : student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)

@csrf_exempt
def save_attendance_data_for_student(request):
    if request.method != "POST":
        return HttpResponse("Invalid method called from client due to dynamic HTML content")
    else:
        # Below line was extracting list however later JSON was stringify & forwards from POST to this method
        # student_ids = request.POST.getlist("student_ids[]")
        student_ids = request.POST.get("student_ids")
        attendance_date = request.POST.get("attendance_date")
        attendance = Attendance.objects.get(id=attendance_date)
        print(student_ids, attendance_date)

        json_student_data = json.loads(student_ids)

        try:
            for stud in json_student_data:
                print(f'DEBUGGING - Saving {stud} into AttendanceReport at student level however there is only one record')
                student = Students.objects.get(admin=stud['id'])
                attendance_report = AttendanceReport.objects.get(student_id=student, attendance_id=attendance)
                attendance_report.status = stud['status']
                attendance_report.save()
            return HttpResponse("OK")
        except:
            return HttpResponse("ERR")

@login_required
def staff_apply_leave(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    leave_data = LeaveReportStaff.objects.filter(staff_id=staff_obj)
    return render(request, "staff_template/staff_apply_leave_template.html", {"leave_data": leave_data})

@login_required
def staff_apply_leave_save(request):
    if request.method != "POST":
        return HttpResponseRedirect("/staff_apply_leave")
    else:
        leave_date = request.POST.get("leave_date")
        leave_message = request.POST.get("leave_message")

        # As LeaveReport has staff as foreign key so staff model to be passed
        staff_model = Staffs.objects.get(admin=request.user.id)

    try:
        leave_report = LeaveReportStaff(staff_id=staff_model,
                                        leave_date=leave_date,
                                        leave_message=leave_message,
                                        leave_status=0)
        leave_report.save()
        messages.success(request, f"Successfully applied for leave by staff")
        return HttpResponseRedirect("/staff_apply_leave")
    except Exception as e:
        messages.error(request, f"Failed to apply for leave by staff with reason {e}")
        return HttpResponseRedirect("/staff_apply_leave")

@login_required
def staff_feedback(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    feedback_data = FeedbackStaffs.objects.filter(staff_id=staff_obj)
    return render(request, "staff_template/staff_feedback_template.html", {"feedback_data": feedback_data})

@login_required
def staff_feedback_save(request):
    if request.method != "POST":
        return HttpResponseRedirect("/staff_feedback")
    else:
        feedback_message = request.POST.get("feedback_message")

        # As LeaveReport has staff as foreign key so staff model to be passed
        staff_model = Staffs.objects.get(admin=request.user.id)

    try:
        feedback = FeedbackStaffs(staff_id=staff_model,
                                  feedback_message=feedback_message,
                                  feedback_reply="Reply awaited from admin")
        feedback.save()
        messages.success(request, f"Successfully provided feedback by staff")
        return HttpResponseRedirect("/staff_feedback")
    except Exception as e:
        messages.error(request, f"Failed to provide feedback by staff with reason {e}")
        return HttpResponseRedirect("/staff_feedback")