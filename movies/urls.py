from django.urls import path
from . import views

urlpatterns = [
    # Ensure the name is EXACTLY 'movie_list'
    path('', views.index, name='movie_list'), 
    path('theaters/<int:movie_id>/', views.theater_list, name='theater'),
    path('book/<int:theater_id>/', views.book_seats, name='book_seats'),
]