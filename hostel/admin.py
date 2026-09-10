from django.contrib import admin
from .models import UserProfile, HostelBlock, Room, RoomAllotment, Complaint

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'roll_number', 'phone_number', 'department')
    search_fields = ('user__username', 'roll_number', 'department')
    list_filter = ('role', 'gender')

@admin.register(HostelBlock)
class HostelBlockAdmin(admin.ModelAdmin):
    list_display = ('name', 'block_type', 'total_floors')
    list_filter = ('block_type',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'block', 'floor', 'room_type', 'capacity', 'occupied_beds', 'available_beds', 'rent_per_semester')
    list_filter = ('block', 'room_type', 'floor')
    search_fields = ('room_number',)

@admin.register(RoomAllotment)
class RoomAllotmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'room', 'status', 'applied_date', 'allotment_date')
    list_filter = ('status', 'room__block')
    search_fields = ('student__username', 'room__room_number')

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'student',
        'category',
        'title',
        'status',
        'assigned_to',
        'created_at',
        'rating'
    )

    list_filter = (
        'status',
        'category'
    )