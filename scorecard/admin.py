from django.contrib import admin
from .models import Players,Team,Match,Wicket
# Register your models here.
admin.site.register(Players)
admin.site.register(Team)
admin.site.register(Match)
admin.site.register(Wicket)
