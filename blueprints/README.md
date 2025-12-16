# Blueprints RN-Collectes

Ce dossier contient des blueprints pour automatiser les notifications de collecte.

## 📱 Notification de Collecte

**Fichier:** `automation/rn_collectes/notification_collecte.yaml`

Ce blueprint permet de créer une automation qui envoie des notifications personnalisées pour rappeler les collectes à venir.

### Fonctionnalités

- ⏰ **Heure personnalisable** : Choisissez l'heure de la notification
- 📅 **Jours avant** : Configurez combien de jours avant la collecte vous voulez être notifié (0-7 jours)
- ✅ **Sélection des types** : Activez/désactivez les notifications pour chaque type de collecte avec des checkboxes :
  - Déchets
  - Récupération
  - Compost
  - Encombrants
  - Résidus verts
  - Arbre de Noël
- 🤖 **Détection automatique** : Les capteurs sont trouvés automatiquement, pas besoin de les sélectionner manuellement !
- 📱 **Multi-appareils** : Sélectionnez plusieurs appareils dans une liste
- 💬 **Messages intelligents** : Le message s'adapte automatiquement :
  - "aujourd'hui" si jour même
  - "demain" si la veille
  - "dans X jours" pour les autres cas

### Exemple de messages

- 1 type : `N'oublie pas de mettre le "Déchets" au chemin pour demain !`
- 2 types : `N'oublie pas de mettre les "Déchets et Récupération" au chemin pour demain !`
- 3+ types : `N'oublie pas de mettre les "Déchets, Récupération et Compost" au chemin pour demain !`

### Installation

#### Via l'interface Home Assistant

1. Allez dans **Paramètres** → **Automatisations & Scènes**
2. Cliquez sur **Blueprints**
3. Cliquez sur **Importer un blueprint**
4. Collez l'URL : `https://github.com/maxim31cote/RN-Collectes/blob/main/blueprints/automation/rn_collectes/notification_collecte.yaml`

#### Manuellement

1. Copiez le fichier dans `config/blueprints/automation/rn_collectes/notification_collecte.yaml`
2. Redémarrez Home Assistant

### Utilisation

1. Créez une nouvelle automation basée sur ce blueprint
2. Configurez :
   - **Adresse** : Sélectionnez n'importe quel capteur de l'adresse à surveiller (si vous avez plusieurs adresses configurées)
   - L'heure de notification (ex: 19:00)
   - Le nombre de jours avant (ex: 1 pour la veille)
   - Cochez les types de collecte à surveiller (Déchets, Récupération, Compost, etc.)
   - Sélectionnez les appareils qui recevront les notifications dans la liste
3. Sauvegardez l'automation

**Note :** Les capteurs sont détectés automatiquement pour l'adresse choisie ! Si vous avez plusieurs adresses, créez une automation par adresse.

### Prérequis

- Intégration **RN-Collectes** configurée
- Application mobile **Home Assistant** installée sur vos appareils
- Service de notification **mobile_app** configuré

### Exemples de configuration

#### Notification la veille à 19h

- **Heure** : 19:00
- **Jours avant** : 1
- **Types** : Déchets, Récupération, Compost activés
- **Appareils** : Votre téléphone

#### Notification le matin même à 7h

- **Heure** : 07:00
- **Jours avant** : 0
- **Types** : Tous activés
- **Appareils** : Tous les téléphones de la maison

#### Notification 2 jours avant à 20h

- **Heure** : 20:00
- **Jours avant** : 2
- **Types** : Encombrants uniquement
- **Appareils** : Votre téléphone
