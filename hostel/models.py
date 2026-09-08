from django.db import models
from django.contrib.auth.models import User

# User Profile & Role-Based Access
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('warden', 'Hostel Warden / Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    roll_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=10, choices=(('Male', 'Male'), ('Female', 'Female')), default='Male')
    department = models.CharField(max_length=50, blank=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# Module 1: Room Allotment & Vacancy Tracking Models
class HostelBlock(models.Model):
    BLOCK_TYPES = (
        ('Boys', 'Boys Hostel'),
        ('Girls', 'Girls Hostel'),
    )
    name = models.CharField(max_length=50) # e.g. Block A (Ramanujan Hall)
    block_type = models.CharField(max_length=10, choices=BLOCK_TYPES)
    total_floors = models.PositiveIntegerField(default=3)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.block_type})"


class Room(models.Model):
    ROOM_TYPES = (
        ('Single-AC', 'Single Bed AC'),
        ('Double-NonAC', 'Double Sharing Non-AC'),
        ('Triple-NonAC', 'Triple Sharing Non-AC'),
        ('Double-AC', 'Double Sharing AC'),
    )
    block = models.ForeignKey(HostelBlock, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)
    floor = models.PositiveIntegerField(default=1)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='Double-NonAC')
    capacity = models.PositiveIntegerField(default=2) # Total bed capacity
    occupied_beds = models.PositiveIntegerField(default=0) # Currently allocated beds
    rent_per_semester = models.DecimalField(max_digits=10, decimal_places=2, default=25000.00)

    @property
    def available_beds(self):
        """Calculates vacant beds in real-time"""
        return max(0, self.capacity - self.occupied_beds)

    @property
    def is_full(self):
        """Checks if room reached full capacity"""
        return self.occupied_beds >= self.capacity

    def __str__(self):
        return f"{self.block.name} - Room {self.room_number}"


class RoomAllotment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending Review'),
        ('Approved', 'Approved / Allotted'),
        ('Rejected', 'Rejected'),
        ('Vacated', 'Vacated'),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='allotments')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='allotments')
    applied_date = models.DateTimeField(auto_now_add=True)
    allotment_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.room} ({self.status})"
