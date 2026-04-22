from django.contrib.auth.models import User
from django.db import models

DEPARTMENTS = [
    ('ICT', 'ICT'),
    ('Finance', 'Finance'),
    ('Reception', 'Reception'),
    ('Accounts', 'Accounts'),
    ('Procurement', 'Procurement'),
    ('HR', 'Human Resource'),
    ('Registry', 'Registry'),
    ('Technical', 'Technical'),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=50, choices=DEPARTMENTS, default='ICT')
    
    def __str__(self):
        return f"{self.user.username} ({self.department})"

class Ticket(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Resolved', 'Resolved')]
    PRIORITY_CHOICES = [('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')]

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.title
    
class Announcement(models.Model):
    CATEGORY_CHOICES = [
        ('General', 'General'),
        ('System Maintenance', 'System Maintenance'),
        ('Network Alert', 'Network Alert'),
        ('Security Update', 'Security Update'),
        ('Software Update', 'Software Update'),
        ('Holiday Notice', 'Holiday Notice'),
    ]

    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='General')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def full_announcement(self):
        return f"{self.category}: {self.message}"

    def __str__(self):
        return self.full_announcement[:50]