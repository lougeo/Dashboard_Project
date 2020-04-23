"""exl_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from users import views as user_views
from dashboard import views as dashboard_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('home/', dashboard_views.home, name='home'),
    path('new-project/', dashboard_views.new_project, name='new_project'),
    path('new-report/', dashboard_views.new_report, name='new_report'),
    path('new-report-add/', dashboard_views.new_report_add, name='new_report_add'),
    path('update-report/', dashboard_views.update_report, name='update_report'),
    path('update-report-add/<int:pk>/', dashboard_views.update_report_add, name='update_report_add'),
    path('report-approval/', dashboard_views.report_approval, name='report_approval'),
    path('', include('dashboard.urls'))
]
