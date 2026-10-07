from django.urls import path

from . import views


urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),
    path('analytics/', views.analytics, name='analytics'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/report/', views.export_report, name='export_report'),
    path('tickets/new/', views.ticket_create, name='ticket_create'),
    path('tickets/<int:pk>/edit/', views.ticket_update, name='ticket_update'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),
]
