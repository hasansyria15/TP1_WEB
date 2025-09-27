import os
from django.shortcuts import render, Http404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .froms import LoginForm, RegisterForm, UserEditForm
from django.utils import timezone
from django.contrib import messages
from .models import Activity, User
from .froms import ArticleSearchForm, addNewActivity
from .services.aqi import get_air_quality
from django.http import HttpResponseBadRequest
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.conf import settings

# Create your views here.

# Fonctions d'aide pour les pages d'erreur personnalisées
def render_400_error(request, message="Requête invalide"):
    """Retourne une page d'erreur 400 personnalisée"""
    return render(request, '400.html', {
        'exception': message
    }, status=400)

def render_403_error(request, message="Accès interdit"):
    """Retourne une page d'erreur 403 personnalisée"""
    return render(request, '403.html', {
        'exception': message
    }, status=403)

def render_404_error(request, message="Page non trouvée"):
    """Retourne une page d'erreur 404 personnalisée"""
    return render(request, '404.html', {
        'exception': message
    }, status=404)

def render_500_error(request, message="Erreur serveur"):
    """Retourne une page d'erreur 500 personnalisée"""
    return render(request, '500.html', {
        'exception': message
    }, status=500)

def redirect_to_login_with_message(request, message="Vous devez être connecté pour accéder à cette page."):
    """Redirige vers la page de connexion avec un message d'erreur"""
    messages.error(request, message)
    # Récupérer l'URL actuelle pour la redirection après connexion
    next_url = request.get_full_path()
    return redirect(f"{settings.LOGIN_URL}?next={next_url}")

def custom_login_required(message="Vous devez être connecté pour accéder à cette page."):
    """Décorateur personnalisé pour exiger une authentification avec message personnalisé"""
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login_with_message(request, message)
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator

#Done
def index(request):
    # pylint: disable=no-member
    activities = Activity.objects.filter(
        start_time__gte=timezone.now()
    ).select_related('category', 'proposer').order_by('start_time')[:3]

    return render(request, 'activities/home.html', {'activities': activities})

#Done
def Login_view(request):

    # Empêche l'accès à la page de connexion si l'utilisateur est déjà connecté
    if request.user.is_authenticated:
        return redirect('home')

    # Vérifier si l'utilisateur vient d'une page nécessitant une connexion
    next_url = request.GET.get('next', '')
    if 'add' in next_url:
        messages.info(request, "Vous devez être connecté pour ajouter une activité.")
    elif 'profile' in next_url:
        messages.info(request, "Vous devez être connecté pour accéder à votre profil.")
    elif next_url and next_url != '/':
        messages.info(request, "Vous devez être connecté pour accéder à cette page.")

    if request.method == 'POST':
        form = LoginForm(request.POST)

        # un débug simple pour voir les données reçues
        print(f"Données POST reçues: {request.POST}")

        if form.is_valid():
             # Récupérer les données du formulaire
            user = form.save()


            # Extra debug pour s'Assurer que l'utilisateur existe
            if user is not None:
                login(request, user)
                print(f"Connexion réussie pour l'utilisateur: {user.username}")
                return redirect('home')
            else:
                print("Authentification échouée")
        else:
            print(f"Formulaire invalide - Erreurs: {form.errors}")
            print(f"Non-field errors: {form.non_field_errors()}")
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})

#Done
def signup_view(request):

    # Empêche l'accès à la page d'inscription si l'utilisateur est déjà connecté
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie. Vous êtes maintenant connecté.")
            return redirect('home')
        else:
            messages.error(request, "Erreur lors de l'inscription. Veuillez corriger les erreurs ci-dessous.")
    else:
        form = RegisterForm()

    return render(request, 'registration/signup.html', {'form': form})

