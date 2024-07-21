from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sort/', views.sort, name='sort'),
    path('process/', views.process_file, name='process_file'),
    path('download/<str:file_path>/', views.download_file, name='download_file'),
    path('separation/', views.separation, name='separation_page'),
    path('split/', views.split_file, name='split_file'),
    path('merge/', views.merge, name='merge_page'),
    path('merged/', views.merge_files, name='merge_files'),
    path('normalization/', views.normalization, name='normalization_page'),
    path('normalize/', views.normalize_file, name='normalize_file'),
    path('reformat/', views.reformat, name='reformat_page'),
    path('reformated/', views.reformat_file, name='reformat_file'),
    path('empty/', views.empty, name='empty_page'),
    path('emptycheck/', views.check_empty_entries, name='check_empty_entries'),
    path('duplicate/', views.find_duplicate, name='find_duplicate_page'),
    path('find_duplicates/', views.find_duplicates, name='find_duplicates'),
]