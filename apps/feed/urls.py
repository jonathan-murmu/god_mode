from django.urls import path

from apps.feed import views

urlpatterns = [
    path('timeline/', views.TimeLine.as_view(), name='timeline')
]