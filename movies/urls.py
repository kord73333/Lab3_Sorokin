from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_movie, name='add_movie'),
    path('upload/', views.upload_file, name='upload_file'),
    path('files/', views.list_files, name='list_files'),
    path('data/', views.data_view, name='data_view'),
    path('movies/<int:pk>/edit/', views.movie_edit, name='movie_edit'),
    path('movies/<int:pk>/delete/', views.movie_delete, name='movie_delete'),
    path('movies/search/', views.movie_search, name='movie_search'),
]