#Done
def activity_detail(request, activity_id):
    # Rechercher l'activité par ID
    # pylint: disable=no-member
    activity = Activity.objects.filter(id=activity_id).first()

    # Vérifier que l'activité existe avant d'aller plus loin
    if activity is None:
        return render_404_error(request, "Cette activité n'existe pas")

    # Récupérer la qualité de l'air pour la localisation de l'activité
    air_data = None
    aqi_description = None
    aqi_value = None
    aqi_error_message = None
    
    try:
        air_data = get_air_quality(activity.location_city)
        aqi_value = air_data["data"]["aqi"] if air_data and "data" in air_data and "aqi" in air_data["data"] else None

        if aqi_value is not None:
            # Process the AQI value here
            if aqi_value <= 50:
                aqi_description = {
                    'level': 'Bon',
                    'color': 'success',
                    'description': 'Qualité de l\'air excellente, idéale pour les activités extérieures'
                }
            elif aqi_value <= 100:
                aqi_description = {
                    'level': 'Modéré',
                    'color': 'warning',
                    'description': 'Qualité de l\'air acceptable, mais certaines personnes sensibles pourraient ressentir des effets'
                }
            elif aqi_value <= 150:
                aqi_description = {
                    'level': 'Mauvais pour les sensibles',
                    'color': 'orange',
                    'description': 'Les personnes sensibles devraient réduire les activités prolongées à l\'extérieur'
                }
            elif aqi_value <= 200:
                aqi_description = {
                    'level': 'Mauvais',
                    'color': 'danger',
                    'description': 'Tout le monde pourrait commencer à ressentir des effets sur la santé; les personnes sensibles devraient éviter les activités extérieures'
                }
            elif aqi_value <= 300:
                aqi_description = {
                    'level': 'Très mauvais',
                    'color': 'dark',
                    'description': 'Aucune activité extérieure recommandée pour tout le monde'
                }
            else:
                aqi_description = {
                    'level': 'Dangereux',
                    'color': 'black',
                    'description': 'Aucune activité extérieure recommandée pour tout le monde'
                }
        else:
            aqi_error_message = "Les données de qualité de l'air ne sont pas disponibles pour cette ville"
            
    except ValueError as e:
        # Gestion spécifique des erreurs de l'API
        error_msg = str(e).lower()
        if "ville non trouvée" in error_msg or "not found" in error_msg or "unknown station" in error_msg:
            aqi_error_message = f"Données de qualité de l'air non disponibles pour '{activity.location_city}'"
        elif "timeout" in error_msg:
            aqi_error_message = "Service de qualité de l'air trop lent à répondre"
        elif "réseau" in error_msg or "network" in error_msg or "connexion" in error_msg or "dns" in error_msg:
            aqi_error_message = "Impossible de récupérer les données de qualité de l'air (problème de connexion)"
        elif "token" in error_msg:
            aqi_error_message = "Service de qualité de l'air temporairement indisponible (authentification)"
        elif "limite" in error_msg or "limit" in error_msg:
            aqi_error_message = "Service de qualité de l'air temporairement indisponible (limite atteinte)"
        elif "invalide" in error_msg or "invalid" in error_msg:
            aqi_error_message = f"Nom de ville '{activity.location_city}' non reconnu par le service"
        else:
            aqi_error_message = "Données de qualité de l'air temporairement indisponibles"
        
        # Log l'erreur pour le développeur mais ne pas l'afficher à l'utilisateur
        print(f"[AQI] Erreur pour {activity.location_city}: {e}")
        
    except Exception as e:
        # Gestion des erreurs inattendues
        aqi_error_message = "Données de qualité de l'air temporairement indisponibles"
        print(f"[AQI] Erreur inattendue pour {activity.location_city}: {e}")

    # compter le nombre des participants
    participant_count = activity.attendees.count()
    for a in activity.attendees.all():
        print(a.first_name + " " + a.last_name)

    context = {
        'activity': activity,
        'participant_count': participant_count,
        'air_quality': aqi_value,
        'aqi_description': aqi_description,
        'aqi_error_message': aqi_error_message,
    }

    return render(request, 'activities/activity_detail.html', context)

