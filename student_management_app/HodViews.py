from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import json

from student_management_app.models import CustomUser, Courses, Staffs, Subjects, Students, SessionYearModel, \
    FeedbackStudents, FeedbackStaffs, LeaveReportStudent, LeaveReportStaff, Attendance, AttendanceReport

@login_required
def admin_home(request):
    student_count = Students.objects.all().count()
    staff_count   = Staffs.objects.all().count()
    course_count  = Courses.objects.all().count()
    subject_count = Subjects.objects.all().count()

    course_list = []
    subject_count_list = []
    student_count_list_in_course = []
    course_all = Courses.objects.all()

    for course in course_all:
        subject_count_in_course = Subjects.objects.filter(course_id=course.id).count()
        student_count_list_in_each_course = Students.objects.filter(course_id=course.id).count()
        course_list.append(course.course_name)
        subject_count_list.append(subject_count_in_course)
        student_count_list_in_course.append(student_count_list_in_each_course)

    subject_list = []
    student_count_list_in_subject = []
    subject_all = Subjects.objects.all()

    for subject in subject_all:
        course = Courses.objects.get(id=subject.course_id.id)
        student_count_in_each_subject = Students.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count_in_each_subject)

    return render(request, "hod_template/admin_home_template.html",
                  {"student_count" : student_count,
                   "course_count" : course_count,
                   "subject_count" : subject_count,
                   "staff_count" : staff_count,
                   "course_list" : course_list,
                   "subject_count_list" : subject_count_list,
                   "student_count_list_in_course" : student_count_list_in_course,
                   "subject_list": subject_list,
                   "student_count_list_in_subject": student_count_list_in_subject})

@login_required
def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")

@login_required
def add_staff_save(request):
    print(dir(request))
    if request.method != "POST":
        return HttpResponse("Invalid method called")
    else:
        email = request.POST.get("email")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        address = request.POST.get("address")
        try:
            user = CustomUser.objects.create_user(username=username,
                                              email=email,
                                              password=password,
                                              last_name=last_name,
                                              first_name=first_name,
                                              user_type=2)
            print(dir(user))
            print(dir(user.staffs))
            user.staffs.address = address
            user.save()
            messages.success(request, f"Successfully added staff with user name {username}")
            return HttpResponseRedirect("/add_staff")
        except Exception as e:
            messages.error(request, f"Failed to add staff with user name {username} with reason {e}")
            return HttpResponseRedirect("/add_staff")

@login_required
def add_course(request):
    return render(request, "hod_template/add_course_template.html")

@login_required
def add_course_save(request):
    print(dir(request))
    if request.method != "POST":
        return HttpResponse("Invalid method called")
    else:
        course = request.POST.get("course")
        try:
            course_model= Courses(course_name=course)
            course_model.save()
            messages.success(request, f"Successfully added course with name {course}")
            return HttpResponseRedirect("/add_course")
        except Exception as e:
            messages.error(request, f"Failed to add course with name {course} with reason {e}")
            return HttpResponseRedirect("/add_course")

@login_required
def add_student(request):
    courses  = Courses.objects.all()
    sessions = SessionYearModel.objects.all()
    return render(request, "hod_template/add_student_template.html", {"courses" : courses, "sessions" : sessions})

@login_required
def add_student_save(request):
    print(dir(request))
    if request.method != "POST":
        return HttpResponse("Invalid method called")
    else:
        email = request.POST.get("email")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        address = request.POST.get("address")
        course_id = request.POST.get("course")
        session_id = request.POST.get("session")
        print(course_id)
        print(session_id)
        sex = request.POST.get("sex")

        profile_pic = request.FILES['profile_pic']
        fs = FileSystemStorage()
        filename = fs.save(profile_pic.name, profile_pic)
        profile_pic_url = fs.url(filename)

        try:
            user = CustomUser.objects.create_user(username=username,
                                              email=email,
                                              password=password,
                                              last_name=last_name,
                                              first_name=first_name,
                                              user_type=3)
            user.students.address = address
            course_obj = Courses.objects.get(id=course_id)
            print(dir(course_obj))
            print(course_obj)
            print("Course object seems to be present")

            session_obj = SessionYearModel.objects.get(id=session_id)
            print(dir(session_obj))
            print(session_obj)
            print("Session object seems to be present")

            user.students.course_id = course_obj
            user.students.session_id = session_obj
            # user.students.session_start_year = session_start
            # user.students.session_end_year = session_end
            user.students.gender = sex
            user.students.profile_pic = profile_pic_url
            user.save()
            messages.success(request, f"Successfully added student with user name {username}")
            return HttpResponseRedirect("/add_student")
        except Exception as e:
            messages.error(request, f"Failed to add student with user name {username} with reason {e}")
            return HttpResponseRedirect("/add_student")

