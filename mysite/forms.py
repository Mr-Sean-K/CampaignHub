from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Client, Campaign, Task

# forms for creating and editing staff users (managers, creatives)
class StaffCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')

class StaffUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')

# form for creating and editing partner clients/companies
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('name', 'email', 'phone_number', 'company_name')

# forms for CRUD operations on campaigns and tasks

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ('client', 'campaign_name', 'status', 'start_date', 'end_date')
        
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('campaign', 'title', 'description', 'assigned_to', 'deadline', 'status', 'priority')

    # ensure only creatives can be assigned to tasks
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(role='creative')

