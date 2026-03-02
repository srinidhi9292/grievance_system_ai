from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


class User(AbstractUser):
    ROLE_CHOICES = [
        ('citizen', 'Citizen'),
        ('admin', 'Admin/Authority'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='grievance_users',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='grievance_users',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    class Meta:
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.username} ({self.role})"

    def is_admin_user(self):
        return self.role == 'admin' or self.is_staff


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
    ]

    CATEGORY_CHOICES = [
        ('road', 'Road & Infrastructure'),
        ('water', 'Water Supply'),
        ('drainage', 'Drainage & Sewage'),
        ('electricity', 'Electricity'),
        ('garbage', 'Garbage & Sanitation'),
        ('parks', 'Parks & Recreation'),
        ('noise', 'Noise Pollution'),
        ('building', 'Building & Construction'),
        ('traffic', 'Traffic & Transport'),
        ('other', 'Other'),
    ]

    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    DEPARTMENT_CHOICES = [
        ('roads', 'Roads Department'),
        ('water', 'Water Department'),
        ('drainage', 'Drainage Department'),
        ('electricity', 'Electricity Department'),
        ('sanitation', 'Sanitation Department'),
        ('general', 'General Administration'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='complaint_images/', blank=True, null=True)

    # Location
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    location_address = models.TextField(blank=True)

    # AI-Generated Fields
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    priority_score = models.IntegerField(default=0)  # 0-100
    priority_level = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='low')
    sentiment_score = models.FloatField(default=0.0)  # -1 to 1
    sentiment_label = models.CharField(max_length=20, default='neutral')
    estimated_resolution_days = models.IntegerField(default=7)

    # Workflow
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='submitted')
    assigned_department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='general', blank=True)
    admin_remarks = models.TextField(blank=True)
    is_duplicate = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    expected_resolution_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['priority_level']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_duplicate']),
        ]

    def __str__(self):
        return f"{self.title} - {self.status}"

    def get_status_percentage(self):
        status_map = {
            'submitted': 10,
            'under_review': 30,
            'in_progress': 60,
            'resolved': 100,
            'closed': 100,
            'rejected': 0,
        }
        return status_map.get(self.status, 0)

    def get_priority_color(self):
        color_map = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'dark',
        }
        return color_map.get(self.priority_level, 'secondary')

    def get_status_color(self):
        color_map = {
            'submitted': 'info',
            'under_review': 'warning',
            'in_progress': 'primary',
            'resolved': 'success',
            'closed': 'secondary',
            'rejected': 'danger',
        }
        return color_map.get(self.status, 'secondary')

    def mark_resolved(self):
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()


class DuplicateMapping(models.Model):
    complaint = models.OneToOneField(
        Complaint, on_delete=models.CASCADE, related_name='duplicate_of'
    )
    master_complaint = models.ForeignKey(
        Complaint, on_delete=models.CASCADE, related_name='duplicates'
    )
    similarity_score = models.FloatField(default=0.0)
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['master_complaint']),
        ]

    def __str__(self):
        return f"Duplicate: {self.complaint.title} -> Master: {self.master_complaint.title}"


class ComplaintTimeline(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='timeline')
    status = models.CharField(max_length=30)
    message = models.TextField()
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.complaint.title} - {self.status} at {self.timestamp}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
