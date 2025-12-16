# Collectes Rouyn-Noranda - Intégration Home Assistant

Cette intégration permet de suivre les collectes de déchets, récupération, compost, encombrants et résidus verts de la Ville de Rouyn-Noranda.

## ✨ Fonctionnalités

- 🔄 **Listes déroulantes intelligentes** : Sélection facile de votre rue et numéro civique depuis les données officielles de la ville
- 📊 **5 capteurs de collecte** : Un capteur pour chaque type de collecte avec la prochaine date
- 📅 **Calendrier intégré** : Tous les événements de collecte dans le calendrier Home Assistant
- 🔔 **Automatisations** : Créez des rappels avant chaque collecte
- 🕐 **Mise à jour automatique** : Synchronisation toutes les 12 heures avec le site de la ville

## Installation

### HACS (Recommandé)

[![Ajouter à HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=maxim31cote&repository=RN-Collectes&category=integration)

**OU manuellement :**

1. Ouvrez HACS dans Home Assistant
2. Allez dans "Intégrations"
3. Cliquez sur les trois points en haut à droite et sélectionnez "Dépôts personnalisés"
4. Ajoutez l'URL : `https://github.com/maxim31cote/RN-Collectes`
5. Sélectionnez la catégorie "Integration"
6. Recherchez "RN-Collectes" et installez-le
7. Redémarrez Home Assistant

### Installation manuelle

1. Téléchargez la dernière version depuis [GitHub](https://github.com/maxim31cote/RN-Collectes)
2. Copiez le dossier `custom_components/rn_collectes` dans votre dossier `config/custom_components/`
3. Redémarrez Home Assistant

## Configuration

1. Allez dans Paramètres → Appareils et services → Ajouter une intégration
2. Recherchez "RN-Collectes"
3. **Étape 1** : Sélectionnez votre rue dans la liste déroulante (toutes les rues de Rouyn-Noranda sont disponibles)
4. **Étape 2** : Sélectionnez votre numéro civique dans la liste déroulante (les numéros sont chargés automatiquement pour votre rue)
5. Cliquez sur "Soumettre"

L'intégration créera automatiquement :
- 5 capteurs, un pour chaque type de collecte :
  - Prochaine collecte Déchets
  - Prochaine collecte Récupération
  - Prochaine collecte Compost
  - Prochaine collecte Encombrants
  - Prochaine collecte Résidus verts
- 1 calendrier contenant tous les événements de collecte

## Utilisation

### Capteurs

Chaque capteur affiche la date de la prochaine collecte pour son type. Les attributs supplémentaires incluent :
- `jours_restants` : Nombre de jours avant la prochaine collecte
- `prochaine_date` : Date de la prochaine collecte (format YYYY-MM-DD)
- `prochaines_collectes` : Liste des 5 prochaines collectes
- `type_collecte` : Type de collecte
- `derniere_mise_a_jour` : Date de la dernière mise à jour

### Calendrier

Le calendrier affiche tous les événements de collecte et peut être utilisé dans :
- La vue calendrier de Home Assistant
- Les cartes de calendrier personnalisées
- Les automatisations basées sur les événements de calendrier

### Exemple d'automatisation

```yaml
automation:
  - alias: "Rappel collecte déchets"
    trigger:
      - platform: state
        entity_id: sensor.prochaine_collecte_dechets
        attribute: jours_restants
        to: "1"
    action:
      - service: notify.mobile_app
        data:
          message: "N'oubliez pas de sortir les déchets demain!"
```

### Exemple de carte Lovelace

```yaml
type: entities
title: Prochaines collectes
entities:
  - entity: sensor.prochaine_collecte_dechets
  - entity: sensor.prochaine_collecte_recuperation
  - entity: sensor.prochaine_collecte_compost
  - entity: sensor.prochaine_collecte_encombrants
  - entity: sensor.prochaine_collecte_residus_verts
```

## 📱 Blueprint de notification

Un blueprint est disponible pour créer facilement des automatisations de notification avec messages personnalisés.

[![Importer le blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fmaxim31cote%2FRN-Collectes%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Frn_collectes%2Fnotification_collecte.yaml)

**Fonctionnalités du blueprint :**
- ⏰ Heure de notification personnalisable
- 📅 Choix du nombre de jours avant la collecte (0-7 jours)
- ✅ Sélection des types de collecte à surveiller
- 💬 Messages intelligents qui s'adaptent ("aujourd'hui", "demain", "dans X jours")
- 📱 Support multi-appareils

**Exemples de messages :**
- `N'oublie pas de mettre le "Déchets" au chemin pour demain !`
- `N'oublie pas de mettre les "Déchets et Récupération" au chemin pour aujourd'hui !`
- `N'oublie pas de mettre les "Déchets, Récupération et Compost" au chemin pour dans 2 jours !`

[Plus d'informations sur le blueprint](blueprints/README.md)

## Mise à jour des données

Les données sont mises à jour automatiquement toutes les 12 heures. Vous pouvez forcer une mise à jour en rechargeant l'intégration.

## Support

Pour signaler un problème ou suggérer une amélioration, veuillez ouvrir une issue sur GitHub.

## Licence

Ce projet est sous licence MIT.
