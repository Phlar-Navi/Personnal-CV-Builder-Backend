from django.contrib import admin
from .models import User, Socials, SessionLog
# Register your models here.

admin.site.register(User)
admin.site.register(Socials)
admin.site.register(SessionLog)