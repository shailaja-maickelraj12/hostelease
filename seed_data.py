import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hostelease_project.settings')
django.setup()

from django.contrib.auth.models import User
from hostel.models import UserProfile, HostelBlock, Room, RoomAllotment, FeePayment, Complaint

def seed():
    print("Seeding initial data for HostelEase...")

    # 1. Create Warden / Admin user
    if not User.objects.filter(username='warden').exists():
        warden_user = User.objects.create_superuser('warden', 'warden@campus.edu', 'admin123')
        warden_user.first_name = "Hostel"
        warden_user.last_name = "Warden"
        warden_user.save()
        UserProfile.objects.create(
            user=warden_user,
            role='warden',
            roll_number='WARDEN01',
            phone_number='9876543210',
            gender='Male',
            department='Administration'
        )
        print("Created Warden: username='warden', password='admin123'")

    # 2. Create Student user
    if not User.objects.filter(username='student1').exists():
        student_user = User.objects.create_user('student1', 'student1@campus.edu', 'student123')
        student_user.first_name = "Rahul"
        student_user.last_name = "Sharma"
        student_user.save()
        UserProfile.objects.create(
            user=student_user,
            role='student',
            roll_number='23CS101',
            phone_number='9898989898',
            gender='Male',
            department='Computer Science',
            guardian_name='Mr. Sharma',
            guardian_phone='9111122222'
        )
        print("Created Student: username='student1', password='student123'")

    # 3. Create Hostel Blocks
    block_a, _ = HostelBlock.objects.get_or_create(
        name="Block A (Ramanujan Hall)",
        defaults={'block_type': 'Boys', 'total_floors': 3, 'description': 'Main Campus Boys Hostel'}
    )
    block_b, _ = HostelBlock.objects.get_or_create(
        name="Block B (Kalpana Hall)",
        defaults={'block_type': 'Girls', 'total_floors': 3, 'description': 'Main Campus Girls Hostel'}
    )

    # 4. Create Sample Rooms
    r1, _ = Room.objects.get_or_create(
        block=block_a,
        room_number="101",
        defaults={'floor': 1, 'room_type': 'Double-NonAC', 'capacity': 2, 'occupied_beds': 0, 'rent_per_semester': 22000.00}
    )
    r2, _ = Room.objects.get_or_create(
        block=block_a,
        room_number="102",
        defaults={'floor': 1, 'room_type': 'Single-AC', 'capacity': 1, 'occupied_beds': 0, 'rent_per_semester': 35000.00}
    )
    r3, _ = Room.objects.get_or_create(
        block=block_a,
        room_number="201",
        defaults={'floor': 2, 'room_type': 'Triple-NonAC', 'capacity': 3, 'occupied_beds': 0, 'rent_per_semester': 18000.00}
    )
    r4, _ = Room.objects.get_or_create(
        block=block_b,
        room_number="101",
        defaults={'floor': 1, 'room_type': 'Double-AC', 'capacity': 2, 'occupied_beds': 0, 'rent_per_semester': 28000.00}
    )
    print("Created sample rooms across Block A and Block B.")

    # 5. Create Sample Fee for student1
    student_user = User.objects.get(username='student1')
    FeePayment.objects.get_or_create(
        student=student_user,
        fee_type='Hostel Rent',
        defaults={
            'amount': 22000.00,
            'due_date': timezone.now().date() + timezone.timedelta(days=15),
            'status': 'Pending'
        }
    )
    FeePayment.objects.get_or_create(
        student=student_user,
        fee_type='Mess Fee',
        defaults={
            'amount': 15000.00,
            'due_date': timezone.now().date() + timezone.timedelta(days=15),
            'status': 'Pending'
        }
    )
    print("Created sample pending fees for student1.")

    print("Data seeding completed successfully!")

if __name__ == '__main__':
    seed()
