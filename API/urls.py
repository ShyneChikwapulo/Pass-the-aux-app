from django.urls import path
from .views import RoomView

urlpatterns = [
    path('Room',RoomView.as_view()),

]