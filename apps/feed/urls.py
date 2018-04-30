from django.urls import path
from apps.feed.views import TimeLine

urlpatterns = [
    path('timeline/', TimeLine.as_view(), name='feed-timeline')
]