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

    # Member 1: Room Allotment & Vacancy Tracking
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/apply/<int:room_id>/', views.apply_room, name='apply_room'),
    path('my-room/', views.my_room, name='my_room'),
    path('warden/allotments/', views.manage_allotments, name='manage_allotments'),
    path('warden/allotments/update/<int:allotment_id>/<str:new_status>/', views.update_allotment_status, name='update_allotment_status'),
    path('warden/export/allotments/', views.export_allotments_csv, name='export_allotments_csv'),
    # Member 3: Complaints Management, Analytics & CSV Reports
    path('complaints/', views.complaint_list, name='complaint_list'),
    path('complaints/new/', views.submit_complaint, name='submit_complaint'),
    path('complaints/<int:complaint_id>/feedback/', views.complaint_feedback, name='complaint_feedback'),
    path('warden/complaints/', views.manage_complaints, name='manage_complaints'),
    path('warden/complaints/<int:complaint_id>/update/', views.update_complaint, name='update_complaint'),
    path('warden/analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('warden/complaints/export/', views.export_complaints_csv, name='export_complaints_csv'),
]

