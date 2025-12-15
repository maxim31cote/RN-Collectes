# Documentation Technique - Rouyn-Noranda Collectes

## Architecture de l'intégration

Cette intégration utilise l'API du portail citoyen de Rouyn-Noranda pour récupérer les calendriers de collecte au format iCalendar (.ics).

### Composants principaux

#### 1. collector.py
Responsable de la récupération des données depuis le site web.

**Méthodes statiques** :
- `async_get_streets()` : Récupère la liste complète des rues depuis le HTML de la page
- `async_get_civic_numbers(street)` : Appelle l'API AJAX OctoberCMS pour obtenir les numéros civiques d'une rue

**API utilisée pour les numéros civiques** :
```python
POST https://citoyen.rouyn-noranda.ca/calendrier-de-collectes
Headers:
  X-Requested-With: XMLHttpRequest
  X-OCTOBER-REQUEST-HANDLER: addressPicker::onChangeStreet
  X-OCTOBER-REQUEST-PARTIALS: addressPicker::dropdown_civic
Data:
  addresses_street: <nom_de_la_rue>

Réponse JSON:
{
  "addressPicker::dropdown_civic": "<option>...</option>..."
}
```

**Récupération du fichier .ics** :
1. Soumission du formulaire en AJAX avec :
   - Headers : `X-OCTOBER-REQUEST-HANDLER: avisComposanteCollectes0::onSubmitAddressFromPicker`
   - Headers : `X-OCTOBER-REQUEST-PARTIALS: avisComposanteCollectes0::schedule`
   - Data : `addresses_street` et `addresses_civic`

2. La réponse JSON contient le HTML du calendrier qui inclut l'URL du fichier .ics

3. Extraction de l'URL `.ics` depuis le HTML :
   - Format : `https://citoyen.rouyn-noranda.ca/avis/collectes/calendrier.ics?secteurs=XX`
   - Le paramètre `secteurs` correspond au secteur de collecte (ex: 45 pour le secteur 23)

4. Téléchargement du fichier .ics depuis l'URL extraite

5. Parsing du fichier iCalendar

#### 2. config_flow.py
Gère le processus de configuration en 2 étapes :

**Étape 1 - Sélection de la rue** (`async_step_user`) :
- Récupère la liste des rues via `CollectesCollector.async_get_streets()`
- Affiche un sélecteur déroulant
- Stocke la rue sélectionnée dans `self._selected_street`

**Étape 2 - Sélection du numéro civique** (`async_step_civic_number`) :
- Récupère les numéros civiques via `CollectesCollector.async_get_civic_numbers()`
- Affiche un sélecteur déroulant si des numéros sont disponibles
- Sinon, permet la saisie manuelle
- Valide l'adresse en tentant de récupérer le calendrier

**Mode de secours** (`async_step_manual`) :
- Permet la saisie manuelle si la récupération des listes échoue
- Utilisé comme fallback en cas de problème avec le site

#### 3. sensor.py
Crée 5 capteurs, un pour chaque type de collecte :

**Capteurs créés** :
- `sensor.prochaine_collecte_dechets`
- `sensor.prochaine_collecte_recuperation`
- `sensor.prochaine_collecte_compost`
- `sensor.prochaine_collecte_encombrants`
- `sensor.prochaine_collecte_residus_verts`

**État du capteur** : Date de la prochaine collecte (YYYY-MM-DD)

**Attributs** :
- `type_collecte` : Type de collecte
- `jours_restants` : Nombre de jours avant la collecte
- `prochaine_date` : Date formatée
- `prochaines_collectes` : Liste des 5 prochaines collectes
- `description` : Description de l'événement
- `derniere_mise_a_jour` : Timestamp de la dernière mise à jour

#### 4. calendar.py
Crée une entité calendrier contenant tous les événements de collecte.

**Fonctionnalités** :
- `event` : Retourne le prochain événement
- `async_get_events(start, end)` : Retourne tous les événements dans une plage de dates
- Compatible avec toutes les cartes de calendrier de Home Assistant

### Parsing du fichier iCalendar

La méthode `_parse_ics()` dans `collector.py` :

1. Parse le fichier .ics avec la bibliothèque `icalendar`
2. Utilise `recurring-ical-events` pour gérer les événements récurrents
3. Extrait les événements des 365 prochains jours
4. Catégorise les événements par type basé sur le résumé (SUMMARY)
5. Retourne une structure de données organisée

**Détection du type de collecte** :
```python
for collecte_type in COLLECTE_TYPES:
    if collecte_type.lower() in summary.lower():
        collectes[collecte_type].append(event_data)
```

### Gestion des mises à jour

Le `DataUpdateCoordinator` dans `__init__.py` :
- Intervalle de mise à jour : 12 heures
- Méthode de mise à jour : `collector.async_get_collectes()`
- Gestion automatique des erreurs et des réessais

### Structure des données

**Format retourné par `async_get_collectes()`** :
```python
{
    'collectes': {
        'Déchets': [
            {'date': datetime, 'summary': str, 'description': str},
            ...
        ],
        'Récupération': [...],
        'Compost': [...],
        'Encombrants': [...],
        'Résidus verts': [...]
    },
    'all_events': [
        {'date': datetime, 'summary': str, 'description': str},
        ...
    ],
    'last_update': datetime
}
```

## Dépendances

```
icalendar>=5.0.0          # Parsing des fichiers .ics
recurring-ical-events>=2.0.0  # Gestion des événements récurrents
aiohttp>=3.8.0            # Requêtes HTTP asynchrones
```

## Points d'attention

1. **Parsing HTML** : Le code parse le HTML du site, qui pourrait changer. Des regex sont utilisées pour extraire les données.

2. **API OctoberCMS** : L'intégration utilise l'API AJAX d'OctoberCMS. Les headers spécifiques sont nécessaires :
   - `X-OCTOBER-REQUEST-HANDLER`
   - `X-OCTOBER-REQUEST-PARTIALS`

3. **Noms de champs** : Les champs du formulaire sont :
   - `addresses_street` (et non `street`)
   - `addresses_civic` (et non `civic_number`)

4. **Sessions HTTP** : Une session `aiohttp` est créée et réutilisée pour éviter de créer trop de connexions.

## Tests

Un script de test est disponible : `test_integration.py`

```bash
# Modifier les variables dans le script
python test_integration.py
```

## Debugging

Pour activer les logs de debug dans Home Assistant :

```yaml
logger:
  default: info
  logs:
    custom_components.rouyn_noranda_collectes: debug
```

## Maintenance

Si le site web change :

1. **Changement des noms de rues** : Les rues sont extraites dynamiquement, aucun changement nécessaire
2. **Changement de l'API** : Vérifier les endpoints dans les outils de développement du navigateur
3. **Changement du format .ics** : Vérifier le parsing dans `_parse_ics()`
4. **Nouveaux types de collecte** : Ajouter dans `const.py` → `COLLECTE_TYPES`