#done
def activity_list(request):
    # Récupérer toutes les activités par défaut
    # pylint: disable=no-member
    activities = Activity.objects.filter(
        start_time__gte=timezone.now()
    )
    

    # Créer une instance du formulaire avec les données GET
    form = ArticleSearchForm(request.GET)

    # Obtenir scoop directement de request.GET car il peut venir des boutons
    scoop = request.GET.get('scoop')

    # Vérifier si le formulaire est valide
    if form.is_valid():
        # Filtrage par catégorie
        category = form.cleaned_data.get('category')

        if category and category != 'all':
            activities = activities.filter(category__name=category)

        # Filtrage par vue
        if scoop and scoop != 'all':
            if request.user.is_authenticated:
                if scoop == 'mine':
                    # Mes activités proposées
                    activities = activities.filter(proposer=request.user)
                elif scoop == 'inscrit':
                    # Mes inscriptions
                    activities = activities.filter(attendees=request.user)
            else:
                # Utilisateur non connecté essayant d'accéder à une section privée
                return redirect_to_login_with_message(request, "Vous devez être connecté pour voir cette section")
    else:
        # Si le formulaire n'est pas valide, rediriger vers la page d'erreur 400
        error_message = ""
        for field, errors in form.errors.items():
            for error in errors:
                error_message += f"{field}: {error} "

        # Retourner une page d'erreur 400 personnalisée
        return render_400_error(request, error_message.strip())

    # Ordonner par date de début
    activities = activities.order_by('start_time')

    context = {
        'activities': activities,
        'form': form,
        'scoop': scoop or 'all',  # Passer le paramètre scoop au template
    }

    return render(request, 'activities/activity_list.html', context)

#Done
def profile(request, user_id=None):
    """
    Vue pour la page de profil utilisateur.
    Si user_id est fourni, affiche le profil de cet utilisateur.
    Sinon, affiche le profil de l'utilisateur connecté.
    """

    # pylint: disable=no-member
    if not request.user.is_authenticated:
        return redirect_to_login_with_message(request, "Vous devez être connecté pour voir les profils")

    # Si un user_id est fourni, récupérer cet utilisateur, sinon l'utilisateur connecté
    if user_id:
        try:
            utilisateur = User.objects.get(id=user_id)

        except User.DoesNotExist:
            raise Http404("Utilisateur non trouvé")
    else:
        utilisateur = request.user

    # Récupérer toutes les activités pour les statistiques
    all_activities_proposed = Activity.objects.filter(proposer=utilisateur)
    all_activities_attending = Activity.objects.filter(attendees=utilisateur)

    # Récupérer les 2 activités les plus récentes de chaque type
    recent_activities_proposed = all_activities_proposed.order_by('-start_time')[:2]
    recent_activities_attending = all_activities_attending.order_by('-start_time')[:2]

    context = {
        'activities_proposed': all_activities_proposed,  # Pour les statistiques
        'activities_attending': all_activities_attending,  # Pour les statistiques
        'recent_activities_proposed': recent_activities_proposed,  # Pour l'affichage
        'recent_activities_attending': recent_activities_attending,  # Pour l'affichage
        'user': utilisateur,
    }


    return render(request, 'activities/profile.html', context)

#Done
@custom_login_required("Vous devez être connecté pour modifier votre profil.")
def edit_profile(request):
    """
    Vue pour modifier le profil utilisateur.
    GET: Affiche le formulaire pré-rempli avec les données actuelles
    POST: Traite et sauvegarde les modifications
    """
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=request.user, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = UserEditForm(instance=request.user, user=request.user)

    return render(request, 'activities/edit_profile.html', {
        'form': form,
        'user': request.user,
    })

# Vues de test pour les pages d'erreur (à supprimer en production)
def test_404(request):
    """Vue de test pour la page d'erreur 404"""
    return render_404_error(request, "Page de test 404 - Cette page n'existe pas")

def test_400(request):
    """Vue de test pour la page d'erreur 400"""
    return render_400_error(request, "Erreur de test 400 - Paramètres de requête invalides")

