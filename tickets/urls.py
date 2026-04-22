from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_ticket, name='create_ticket'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/<int:pk>/delete/', views.delete_ticket, name='delete_ticket'),
    path('ticket/<int:pk>/update/', views.update_ticket, name='update_ticket'),
    path('export-pdf/', views.export_tickets_pdf, name='export_tickets_pdf'),
    
    # Staff Portal Specific Logout
    path('logout/', views.staff_logout, name='staff_logout'),
]