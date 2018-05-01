from django.contrib import admin

# Register your models here.
from apps.feed.models import Item, Board, Pin, Follow

admin.site.register(Item)
admin.site.register(Board)
admin.site.register(Pin)
admin.site.register(Follow)