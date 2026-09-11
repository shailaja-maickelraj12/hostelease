import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum

from .models import UserProfile, HostelBlock, Room, RoomAllotment
from .forms import StudentRegistrationForm, RoomApplicationForm

# ==========================================
# AUTHENTICATION & ROLE-BASED ACCESS
# ==========================================

def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if hasattr(request.user, 'profile') and request.user.profile.role == 'student':
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access restricted to students.")
        return redirect('dashboard')
    return wrapper

def warden_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.role == 'warden'):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access restricted to Hostel Wardens and Administrators.")
        return redirect('dashboard')
    return wrapper


def home(request):
    blocks = HostelBlock.objects.all()
    total_rooms = Room.objects.count()
    total_capacity = Room.objects.aggregate(total=Sum('capacity'))['total'] or 0
    total_occupied = Room.objects.aggregate(total=Sum('occupied_beds'))['total'] or 0
    available_beds = max(0, total_capacity - total_occupied)

    return render(request, 'hostel/home.html', {
        'blocks': blocks,
        'total_rooms': total_rooms,
        'total_capacity': total_capacity,
        'available_beds': available_beds,
    })


def register_student(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created for {user.username}! You can now login.")
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'hostel/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'hostel/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def dashboard(request):
    if request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.role == 'warden'):
        return redirect('warden_dashboard')
    return redirect('student_dashboard')


@login_required
def student_dashboard(request):
    allotment = RoomAllotment.objects.filter(student=request.user, status='Approved').first()
    pending_app = RoomAllotment.objects.filter(student=request.user, status='Pending').first()

    return render(request, 'hostel/student_dashboard.html', {
        'allotment': allotment,
        'pending_app': pending_app,
    })


@warden_required
def warden_dashboard(request):
    total_rooms = Room.objects.count()
    total_capacity = Room.objects.aggregate(total=Sum('capacity'))['total'] or 0
    total_occupied = Room.objects.aggregate(total=Sum('occupied_beds'))['total'] or 0
    total_vacant = max(0, total_capacity - total_occupied)
    occupancy_rate = round((total_occupied / total_capacity * 100), 1) if total_capacity > 0 else 0

    pending_allotments = RoomAllotment.objects.filter(status='Pending').count()
    recent_allotments = RoomAllotment.objects.all().order_by('-applied_date')[:5]

    return render(request, 'hostel/warden_dashboard.html', {
        'total_rooms': total_rooms,
        'total_capacity': total_capacity,
        'total_occupied': total_occupied,
        'total_vacant': total_vacant,
        'occupancy_rate': occupancy_rate,
        'pending_allotments': pending_allotments,
        'recent_allotments': recent_allotments,
    })


# ==========================================
# MODULE 1: ROOM ALLOTMENT & VACANCY TRACKING
# ==========================================

@login_required
def room_list(request):
    blocks = HostelBlock.objects.all()
    selected_block = request.GET.get('block')
    selected_type = request.GET.get('type')

    rooms = Room.objects.all()
    if selected_block:
        rooms = rooms.filter(block_id=selected_block)
    if selected_type:
        rooms = rooms.filter(room_type=selected_type)

    return render(request, 'hostel/room_list.html', {
        'rooms': rooms,
        'blocks': blocks,
        'selected_block': selected_block,
        'selected_type': selected_type,
    })


@student_required
def apply_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    # Check if student already has an active allotment
    existing_allotment = RoomAllotment.objects.filter(student=request.user, status='Approved').first()
    if existing_allotment:
        messages.warning(request, f"You already have an active room: Room {existing_allotment.room.room_number}.")
        return redirect('my_room')

    # Check if student has a pending application
    pending_allotment = RoomAllotment.objects.filter(student=request.user, status='Pending').first()
    if pending_allotment:
        messages.warning(request, "You already have a pending application awaiting warden review.")
        return redirect('student_dashboard')

    if room.is_full:
        messages.error(request, "Sorry! This room has reached maximum capacity.")
        return redirect('room_list')

    if request.method == 'POST':
        RoomAllotment.objects.create(
            student=request.user,
            room=room,
            status='Pending'
        )
        messages.success(request, f"Application submitted for Room {room.room_number} ({room.block.name}). Awaiting warden approval.")
        return redirect('student_dashboard')

    return render(request, 'hostel/apply_room.html', {'room': room})


@student_required
def my_room(request):
    allotment = RoomAllotment.objects.filter(student=request.user, status='Approved').first()
    roommates = []
    if allotment:
        roommates = RoomAllotment.objects.filter(room=allotment.room, status='Approved').exclude(student=request.user)

    return render(request, 'hostel/my_room.html', {
        'allotment': allotment,
        'roommates': roommates,
    })


@warden_required
def manage_allotments(request):
    allotments = RoomAllotment.objects.all().order_by('-applied_date')
    return render(request, 'hostel/manage_allotments.html', {'allotments': allotments})


