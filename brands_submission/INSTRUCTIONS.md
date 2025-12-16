# Instructions pour soumettre au dépôt brands

## Étapes à suivre :

1. **Va sur** : https://github.com/home-assistant/brands

2. **Fork le dépôt** : Clique sur "Fork" en haut à droite

3. **Dans ton fork**, va dans le dossier `custom_integrations/`

4. **Crée un nouveau dossier** `rn_collectes`

5. **Upload les 4 fichiers** depuis `brands_submission/custom_integrations/rn_collectes/` :
   - `icon.png` (256×256, fond transparent)
   - `icon@2x.png` (512×512, haute résolution)
   - `logo.png` (256×256, fond transparent)
   - `logo@2x.png` (512×512, haute résolution)

6. **Crée une Pull Request** avec :
   - **Titre** : `Add Collectes Rouyn-Noranda (rn_collectes)`
   - **Description** :
   ```
   # Collectes Rouyn-Noranda
   
   Custom integration for waste collection schedules in Rouyn-Noranda, Quebec, Canada.
   
   **Integration domain:** `rn_collectes`
   **Repository:** https://github.com/maxim31cote/RN-Collectes
   **Type:** Custom Integration
   
   This integration provides sensors and calendar entities for tracking:
   - Garbage collection (Déchets)
   - Recycling (Récupération) 
   - Compost
   - Bulk items (Encombrants)
   - Green waste (Résidus verts)
   - Christmas trees (Arbres de Noël)
   ```

7. **Attends l'approbation** - Les mainteneurs vont vérifier et merger ta PR

Une fois mergée, ton logo apparaîtra automatiquement dans Home Assistant !
