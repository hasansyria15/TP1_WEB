from django.urls import path
from . import views
from .froms import CustomAuthenticationForm
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('activity_list/', views.activity_list, name='activity_list'),
    path('<int:activity_id>/', views.activity_detail, name='activity_detail'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)