@warden_required
def update_allotment_status(request, allotment_id, new_status):
    allotment = get_object_or_404(RoomAllotment, id=allotment_id)
    room = allotment.room

    if new_status == 'Approved':
        if room.is_full:
            messages.error(request, f"Cannot approve! Room {room.room_number} is already full.")
            return redirect('manage_allotments')
        
        allotment.status = 'Approved'
        allotment.allotment_date = timezone.now()
        allotment.save()

        # Update room occupied beds count
        room.occupied_beds += 1
        room.save()

        messages.success(request, f"Room {room.room_number} allotted to {allotment.student.username}.")

    elif new_status == 'Rejected':
        allotment.status = 'Rejected'
        allotment.save()
        messages.info(request, f"Application rejected for {allotment.student.username}.")

    elif new_status == 'Vacated':
        allotment.status = 'Vacated'
        allotment.save()
        if room.occupied_beds > 0:
            room.occupied_beds -= 1
            room.save()
        messages.info(request, f"Room vacated for {allotment.student.username}. Vacancy updated.")

    return redirect('manage_allotments')


@warden_required
def export_allotments_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="room_allotment_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Roll Number', 'Student Name', 'Email', 'Block', 'Room Number', 'Room Type', 'Allotment Date', 'Status'])

    allotments = RoomAllotment.objects.all().select_related('student', 'student__profile', 'room', 'room__block')
    for a in allotments:
        roll = a.student.profile.roll_number if hasattr(a.student, 'profile') else 'N/A'
        writer.writerow([
            roll,
            a.student.get_full_name() or a.student.username,
            a.student.email,
            a.room.block.name,
            a.room.room_number,
            a.room.get_room_type_display(),
            a.allotment_date.strftime('%Y-%m-%d') if a.allotment_date else 'N/A',
            a.status
        ])
    return response


from .models import Complaint
from .forms import ComplaintForm, ComplaintStatusUpdateForm, ComplaintFeedbackForm
@student_required
def complaint_list(request):
    complaints = Complaint.objects.filter(student=request.user).order_by('-created_at')
    return render(request, 'hostel/complaint_list.html', {'complaints': complaints})
@student_required
def submit_complaint(request):
    allotment = RoomAllotment.objects.filter(student=request.user, status='Approved').first()
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.student = request.user
            if allotment:
                complaint.room = allotment.room
            complaint.save()
            messages.success(request, "Maintenance ticket filed successfully!")
            return redirect('complaint_list')
    else:
        form = ComplaintForm()
    return render(request, 'hostel/submit_complaint.html', {'form': form, 'allotment': allotment})
@student_required
def complaint_feedback(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id, student=request.user, status='Resolved')
    if request.method == 'POST':
        form = ComplaintFeedbackForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for your rating!")
            return redirect('complaint_list')
    else:
        form = ComplaintFeedbackForm(instance=complaint)
    return render(request, 'hostel/complaint_feedback.html', {'complaint': complaint, 'form': form})
@warden_required
def manage_complaints(request):
    complaints = Complaint.objects.all().order_by('-created_at')
    return render(request, 'hostel/manage_complaints.html', {'complaints': complaints})
@warden_required
def update_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == 'POST':
        form = ComplaintStatusUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            updated = form.save(commit=False)
            if updated.status == 'Resolved' and not updated.resolved_at:
                updated.resolved_at = timezone.now()
            updated.save()
            messages.success(request, "Ticket updated!")
            return redirect('manage_complaints')
    else:
        form = ComplaintStatusUpdateForm(instance=complaint)
    return render(request, 'hostel/update_complaint.html', {'complaint': complaint, 'form': form})
@warden_required
def analytics_dashboard(request):
    blocks = HostelBlock.objects.all()
    block_labels = [b.name for b in blocks]
    block_occupied = [b.rooms.aggregate(total=Sum('occupied_beds'))['total'] or 0 for b in blocks]
    block_capacity = [b.rooms.aggregate(total=Sum('capacity'))['total'] or 0 for b in blocks]
    categories = Complaint.objects.values('category').annotate(count=Count('id'))
    category_labels = [c['category'] for c in categories]
    category_counts = [c['count'] for c in categories]
    return render(request, 'hostel/analytics.html', {
        'block_labels': block_labels,
        'block_occupied': block_occupied,
        'block_capacity': block_capacity,
        'category_labels': category_labels,
        'category_counts': category_counts,
    })
@warden_required
def export_complaints_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="complaints.csv"'
    writer = csv.writer(response)
    writer.writerow(['Ticket ID', 'Student', 'Category', 'Title', 'Status', 'Date'])
    for c in Complaint.objects.all():
        writer.writerow([c.id, c.student.username, c.category, c.title, c.status, c.created_at.strftime('%Y-%m-%d')])
    return response