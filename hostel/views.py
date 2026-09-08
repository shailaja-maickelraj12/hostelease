import csv
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q

from .models import (
    UserProfile, HostelBlock, Room, RoomAllotment,
    FeePayment, Complaint
)
from .forms import (
    StudentRegistrationForm, RoomApplicationForm,
    ComplaintForm, ComplaintStatusUpdateForm,
    ComplaintFeedbackForm, PaymentCheckoutForm
)


# Helper Decorators
def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if hasattr(request.user, 'profile') and request.user.profile.role == 'student':
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Student portal only.")
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
    payments = FeePayment.objects.filter(student=request.user).order_by('-due_date')
    pending_fee = FeePayment.objects.filter(student=request.user, status='Pending').aggregate(total=Sum('amount'))['total'] or 0
    recent_complaints = Complaint.objects.filter(student=request.user).order_by('-created_at')[:5]

    return render(request, 'hostel/student_dashboard.html', {
        'allotment': allotment,
        'pending_app': pending_app,
        'payments': payments,
        'pending_fee': pending_fee,
        'recent_complaints': recent_complaints,
    })


@warden_required
def warden_dashboard(request):
    total_rooms = Room.objects.count()
    total_capacity = Room.objects.aggregate(total=Sum('capacity'))['total'] or 0
    total_occupied = Room.objects.aggregate(total=Sum('occupied_beds'))['total'] or 0
    total_vacant = max(0, total_capacity - total_occupied)
    occupancy_rate = round((total_occupied / total_capacity * 100), 1) if total_capacity > 0 else 0

    pending_allotments = RoomAllotment.objects.filter(status='Pending').count()
    pending_complaints = Complaint.objects.filter(status='Pending').count()
    total_fee_collected = FeePayment.objects.filter(status='Paid').aggregate(total=Sum('amount'))['total'] or 0
    pending_fee_total = FeePayment.objects.filter(status='Pending').aggregate(total=Sum('amount'))['total'] or 0

    recent_complaints = Complaint.objects.all().order_by('-created_at')[:5]

    return render(request, 'hostel/warden_dashboard.html', {
        'total_rooms': total_rooms,
        'total_capacity': total_capacity,
        'total_occupied': total_occupied,
        'total_vacant': total_vacant,
        'occupancy_rate': occupancy_rate,
        'pending_allotments': pending_allotments,
        'pending_complaints': pending_complaints,
        'total_fee_collected': total_fee_collected,
        'pending_fee_total': pending_fee_total,
        'recent_complaints': recent_complaints,
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

    # Check if student already has an active allotment or pending application
    existing_allotment = RoomAllotment.objects.filter(student=request.user, status='Approved').first()
    if existing_allotment:
        messages.warning(request, f"You are already allotted Room {existing_allotment.room.room_number}.")
        return redirect('my_room')

    pending_allotment = RoomAllotment.objects.filter(student=request.user, status='Pending').first()
    if pending_allotment:
        messages.warning(request, "You already have a pending room application waiting for warden approval.")
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
        messages.success(request, f"Room application submitted for Room {room.room_number} ({room.block.name}). Awaiting warden approval.")
        return redirect('student_dashboard')

    return render(request, 'hostel/apply_room.html', {'room': room})


@student_required
def my_room(request):
    allotment = RoomAllotment.objects.filter(student=request.user, status='Approved').first()
    roommates = []
    if allotment:
        # Find other students allotted to the same room
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

        # Auto-generate initial semester fee for student
        FeePayment.objects.get_or_create(
            student=allotment.student,
            fee_type='Hostel Rent',
            defaults={
                'amount': room.rent_per_semester,
                'due_date': timezone.now().date() + timezone.timedelta(days=15),
                'status': 'Pending'
            }
        )
        messages.success(request, f"Allotment approved for {allotment.student.username} in Room {room.room_number}.")

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
        messages.info(request, f"Room vacated for {allotment.student.username}.")

    return redirect('manage_allotments')


# ==========================================
# MODULE 2: FEE PAYMENT INTEGRATION
# ==========================================

@student_required
def student_fees(request):
    payments = FeePayment.objects.filter(student=request.user).order_by('-due_date')
    pending_total = payments.filter(status='Pending').aggregate(total=Sum('amount'))['total'] or 0
    paid_total = payments.filter(status='Paid').aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'hostel/student_fees.html', {
        'payments': payments,
        'pending_total': pending_total,
        'paid_total': paid_total,
    })


@student_required
def pay_fee(request, payment_id):
    payment = get_object_or_404(FeePayment, id=payment_id, student=request.user)
    if payment.status == 'Paid':
        messages.info(request, "This fee has already been settled.")
        return redirect('fee_receipt', payment_id=payment.id)

    if request.method == 'POST':
        form = PaymentCheckoutForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data['payment_method']
            # Simulate Payment Gateway success
            payment.status = 'Paid'
            payment.payment_method = method
            payment.transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
            payment.paid_at = timezone.now()
            payment.save()

            messages.success(request, f"Payment of Rs.{payment.amount} successful! Transaction ID: {payment.transaction_id}")
            return redirect('fee_receipt', payment_id=payment.id)
    else:
        form = PaymentCheckoutForm()

    return render(request, 'hostel/pay_fee.html', {
        'payment': payment,
        'form': form,
    })


@login_required
def fee_receipt(request, payment_id):
    if request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.role == 'warden'):
        payment = get_object_or_404(FeePayment, id=payment_id)
    else:
        payment = get_object_or_404(FeePayment, id=payment_id, student=request.user)

    allotment = RoomAllotment.objects.filter(student=payment.student, status='Approved').first()
    return render(request, 'hostel/fee_receipt.html', {
        'payment': payment,
        'allotment': allotment,
    })


