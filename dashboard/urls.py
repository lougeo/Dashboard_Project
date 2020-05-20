from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('new-report/', views.new_report, name='new_report'),
    path('new-report-concrete/', views.new_report_concrete, name='new_report_concrete'),
    path('new-report-sieve/', views.new_report_sieve, name='new_report_sieve'),
    path('update-report/', views.update_report, name='update_report'),
    path('update-report-add/<int:pk>/', views.update_report_add, name='update_report_add'),
    path('report-approval/', views.report_approval, name='report_approval'),
    path('view-report/<int:pk>/', views.cr_view, name='cr_view'),
    path('update-full-report/<int:pk>/', views.cr_update, name='cr_update'),
    path('view-pdf/<int:pk>/', views.ViewPDF, name='ViewPDF'),
    path('download-pdf/<int:pk>/', views.DownloadPDF, name='DownloadPDF'),

    path('ajax/load-projects/', views.load_projects, name='ajax_load_projects'),

]
