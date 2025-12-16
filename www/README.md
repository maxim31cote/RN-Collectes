# Carte Custom - Collectes Rouyn-Noranda

Une carte Lovelace moderne pour afficher vos prochaines collectes avec de belles icônes et un code couleur intelligent.

## 📸 Aperçu

La carte affiche :
- 🗑️ **Icônes visuelles** pour chaque type de collecte
- 🎨 **Code couleur** pour le nombre de jours :
  - 🔴 Rouge : Aujourd'hui ou demain
  - 🟠 Orange : Dans 2 jours
  - 🟢 Vert : Dans 3-5 jours
  - ⚪ Gris : Plus de 5 jours
- 📅 **Date de collecte** pour chaque type
- ⏱️ **Tri automatique** par proximité

## 🚀 Installation

### Méthode 1 : HACS (Recommandé une fois ajouté)

1. Ouvrir HACS
2. Aller dans "Frontend"
3. Chercher "RN Collectes Card"
4. Cliquer sur "Download"

### Méthode 2 : Manuel

1. **Télécharger le fichier** `rn-collectes-card.js`

2. **Copier dans votre dossier www**
   ```bash
   # Depuis votre configuration Home Assistant
   mkdir -p www
   cp rn-collectes-card.js www/
   ```

3. **Ajouter la ressource dans Home Assistant**
   - Aller dans **Paramètres** → **Tableaux de bord** → **Ressources**
   - Cliquer sur **+ Ajouter une ressource**
   - URL : `/local/rn-collectes-card.js`
   - Type de ressource : **Module JavaScript**

4. **Redémarrer Home Assistant** (ou vider le cache du navigateur)

## ⚙️ Configuration

### Configuration de base

```yaml
type: custom:rn-collectes-card
entities:
  - sensor.5056_dechets
  - sensor.5056_recuperation
  - sensor.5056_compost
  - sensor.5056_encombrants
  - sensor.5056_residus_verts
  - sensor.5056_arbre_de_noel
```

### Configuration multi-adresse

```yaml
type: custom:rn-collectes-card
entities:
  - sensor.5056_dechets
  - sensor.5056_recuperation
  - sensor.1234_dechets
  - sensor.1234_recuperation
```

### Via l'interface graphique

1. Ajouter une carte
2. Chercher "Carte Collectes RN"
3. Sélectionner vos entités
4. Sauvegarder

## 🎨 Personnalisation

La carte s'adapte automatiquement au thème Home Assistant (clair/sombre).

### Modifier le titre

```yaml
type: custom:rn-collectes-card
title: Mes Collectes
entities:
  - sensor.5056_dechets
  - sensor.5056_recuperation
```

## 🐛 Dépannage

### La carte n'apparaît pas

1. Vérifier que la ressource est bien ajoutée dans **Paramètres → Tableaux de bord → Ressources**
2. Vider le cache du navigateur (Ctrl+F5)
3. Vérifier la console du navigateur (F12) pour les erreurs

### Les icônes ne s'affichent pas

Les icônes sont des emojis Unicode, elles devraient s'afficher sur tous les navigateurs modernes.

### Erreur "Vous devez définir au moins une entité"

Assurez-vous d'avoir au moins une entité dans la configuration :
```yaml
entities:
  - sensor.votre_capteur_ici
```

## 📝 Exemples

### Carte simple avec titre personnalisé

```yaml
type: custom:rn-collectes-card
title: 🗑️ Prochaines Collectes
entities:
  - sensor.5056_dechets
  - sensor.5056_recuperation
  - sensor.5056_compost
```

### Dans une vue avec d'autres cartes

```yaml
views:
  - title: Accueil
    cards:
      - type: custom:rn-collectes-card
        entities:
          - sensor.5056_dechets
          - sensor.5056_recuperation
      
      - type: calendar
        entities:
          - calendar.5056_calendrier
```

## 🔄 Mises à jour

Pour mettre à jour la carte :
1. Télécharger la nouvelle version de `rn-collectes-card.js`
2. Remplacer l'ancienne dans le dossier `www`
3. Vider le cache du navigateur (Ctrl+F5)

## 📄 Licence

MIT License - Voir le fichier LICENSE du projet principal
