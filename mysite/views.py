from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CampaignForm, ClientForm, StaffCreationForm, StaffUpdateForm
from .models import Campaign, Client, Task, User
from .permissions import role_required

@login_required
def dashboard(request):

    # dashboard content varies depending on user role
    user = request.user
    role_context = {"role": user.role}

    if user.is_superuser or user.role in [User.Role.ADMIN, User.Role.ACCOUNT_MANAGER]:
        # management roles dashboard displays all stats
        role_context["campaign_count"] = Campaign.objects.count()
        role_context["client_count"] = Client.objects.count()
        role_context["task_count"] = Task.objects.count()
        role_context["user_count"] = User.objects.count()