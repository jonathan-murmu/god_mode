from django.contrib import admin
from apps.feed.models import Posts, Follow, Like, Tweet, Hashtag

admin.site.register(Posts)
admin.site.register(Like)
admin.site.register(Follow)
admin.site.register(Tweet)
admin.site.register(Hashtag)
