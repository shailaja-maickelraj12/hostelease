from django.urls import path
from . import views

urlpatterns = [
    # Auth & Portals
    path('', views.home, name='home'),
    path('register/', views.register_student, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('warden/dashboard/', views.warden_dashboard, name='warden_dashboard'),

    # Module 1: Room Allotment & Vacancy
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/apply/<int:room_id>/', views.apply_room, name='apply_room'),
    path('my-room/', views.my_room, name='my_room'),
    path('warden/allotments/', views.manage_allotments, name='manage_allotments'),
    path('warden/allotments/update/<int:allotment_id>/<str:new_status>/', views.update_allotment_status, name='update_allotment_status'),

    # Module 2: Fee Payment Integration
    path('fees/', views.student_fees, name='student_fees'),
    path('fees/pay/<int:payment_id>/', views.pay_fee, name='pay_fee'),
    path('fees/receipt/<int:payment_id>/', views.fee_receipt, name='fee_receipt'),
    path('warden/fees/', views.warden_fee_tracker, name='warden_fee_tracker'),

    # Module 3: Complaint Management & Analytics
    path('complaints/', views.complaint_list, name='complaint_list'),
    path('complaints/new/', views.submit_complaint, name='submit_complaint'),
    path('complaints/feedback/<int:complaint_id>/', views.complaint_feedback, name='complaint_feedback'),
    path('warden/complaints/', views.manage_complaints, name='manage_complaints'),
    path('warden/complaints/update/<int:complaint_id>/', views.update_complaint, name='update_complaint'),
    path('warden/analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('warden/export/students/', views.export_students_csv, name='export_students_csv'),
    path('warden/export/complaints/', views.export_complaints_csv, name='export_complaints_csv'),
]
