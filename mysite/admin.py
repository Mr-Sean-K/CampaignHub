from django.contrib import admin
from .models import User, Client, Campaign, Task

admin.site.register(User)
admin.site.register(Client)
admin.site.register(Campaign)
admin.site.register(Task)