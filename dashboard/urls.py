from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('new-report/', views.new_report, name='new_report'),
    path('new-report-concrete/<int:pk>/', views.new_report_concrete, name='new_report_concrete'),
    path('new-report-sieve/<int:pk>/', views.new_report_sieve, name='new_report_sieve'),
    path('new-standard/', views.new_standard, name='new_standard'),
    # path('new-standard-compression/<int:pk>/', views.new_standard_compression, name='new_standard_compression'),
    # path('new-standard-sieve/<int:pk>/', views.new_standard_sieve, name='new_standard_sieve'),
    path('lab-update-sample-list/', views.lab_update_sample_list, name='lab_update_sample_list'),
    path('lab-update-sample/<int:pk>/', views.lab_update_sample, name='lab_update_sample'),
    path('report-approval/', views.report_approval, name='report_approval'),
    path('view-report-full/<int:pk>/', views.view_report_full, name='view_report_full'),
    path('update-report-full/<int:pk>/', views.update_report_full, name='update_report_full'),
    path('view-pdf/<int:pk>/', views.ViewPDF, name='ViewPDF'),
    path('download-pdf/<int:pk>/', views.DownloadPDF, name='DownloadPDF'),

    path('ajax/load-projects/', views.load_projects, name='ajax_load_projects'),
    path('ajax/sieve-plot-generator/', views.SievePlotGenerator, name='ajax_sieve_plot_generator'),
    path('ajax/load-parameter-form/', views.load_parameter_form, name='ajax_load_parameter_form'),

]
