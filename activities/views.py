from django.shortcuts import render, Http404
from django.http import HttpResponse
from .froms import CustomAuthenticationForm
from django.utils import timezone
from django.db import models
from .models import Activity
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
    return render(request, 'activities/home.html', {'activities': ACTIVITIES})

def Login_view(request):
    form = CustomAuthenticationForm()
    print("Champs du formulaire:", form.fields)
    return render(request, 'registration/login.html', {'form': form})


def activity_detail(request, activity_id):
    # Rechercher l'activité par ID
    activity = None
    for act in ACTIVITIES:
        if act['id'] == activity_id:
            activity = act
            break

    if activity is None:
        raise Http404("Cette activité n'existe pas")

    return render(request, 'activities/detail.html', {'activity': activity})



def activity_list(request):
    # pylint: disable=no-member
    activities = Activity.objects.order_by('start_time')
    return render(request, 'activities/activity_list.html', {'activities': activities})