def test_403(request):
    """Vue de test pour la page d'erreur 403"""
    return render_403_error(request, "Erreur de test 403 - Vous n'avez pas l'autorisation d'accéder à cette ressource")

def test_500(request):
    """Vue de test pour la page d'erreur 500"""
    return render_500_error(request, "Erreur de test 500 - Problème technique sur le serveur")

def test_500_real(request):
    """Vue de test qui déclenche une vraie erreur 500"""
    # Déclencher intentionnellement une erreur pour tester le gestionnaire
    raise Exception("Erreur de test 500 - Division par zéro intentionnelle")
    return None  # Cette ligne ne sera jamais exécutée

def test_aqi_errors(request):
    """Vue de test pour tester différents scénarios d'erreurs AQI"""
    test_cities = [
        "Paris",           # Devrait fonctionner
        "VilleInexistante123", # Ville non trouvée
        "",                # Nom vide
        "A"                # Nom trop court
    ]
    
    results = []
    for city in test_cities:
        try:
            if city == "":
                city_display = "[vide]"
            else:
                city_display = city
                
            air_data = get_air_quality(city) if city else get_air_quality("VilleTestErreur")
            aqi_value = air_data["data"]["aqi"] if air_data else None
            results.append({
                'city': city_display,
                'status': 'Succès',
                'aqi': aqi_value,
                'error': None
            })
        except ValueError as e:
            results.append({
                'city': city_display,
                'status': 'Erreur',
                'aqi': None,
                'error': str(e)
            })
        except Exception as e:
            results.append({
                'city': city_display,
                'status': 'Erreur inattendue',
                'aqi': None,
                'error': str(e)
            })
    
    return render(request, 'activities/test_aqi.html', {'results': results})


#Done
@custom_login_required("Vous devez être connecté pour réserver une activité.")
def reserve_activity(request, activity_id):
    """Vue pour gérer l'inscription/désinscription aux activités"""
    # Le décorateur @custom_login_required gère déjà l'authentification

    # Récupérer l'activité ou retourner 404
    try:
        activity = Activity.objects.get(id=activity_id)
    except Activity.DoesNotExist:
        return render_404_error(request, f"L'activité avec l'ID {activity_id} n'existe pas")

    # Vérifier que l'utilisateur n'est pas le proposeur
    if activity.proposer == request.user:
        messages.error(request, f"Impossible de s'inscrire à votre propre activité '{activity.title}'. En tant qu'organisateur, vous êtes automatiquement associé à cette activité.")
        return redirect('activity_detail', activity_id=activity_id)

    # Vérifier si l'activité n'est pas passée
    if activity.start_time < timezone.now():
        messages.error(request, "Impossible de s'inscrire à une activité passée.")
        return redirect('activity_detail', activity_id=activity_id)

    # Gérer l'inscription/désinscription
    if request.user in activity.attendees.all():
        # L'utilisateur est déjà inscrit, le désinscrire
        activity.attendees.remove(request.user)
        messages.success(request, f"Vous vous êtes désinscrit de l'activité '{activity.title}'.")
    else:
        # L'utilisateur n'est pas inscrit, l'inscrire
        activity.attendees.add(request.user)
        messages.success(request, f"Vous êtes maintenant inscrit à l'activité '{activity.title}' !")

    return redirect('activity_detail', activity_id=activity_id)


#Done
@custom_login_required("Vous devez être connecté pour créer une activité.")
def add_activity(request):
    """Vue pour ajouter une nouvelle activité"""
    
    if request.method == 'POST':
        form = addNewActivity(request.POST)
        if form.is_valid():
            new_activity = form.save(commit=False)
            new_activity.proposer = request.user
            new_activity.save()
            form.save_m2m()  # Pour sauvegarder les relations ManyToMany

            messages.success(request, "Nouvelle activité ajoutée avec succès!")
            return redirect('activity_detail', activity_id=new_activity.id)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = addNewActivity()

    return render(request, 'activities/add_activity.html', {'form': form})
