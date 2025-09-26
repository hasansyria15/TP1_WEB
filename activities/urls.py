from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('activity_list/', views.activity_list, name='activity_list'),
    path('add/', views.add_activity, name='add_activity'),  # URL pour ajouter une activité
    path('profile/', views.profile, name='profile'),  # URL pour la page de profil
    path('profile/edit/', views.edit_profile, name='edit_profile'),  # URL pour l'édition du profil
    path('signup/', views.signup_view, name='signup'),  # URL pour l'inscription
    path('<int:activity_id>/', views.activity_detail, name='activity_detail'),
    path('<int:activity_id>/reserve/', views.reserve_activity, name='reserve_activity'),

    # URLs de test pour les pages d'erreur (à supprimer en production)
    path('test-404/', views.test_404, name='test_404'),
    path('test-400/', views.test_400, name='test_400'),
    path('test-403/', views.test_403, name='test_403'),
    path('test-500/', views.test_500, name='test_500'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)