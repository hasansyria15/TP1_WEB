"""
URL configuration for AirLibre_AldulaimiHasan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import include, path
import activities.views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', activities.views.index, name='home'),
    path('admin/', admin.site.urls),
    path('activities/', include('activities.urls')),
    path('accounts/login/', activities.views.Login_view, name='login'),  # Surcharge la vue login
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', activities.views.signup_view, name='signup')
]

# Gestionnaires d'erreurs personnalisés
handler400 = 'activities.views.render_400_error'
handler403 = 'activities.views.render_403_error'
handler404 = 'activities.views.render_404_error'
handler500 = 'activities.views.render_500_error'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
