from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import landing_page

urlpatterns = [
    path('', landing_page, name='landing'),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('app/', include('core.urls')),
]