@warden_required
def warden_fee_tracker(request):
    status_filter = request.GET.get('status')
    payments = FeePayment.objects.all().order_by('-due_date')
    if status_filter:
        payments = payments.filter(status=status_filter)

    total_collected = FeePayment.objects.filter(status='Paid').aggregate(total=Sum('amount'))['total'] or 0
    total_pending = FeePayment.objects.filter(status='Pending').aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'hostel/warden_fees.html', {
        'payments': payments,
        'total_collected': total_collected,
        'total_pending': total_pending,
        'status_filter': status_filter,
    })


# ==========================================
# MODULE 3: COMPLAINTS & ANALYTICS
# ==========================================

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
            complaint.status = 'Pending'
            complaint.save()
            messages.success(request, "Maintenance ticket filed successfully! The warden team will review it.")
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
            messages.success(request, "Thank you for your rating and feedback!")
            return redirect('complaint_list')
    else:
        form = ComplaintFeedbackForm(instance=complaint)

    return render(request, 'hostel/complaint_feedback.html', {'complaint': complaint, 'form': form})


@warden_required
def manage_complaints(request):
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')

    complaints = Complaint.objects.all().order_by('-created_at')
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if category_filter:
        complaints = complaints.filter(category=category_filter)

    return render(request, 'hostel/manage_complaints.html', {
        'complaints': complaints,
        'status_filter': status_filter,
        'category_filter': category_filter,
    })


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
            messages.success(request, f"Complaint #{complaint.id} status updated to {updated.status}.")
            return redirect('manage_complaints')
    else:
        form = ComplaintStatusUpdateForm(instance=complaint)

    return render(request, 'hostel/update_complaint.html', {'complaint': complaint, 'form': form})


@warden_required
def analytics_dashboard(request):
    # 1. Occupancy by Block
    blocks = HostelBlock.objects.all()
    block_labels = []
    block_occupied = []
    block_capacity = []
    for b in blocks:
        block_labels.append(b.name)
        cap = b.rooms.aggregate(total=Sum('capacity'))['total'] or 0
        occ = b.rooms.aggregate(total=Sum('occupied_beds'))['total'] or 0
        block_capacity.append(cap)
        block_occupied.append(occ)

    # 2. Complaint Categories
    categories = Complaint.objects.values('category').annotate(count=Count('id'))
    category_labels = [c['category'] for c in categories]
    category_counts = [c['count'] for c in categories]

    # 3. Complaint Statuses
    statuses = Complaint.objects.values('status').annotate(count=Count('id'))
    status_labels = [s['status'] for s in statuses]
    status_counts = [s['count'] for s in statuses]

    # 4. Fee Overview
    paid_sum = FeePayment.objects.filter(status='Paid').aggregate(total=Sum('amount'))['total'] or 0
    pending_sum = FeePayment.objects.filter(status='Pending').aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'hostel/analytics.html', {
        'block_labels': block_labels,
        'block_occupied': block_occupied,
        'block_capacity': block_capacity,
        'category_labels': category_labels,
        'category_counts': category_counts,
        'status_labels': status_labels,
        'status_counts': status_counts,
        'paid_sum': float(paid_sum),
        'pending_sum': float(pending_sum),
    })


@warden_required
def export_students_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="allotted_students.csv"'

    writer = csv.writer(response)
    writer.writerow(['Roll Number', 'Student Name', 'Email', 'Block', 'Room Number', 'Allotment Date', 'Status'])

    allotments = RoomAllotment.objects.filter(status='Approved').select_related('student', 'student__profile', 'room', 'room__block')
    for a in allotments:
        roll = a.student.profile.roll_number if hasattr(a.student, 'profile') else 'N/A'
        writer.writerow([
            roll,
            a.student.get_full_name() or a.student.username,
            a.student.email,
            a.room.block.name,
            a.room.room_number,
            a.allotment_date.strftime('%Y-%m-%d') if a.allotment_date else 'N/A',
            a.status
        ])
    return response


@warden_required
def export_complaints_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="complaints_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Ticket ID', 'Student', 'Room', 'Category', 'Title', 'Status', 'Assigned To', 'Filed On', 'Resolved On', 'Rating'])

    complaints = Complaint.objects.all().select_related('student', 'room')
    for c in complaints:
        room_no = c.room.room_number if c.room else 'N/A'
        writer.writerow([
            f"#{c.id}",
            c.student.username,
            room_no,
            c.category,
            c.title,
            c.status,
            c.assigned_to or 'Unassigned',
            c.created_at.strftime('%Y-%m-%d'),
            c.resolved_at.strftime('%Y-%m-%d') if c.resolved_at else 'Pending',
            f"{c.rating} Stars" if c.rating else 'No rating'
        ])
    return response
