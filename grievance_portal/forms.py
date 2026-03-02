from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Complaint


class CitizenRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name'
    }))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone Number (Optional)'
    }))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 2,
        'placeholder': 'Your Address (Optional)'
    }))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'address', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['username', 'password1', 'password2']:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone', '')
        user.address = self.cleaned_data.get('address', '')
        user.role = 'citizen'
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })


class ComplaintForm(forms.ModelForm):
    latitude = forms.DecimalField(
        max_digits=10, decimal_places=7, required=False,
        widget=forms.HiddenInput(attrs={'id': 'latitude'})
    )
    longitude = forms.DecimalField(
        max_digits=10, decimal_places=7, required=False,
        widget=forms.HiddenInput(attrs={'id': 'longitude'})
    )

    class Meta:
        model = Complaint
        fields = ['title', 'description', 'image', 'location_address', 'latitude', 'longitude']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief title of your complaint',
                'id': 'id_title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your complaint in detail...',
                'id': 'id_description'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'location_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter location address',
                'id': 'location_address'
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large. Maximum 5MB allowed.")
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if hasattr(image, 'content_type') and image.content_type not in allowed_types:
                raise forms.ValidationError("Invalid image type. Allowed: JPEG, PNG, GIF, WebP")
        return image


class ComplaintStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['status', 'assigned_department', 'admin_remarks']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_department': forms.Select(attrs={'class': 'form-select'}),
            'admin_remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add admin remarks...'
            }),
        }
