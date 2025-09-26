# AirLibre - Instructions pour les agents IA

## Vue d'ensemble de l'architecture

AirLibre est une application Django pour la découverte et le partage d'activités de plein air. L'architecture suit le pattern MVT de Django avec une app principale `activities` qui gère toute la logique métier.

### Structure du projet
- **App principale** : `activities/` - contient tous les modèles, vues, templates et logique métier
- **Configuration** : `AirLibre_AldulaimiHasan/` - settings Django et URLs racines
- **Modèle utilisateur personnalisé** : `activities.User` (défini dans `AUTH_USER_MODEL`)
- **Base de données** : SQLite (`db.sqlite3`) pour le développement

## Patterns et conventions critiques

### Modèles de données
- **User personnalisé** (`activities.models.User`) hérite d'AbstractUser avec `avatar` et `bio`
- **Activity** avec validation personnalisée dans `clean()` - l'heure de fin doit être après le début
- **Category** pour organiser les activités
- Relations : Activity.proposer (organisateur), Activity.attendees (participants M2M)

### Architecture des vues
- Mélange de vues fonction et de logique métier complexe dans `activities/views.py`
- Pattern de redirection pour utilisateurs authentifiés (`Login_view`, `signup_view`)
- Intégration API externe pour qualité de l'air via `activities/services/aqi.py`
- Gestion d'erreurs avec `Http404` pour paramètres de recherche invalides

### Gestion des formulaires
- Fichier `activities/froms.py` (attention : typo "froms" au lieu de "forms")
- `LoginForm` personnalisé avec méthode `save()` qui retourne l'utilisateur authentifié
- `RegisterForm` hérite de UserCreationForm
- `ArticleSearchForm` pour filtrage des activités

### Service externe AQI
```python
# Pattern d'utilisation du service AQI dans activities/services/aqi.py
air_data = get_air_quality(activity.location_city)
aqi_value = air_data["data"]["aqi"] if air_data else None
```
- Nécessite variable d'environnement `AQICN_TOKEN`
- Gestion d'erreurs avec `ValueError` pour token manquant ou ville introuvable

## Configuration et dépendances

### Environnement virtuel
```powershell
# Activation sur Windows
& .venv/Scripts/Activate.ps1

# Migration des modèles
python manage.py migrate
```

### Variables d'environnement
- `AQICN_TOKEN` : Token API pour service qualité de l'air (fichier `.env`)
- Configuration locale : français canadien (`fr-ca`), fuseau `America/Toronto`

### Fichiers statiques
- **Development** : `activities/static/` pour CSS/JS de l'app
- **Production** : `STATIC_ROOT = BASE_DIR / 'staticfiles'`
- CSS compilé avec SCSS : `activities/static/activities/scss/style.scss`

## Patterns de templates

### Structure de base
- `templates/base.html` : Template parent avec Bootstrap 5.3 et Font Awesome
- Partials dans `templates/partials/` : `_navbar.html`, `_footer.html`
- Templates d'activités dans `templates/activities/`

### URLs et routage
- URLs racines dans `AirLibre_AldulaimiHasan/urls.py`
- URLs d'activités dans `activities/urls.py`
- Pattern : home (`''`) → `activities.views.index`

## Workflow de développement

### Commandes essentielles
```powershell
# Serveur de dev
python manage.py runserver

# Nouvelles migrations
python manage.py makemigrations
python manage.py migrate

# Shell Django
python manage.py shell
```

### Debugging
- Print statements actifs dans `Login_view` pour debugging authentification
- Messages Django utilisés pour feedback utilisateur (`messages.success`, `messages.error`)

## Points d'attention

### Erreurs communes
- **Typo** : `froms.py` au lieu de `forms.py` - garder la cohérence
- **Validation** : Toujours appeler `clean()` avant `save()` sur les modèles Activity
- **Authentification** : Vérifier `request.user.is_authenticated` avant accès aux vues protégées
- **AQI Service** : Gérer les `ValueError` pour token manquant ou ville non trouvée

### Sécurité
- Secret key hardcodée (à changer pour production)
- `DEBUG = True` (désactiver pour production)
- Validation CSRF active par défaut