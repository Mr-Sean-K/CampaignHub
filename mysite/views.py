from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CampaignForm, ClientForm, StaffCreationForm, StaffUpdateForm, TaskForm
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
    elif user.role == User.Role.CREATIVE:
        # creative role dashboard displays assigned tasks
        tasks = Task.objects.filter(assigned_to=user).order_by("priority", "deadline")
        role_context["task_count"] = tasks.count()
        role_context["tasks"] = tasks
    else:
        # default role client sees campaigns/tasks tied to their profile
        client_profile = Client.objects.get(user=user)
        campaigns = Campaign.objects.filter(client=client_profile)
        tasks = Task.objects.filter(campaign__in=campaigns).order_by("priority", "deadline")
        role_context["campaign_count"] = campaigns.count()
        role_context["task_count"] = tasks.count()
        role_context["tasks"] = tasks

    return render(request, "dashboard.html", role_context)

# campaign crud methods -------------------------

@login_required
@role_required(User.Role.ADMIN, User.Role.ACCOUNT_MANAGER)
def campaign_list(request):
    campaigns = Campaign.objects.all()
    return render(request, "campaigns.html", {"campaigns": campaigns})

@login_required
@role_required(User.Role.ADMIN, User.Role.ACCOUNT_MANAGER)
def campaign_create(request):
    form = CampaignForm(request.POST or None)

    # valid forms save to db, invalid forms display errors

    if form.is_valid():
        form.save()
        return redirect("campaign_list")
    
    return render(request, "create.html", {"form": form, "title": "Create Campaign"})

@login_required
@role_required(User.Role.ADMIN, User.Role.ACCOUNT_MANAGER)
def campaign_edit(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk) # load object instance

    form = CampaignForm(request.POST or None, instance=campaign) # bind data from new form to existing object instance

    if form.is_valid():
        form.save()
        return redirect("campaign_list")
    
    return render(request, "create.html", {"form": form, "title": "Edit Campaign"})


@login_required
@role_required(User.Role.ADMIN, User.Role.ACCOUNT_MANAGER)
def campaign_delete(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)

    if request.method == "POST":
        campaign.delete()
        return redirect("campaign_list")
    
    return render(request, "delete.html", {"object": campaign, "title": "Delete Campaign"})

# task crud methods -------------------------

@login_required
def task_list(request):
    user = request.user

    # admins/account managers can view all tasks
    if user.is_superuser or user.role in [User.Role.ADMIN, User.Role.ACCOUNT_MANAGER]:
        tasks = Task.objects.select_related("campaign", "assigned_to").all().order_by("-id")
    # creatives can view only their assigned tasks
    elif user.role == User.Role.CREATIVE:
        tasks = Task.objects.select_related("campaign", "assigned_to").filter(assigned_to=user).order_by("-id")
    # clients can view only tasks tied to their campaigns
    else:
        client_profile = Client.objects.filter(user=user).first()
        tasks = Task.objects.select_related("campaign", "assigned_to").filter(campaign__client=client_profile).order_by("-id") if client_profile else Task.objects.none()

    return render(request, "tasks.html", {"tasks": tasks})


@login_required
@role_required(User.Role.ADMIN, User.Role.ACCOUNT_MANAGER)
def task_create(request):
    form = TaskForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("task_list")
    return render(request, "create.html", {"form": form, "title": "Create Task"})

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    user = request.user

    # admins/account managers can edit any task
    # creatives can edit only their own task
    if user.is_superuser or user.role in [User.Role.ADMIN, User.Role.ACCOUNT_MANAGER]:
        pass
    elif user.role == User.Role.CREATIVE and task.assigned_to == user:
        pass
    else:
        return redirect("dashboard")

    form = TaskForm(request.POST or None, instance=task)

    if user.role == User.Role.CREATIVE:
        # restrict creative edits to task status only.
        allowed_fields = {"status"}
        for name in list(form.fields.keys()):
            if name not in allowed_fields:
                form.fields[name].disabled = True

    if form.is_valid():
        form.save()
        return redirect("task_list")

    return render(request, "create.html", {"form": form, "title": "Edit Task"})

@login_required
@role_required(User.Role.ADMIN, User.Role.ACCOUNT_MANAGER) # only admins/account managers can delete tasks
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":
        task.delete()
        return redirect("task_list")
    
    return render(request, "delete.html", {"object": task, "title": "Delete Task"})


# client crud methods -------------------------

@login_required
@role_required(User.Role.ADMIN, User.Role.ACCOUNT_MANAGER)
def client_list(request):
    clients = Client.objects.select_related("user").all().order_by("-id")
    return render(request, "clients.html", {"clients": clients})


@login_required
@role_required(User.Role.ADMIN, User.Role.ACCOUNT_MANAGER)
def client_create(request):
    form = ClientForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("client_list")
    
    return render(request, "create.html", {"form": form, "title": "Create Client"})


@login_required
@role_required(User.Role.ADMIN, User.Role.ACCOUNT_MANAGER)
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)

    form = ClientForm(request.POST or None, instance=client)
    if form.is_valid():
        form.save()
        return redirect("client_list")
    
    return render(request, "create.html", {"form": form, "title": "Edit Client"})


@login_required
@role_required(User.Role.ADMIN, User.Role.ACCOUNT_MANAGER)
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if request.method == "POST":
        client.delete()
        return redirect("client_list")
    
    return render(request, "delete.html", {"object": client, "title": "Delete Client"})

# staff crud methods -------------------------

@login_required
@role_required(User.Role.ADMIN, User.Role.ACCOUNT_MANAGER)
def staff_list(request):
    staff = User.objects.exclude(role=User.Role.CLIENT).order_by("-id") # list all staff users excluding clients
    return render(request, "staff.html", {"staff": staff})

@login_required
@role_required(User.Role.ADMIN, User.Role.ACCOUNT_MANAGER)
def staff_create(request):
    form = StaffCreationForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("staff_list")
    
    return render(request, "create.html", {"form": form, "title": "Create Staff User"})

@login_required
@role_required(User.Role.ADMIN, User.Role.ACCOUNT_MANAGER)
def staff_edit(request, pk):
    staff = get_object_or_404(User, pk=pk)

    form = StaffUpdateForm(request.POST or None, instance=staff)
    if form.is_valid():
        form.save()
        return redirect("staff_list")
    
    return render(request, "create.html", {"form": form, "title": "Edit Staff User"})

@login_required
@role_required(User.Role.ADMIN, User.Role.ACCOUNT_MANAGER)
def staff_delete(request, pk):
    staff = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        staff.delete()
        return redirect("staff_list")
    
    return render(request, "delete.html", {"object": staff, "title": "Delete Staff User"})