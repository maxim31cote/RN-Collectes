class RNCollectesCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      const card = document.createElement('ha-card');
      card.header = 'Prochaines Collectes';
      this.content = document.createElement('div');
      this.content.style.padding = '16px';
      card.appendChild(this.content);
      this.appendChild(card);
    }

    const entities = this._config.entities || [];
    const collectes = [];

    // Récupérer les données de chaque capteur
    entities.forEach(entityId => {
      const state = hass.states[entityId];
      if (state) {
        const jours = state.attributes.jours_restants;
        const type = state.attributes.type_collecte;
        const prochaine = state.attributes.prochaine_date;
        
        if (jours !== undefined && type) {
          collectes.push({
            type: type,
            jours: parseInt(jours),
            date: prochaine,
            entityId: entityId
          });
        }
      }
    });

    // Trier par nombre de jours
    collectes.sort((a, b) => a.jours - b.jours);

    // Icônes et couleurs pour chaque type
    const icons = {
      'Déchets': { icon: '🗑️', color: '#4CAF50' },
      'Récupération': { icon: '♻️', color: '#2196F3' },
      'Compost': { icon: '🌱', color: '#8BC34A' },
      'Encombrants': { icon: '📦', color: '#FF9800' },
      'Résidus verts': { icon: '🍂', color: '#4CAF50' },
      'Arbre de Noël': { icon: '🎄', color: '#F44336' }
    };

    // Générer le HTML
    let html = '<style>';
    html += '.collecte-item { display: flex; align-items: center; padding: 12px; margin-bottom: 8px; border-radius: 8px; background: var(--card-background-color); border: 1px solid var(--divider-color); }';
    html += '.collecte-icon { font-size: 32px; margin-right: 16px; }';
    html += '.collecte-info { flex: 1; }';
    html += '.collecte-type { font-weight: 500; font-size: 16px; margin-bottom: 4px; }';
    html += '.collecte-date { font-size: 12px; color: var(--secondary-text-color); }';
    html += '.collecte-badge { padding: 4px 12px; border-radius: 12px; font-weight: 500; font-size: 14px; white-space: nowrap; }';
    html += '.badge-urgent { background: #f44336; color: white; }';
    html += '.badge-bientot { background: #ff9800; color: white; }';
    html += '.badge-normal { background: #4caf50; color: white; }';
    html += '.badge-loin { background: var(--disabled-text-color); color: white; }';
    html += '</style>';

    if (collectes.length === 0) {
      html += '<p style="text-align: center; color: var(--secondary-text-color);">Aucune collecte à venir</p>';
    } else {
      collectes.forEach(collecte => {
        const config = icons[collecte.type] || { icon: '📋', color: '#757575' };
        
        // Déterminer la classe du badge selon les jours
        let badgeClass = 'badge-loin';
        let joursText = `${collecte.jours} jours`;
        
        if (collecte.jours === 0) {
          badgeClass = 'badge-urgent';
          joursText = 'Aujourd\'hui';
        } else if (collecte.jours === 1) {
          badgeClass = 'badge-urgent';
          joursText = 'Demain';
        } else if (collecte.jours <= 2) {
          badgeClass = 'badge-bientot';
        } else if (collecte.jours <= 5) {
          badgeClass = 'badge-normal';
        }

        html += `
          <div class="collecte-item">
            <div class="collecte-icon">${config.icon}</div>
            <div class="collecte-info">
              <div class="collecte-type" style="color: ${config.color}">${collecte.type}</div>
              <div class="collecte-date">${collecte.date || 'Date inconnue'}</div>
            </div>
            <div class="collecte-badge ${badgeClass}">${joursText}</div>
          </div>
        `;
      });
    }

    this.content.innerHTML = html;
  }

  setConfig(config) {
    if (!config.entities || config.entities.length === 0) {
      throw new Error('Vous devez définir au moins une entité');
    }
    this._config = config;
  }

  getCardSize() {
    return 3;
  }

  static getConfigElement() {
    return document.createElement("rn-collectes-card-editor");
  }

  static getStubConfig() {
    return {
      entities: []
    };
  }
}

customElements.define('rn-collectes-card', RNCollectesCard);

// Ajouter la carte à la fenêtre pour la rendre disponible
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'rn-collectes-card',
  name: 'Carte Collectes RN',
  description: 'Affiche les prochaines collectes de Rouyn-Noranda'
});

console.info(
  '%c RN-COLLECTES-CARD %c Version 1.0.0 ',
  'color: white; background: #4CAF50; font-weight: 700;',
  'color: #4CAF50; background: white; font-weight: 700;'
);