@login_required
def edit_student(request, student_id):
    courses  = Courses.objects.all()
    sessions = SessionYearModel.objects.all()
    student = Students.objects.get(admin=student_id)
    return render(request, "hod_template/edit_student_template.html", {"student" : student, "courses" : courses, "sessions" : sessions})

@login_required
def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid method called")
    else:
        student_id = request.POST.get("student_id")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        address = request.POST.get("address")
        # session_start = request.POST.get("session_start")
        # session_end = request.POST.get("session_end")
        course_id = request.POST.get("course")
        session_id = request.POST.get("session")
        sex = request.POST.get("sex")

        if request.FILES.get('profile_pic', False):
            profile_pic = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(profile_pic.name, profile_pic)
            profile_pic_url = fs.url(filename)
        else:
            profile_pic_url = None

        try:
            user = CustomUser.objects.get(id=student_id)
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.save()

            student_model = Students.objects.get(admin=student_id)
            student_model.address = address
            # student_model.session_start_year = session_start
            # student_model.session_end_year = session_end
            student_model.gender = sex

            if profile_pic_url != None:
                student_model.profile_pic = profile_pic_url

            course_model = Courses.objects.get(id=course_id)
            student_model.course_id = course_model

            session_model = SessionYearModel.objects.get(id=session_id)
            student_model.session_id = session_model
            student_model.save()

            messages.success(request, f"Successfully updated student with name {first_name} {last_name} with id {student_id}")
            return HttpResponseRedirect(f"/edit_student/{student_id}")
        except Exception as e:
            messages.error(request, f"Failed to update student with name {first_name} {last_name} with id {student_id} with reason {e}")
            return HttpResponseRedirect(f"/edit_student/{student_id}")

@login_required
def add_subject(request):
    courses = Courses.objects.all()
    staffs  = CustomUser.objects.filter(user_type=2)
    return render(request, "hod_template/add_subject_template.html", {"courses" : courses, "staffs" : staffs})

@login_required
def add_subject_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid method called")
    else:
        subject_name = request.POST.get("subject_name")
        course_id = request.POST.get("course")
        course=Courses.objects.get(id=course_id)
        staff_id = request.POST.get("staff")
        staff=CustomUser.objects.get(id=staff_id)
        try:
            subject_model= Subjects(subject_name=subject_name, course_id=course, staff_id=staff)
            subject_model.save()
            messages.success(request, f"Successfully added subject with name {subject_name}")
            return HttpResponseRedirect("/add_subject")
        except Exception as e:
            messages.error(request, f"Failed to add subject with name {subject_name} with reason {e}")
            return HttpResponseRedirect("/add_subject")

@login_required
def manage_staff(request):
    staffs = Staffs.objects.all()
    return render(request, "hod_template/manage_staff_template.html", {"staffs" : staffs})

@login_required
def manage_student(request):
    students = Students.objects.all()
    return render(request, "hod_template/manage_student_template.html", {"students" : students})

@login_required
def manage_course(request):
    courses = Courses.objects.all()
    return render(request, "hod_template/manage_course_template.html", {"courses" : courses})

@login_required
def manage_subject(request):
    subjects = Subjects.objects.all()
    return render(request, "hod_template/manage_subject_template.html", {"subjects" : subjects})

@login_required
def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    return render(request, "hod_template/edit_staff_template.html", {"staff" : staff})

@login_required
def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid method called")
    else:
        staff_id = request.POST.get("staff_id")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        address = request.POST.get("address")

        try:
            user = CustomUser.objects.get(id=staff_id)
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.save()

            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()
            messages.success(request, f"Successfully updated staff with name {first_name} {last_name} with id {staff_id}")
            return HttpResponseRedirect(f"/edit_staff/{staff_id}")
        except Exception as e:
            messages.error(request, f"Failed to updated staff with name {first_name} {last_name} with id {staff_id} with reason {e}")
            return HttpResponseRedirect(f"/edit_staff/{staff_id}")

@login_required
def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    staffs  = CustomUser.objects.filter(user_type=2)
    return render(request, "hod_template/edit_subject_template.html", {"subject" : subject, "courses" : courses, "staffs" : staffs})

