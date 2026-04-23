from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        CLIENT = 'client', 'Client'
        GUEST = 'guest', 'Guest'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.GUEST)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=10, blank=True) # optional field for contact number
    company_name = models.CharField(max_length=100, blank=True) # optional field for company name

    def __str__(self):
        return self.name
    
class Campaign(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active'
        INACTIVE = 'inactive'
        COMPLETED = 'completed'

    client = models.ForeignKey(Client, on_delete=models.CASCADE) # each campaign is linked to a client

    campaign_name = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    start_date = models.DateField()
    end_date = models.DateField()
    def __str__(self):
        return self.campaign_name
        
class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'To Do'
        IN_PROGRESS = 'In Progress'
        REVIEW = 'Review'
        COMPLETED = 'Completed'
    
    class Priority(models.TextChoices):
        LOW = 'Low'
        MEDIUM = 'Medium'
        HIGH = 'High'

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE) # each task belongs to a campaign

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True) # description of task optional

    # task assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, # if task the user assigned to is deleted, the task will not be deleted
        blank=True, null=True) # null/blank true so task can exist without being assigned to anyone
    
    deadline = models.DateField(null=True, blank=True) # optional deadline for task
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.LOW)

    def __str__(self):
        return self.title