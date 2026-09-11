from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, RoomAllotment, Room

class StudentRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    
    roll_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Roll / Registration Number'}))
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    gender = forms.ChoiceField(choices=(('Male', 'Male'), ('Female', 'Female')), widget=forms.Select(attrs={'class': 'form-select'}))
    department = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department (e.g. CSE, IT, ECE)'}))
    guardian_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guardian Name'}))
    guardian_phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guardian Phone Number'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role='student',
                roll_number=self.cleaned_data['roll_number'],
                phone_number=self.cleaned_data['phone_number'],
                gender=self.cleaned_data['gender'],
                department=self.cleaned_data['department'],
                guardian_name=self.cleaned_data['guardian_name'],
                guardian_phone=self.cleaned_data['guardian_phone']
            )
        return user


class RoomApplicationForm(forms.ModelForm):
    room = forms.ModelChoiceField(
        queryset=Room.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select an available room"
    )

    class Meta:
        model = RoomAllotment
        fields = ['room']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.all()



from .models import Complaint
class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['category', 'title', 'description', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief title of problem'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Provide detailed explanation'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
class ComplaintStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['status', 'assigned_to', 'warden_remarks']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Worker/Technician Name'}),
            'warden_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Action taken / remarks'}),
        }
class ComplaintFeedbackForm(forms.ModelForm):
    RATING_CHOICES = [(i, f"{i} Stars") for i in range(1, 6)]
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    class Meta:
        model = Complaint
        fields = ['rating', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Was your complaint resolved satisfactorily?'}),
        }