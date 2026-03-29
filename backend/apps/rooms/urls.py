# rooms/urls.py - Room management URL patterns
from django.urls import path
from . import views

app_name = 'rooms'

# urlpatterns = [
#     path('create/', views.create_room, name='create'),
#     path('get/', views.getTest, name='getTest'),
#     path('join/', views.join_room, name='join'),

  
#     path('<str:room_id>/leave/', views.leave_room, name='leave'),
#     path('<str:room_id>/delete/', views.delete_room, name='delete'),
#       path('<str:room_id>/', views.get_room, name='get'),
# ]


urlpatterns = [
    path('create/', views.create_room, name='create'),
    path('get/', views.getTest, name='getTest'),  # тестовый эндпоинт
    path('join/', views.join_room, name='join'),

    # динамические маршруты в самом низу
    path('<str:room_id>/leave/', views.leave_room, name='leave'),
    path('<str:room_id>/delete/', views.delete_room, name='delete'),
    path('<str:room_id>/', views.get_room, name='get'),
]