@login_required
def edit_subject_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid method called")
    else:
        subject_id   = request.POST.get("subject_id")
        subject_name = request.POST.get("subject_name")
        staff_id = request.POST.get("staff")
        course_id = request.POST.get("course")

        try:
            subject_model = Subjects.objects.get(id=subject_id)
            subject_model.subject_name = subject_name
            staff = CustomUser.objects.get(id=staff_id)
            subject_model.staff_id = staff
            course = Courses.objects.get(id=course_id)
            subject_model.course_id = course
            subject_model.save()

            messages.success(request, f"Successfully updated subject with name {subject_name} with id {subject_id}")
            return HttpResponseRedirect(f"/edit_subject/{subject_id}")
        except Exception as e:
            messages.error(request, f"Failed to update subject with name {subject_name} with id {subject_id} with reason {e}")
            return HttpResponseRedirect(f"/edit_subject/{subject_id}")

@login_required
def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    return render(request, "hod_template/edit_course_template.html", {"course" : course})

@login_required
def edit_course_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid method called")
    else:
        course_id   = request.POST.get("course_id")
        course_name = request.POST.get("course_name")

        try:
            course_model = Courses.objects.get(id=course_id)
            course_model.course_name = course_name
            course_model.save()

            messages.success(request, f"Successfully updated course with name {course_name} with id {course_id}")
            return HttpResponseRedirect(f"/edit_course/{course_id}")
        except Exception as e:
            messages.error(request, f"Failed to update course with name {course_name} with id {course_id} with reason {e}")
            return HttpResponseRedirect(f"/edit_course/{course_id}")

@login_required
def manage_session(request):
    return render(request, "hod_template/manage_session_template.html")

@login_required
def add_session_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid method called")
    else:
        session_start_year = request.POST.get("session_start_year")
        session_end_year = request.POST.get("session_end_year")
        try:
            session_model_year = SessionYearModel(session_start_year=session_start_year, session_end_year=session_end_year)
            session_model_year.save()
            messages.success(request, f"Successfully added session with year start {session_start_year} and ending with {session_end_year}")
            return HttpResponseRedirect(f"/manage_session")
        except Exception as e:
            messages.error(request, f"Failed to add session with year start {session_start_year} and ending with {session_end_year} with reason {e}")
            return HttpResponseRedirect(f"/manage_session")

@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj_exist = CustomUser.objects.filter(email=email).exists()

    if user_obj_exist:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj_exist = CustomUser.objects.filter(username=username).exists()

    if user_obj_exist:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

@login_required
def student_feedback_message(request):
    feedback_data = FeedbackStudents.objects.all()
    return render(request, "hod_template/manage_student_feedback_template.html", {"feedback_data" : feedback_data})

@csrf_exempt
def student_feedback_message_replier(request):
    feedback_id = request.POST.get("feedback_id")
    feedback_reply_message = request.POST.get("feedback_reply_message")

    try:
        feedback_replier_model = FeedbackStudents.objects.get(id=feedback_id)
        feedback_replier_model.feedback_reply = feedback_reply_message
        feedback_replier_model.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

@login_required
def staff_feedback_message(request):
    feedback_data = FeedbackStaffs.objects.all()
    return render(request, "hod_template/manage_staff_feedback_template.html", {"feedback_data" : feedback_data})

@csrf_exempt
def staff_feedback_message_replier(request):
    feedback_id = request.POST.get("feedback_id")
    feedback_reply_message = request.POST.get("feedback_reply_message")

    try:
        feedback_replier_model = FeedbackStaffs.objects.get(id=feedback_id)
        feedback_replier_model.feedback_reply = feedback_reply_message
        feedback_replier_model.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

@login_required
def student_leave_view(request):
    leave_data = LeaveReportStudent.objects.all()
    return render(request, "hod_template/student_leave_view_template.html", {"leave_data" : leave_data})

@login_required
def student_approve_leave(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return HttpResponseRedirect("/student_leave_view")

@login_required
def student_reject_leave(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return HttpResponseRedirect("/student_leave_view")

@login_required
def staff_leave_view(request):
    leave_data = LeaveReportStaff.objects.all()
    return render(request, "hod_template/staff_leave_view_template.html", {"leave_data": leave_data})

@login_required
def staff_approve_leave(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return HttpResponseRedirect("/staff_leave_view")

@login_required
def staff_reject_leave(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return HttpResponseRedirect("/staff_leave_view")

@login_required
def admin_view_attendance(request):
    subjects = Subjects.objects.all()
    sessions  = SessionYearModel.objects.all()
    return render(request, "hod_template/admin_attendance_view_template.html", {"subjects" : subjects, "sessions" : sessions})

@csrf_exempt
def admin_get_attendance_dates(request):
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
def admin_get_attendance_for_student(request):
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
