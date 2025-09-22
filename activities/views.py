from django.shortcuts import render, Http404
from django.http import HttpResponse
from .froms import CustomAuthenticationForm
from django.utils import timezone
from django.db import models
from .models import Activity, Category
from .froms import ArticleSearchForm

# Create your views here.

# Exemples d'activités pour affichage (à remplacer par des données de la base de données)
ACTIVITIES = [
    {
        'id': 1,
        'name': 'Randonnée en montagne',
        'description': 'Découvrez les magnifiques paysages montagneux lors d\'une randonnée guidée.',
        'price': 50.00,
        'duration': '4 heures',
        'difficulty': 'Modérée',
        'location': 'Montagnes des Laurentides'
    },
    {
        'id': 2,
        'name': 'Kayak sur le lac',
        'description': 'Profitez d\'une journée relaxante en kayak sur les eaux calmes du lac.',
        'price': 35.00,
        'duration': '2 heures',
        'difficulty': 'Facile',
        'location': 'Lac Saint-Jean'
    },
    {
        'id': 3,
        'name': 'Vélo de montagne',
        'description': 'Aventurez-vous sur les sentiers accidentés avec nos vélos de montagne de qualité.',
        'price': 45.00,
        'duration': '3 heures',
        'difficulty': 'Difficile',
        'location': 'Mont-Tremblant'
    }
]

def index(request):
    activities = Activity.objects.filter(
        start_time__gte=timezone.now()
    ).select_related('category', 'proposer').order_by('start_time')[:3]

    return render(request, 'activities/home.html', {'activities': activities})

def Login_view(request):
    form = CustomAuthenticationForm()
    print("Champs du formulaire:", form.fields)
    return render(request, 'registration/login.html', {'form': form})


def activity_detail(request, activity_id):
    # Rechercher l'activité par ID
    activity = Activity.objects.filter(id=activity_id).first()

    # compter le nombre des participants
    participant_count = activity.attendees.count() 
    for a in activity.attendees.all():
        print(a.first_name + " " + a.last_name)
    
    context = {
        'activity': activity,
        'participant_count': participant_count,
    }
    
    if activity is None:
        raise Http404("Cette activité n'existe pas")


    return render(request, 'activities/activity_detail.html', context)


def activity_list(request):
    # Récupérer toutes les activités par défaut
    activities = Activity.objects.filter(
        start_time__gte=timezone.now()
    )
    
    # Créer une instance du formulaire avec les données GET
    form = ArticleSearchForm(request.GET)
    
    # Obtenir scoop directement de request.GET car il peut venir des boutons
    scoop = request.GET.get('scoop')
    
    if form.is_valid():
        # Filtrage par catégorie
        category = form.cleaned_data.get('category')
        if category and category != 'all':
            activities = activities.filter(category__name=category)
    
    # Filtrage par vue - maintenant en dehors de form.is_valid()
    if scoop and scoop != 'all':
        if request.user.is_authenticated:
            if scoop == 'mine':
                # Mes activités proposées
                activities = activities.filter(proposer=request.user)
            elif scoop == 'inscrit':
                # Mes inscriptions
                activities = activities.filter(attendees=request.user)


    
    # Ordonner par date de début
    activities = activities.order_by('start_time')
    
    context = {
        'activities': activities,
        'form': form,
        'scoop': scoop or 'all',  # Passer le paramètre scoop au template
    }
    
    return render(request, 'activities/activity_list.html', context)


def profile(request):
    """
    Vue pour la page de profil utilisateur.
    Cette vue est simplifiée et ne contient pas de logique backend.
    """
    return render(request, 'activities/profile.html')

def edit_profile(request):
    """
    Vue pour la page d'édition du profil utilisateur.
    Cette vue est simplifiée et ne contient pas de logique backend.
    """
    return render(request, 'activities/edit_profile.html')
