"""Capteurs pour Rouyn-Noranda Collectes."""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, COLLECTE_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configurer les capteurs depuis une entrée de configuration."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for collecte_type in COLLECTE_TYPES:
        entities.append(CollecteSensor(coordinator, entry, collecte_type))

    async_add_entities(entities)


class CollecteSensor(CoordinatorEntity, SensorEntity):
    """Capteur pour une collecte spécifique."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        collecte_type: str,
    ) -> None:
        """Initialiser le capteur."""
        super().__init__(coordinator)
        self.collecte_type = collecte_type
        self._entry = entry
        # Utiliser le numéro affiché pour distinguer plusieurs adresses
        displayed_number = entry.data.get("displayed_number", entry.data.get("civic_number", ""))
        self._attr_name = f"{displayed_number} - {collecte_type}"
        self._attr_unique_id = f"{entry.entry_id}_{collecte_type.lower().replace(' ', '_')}"
        self._attr_icon = self._get_icon()

    def _get_icon(self) -> str:
        """Retourner l'icône appropriée."""
        icons = {
            "Déchets": "mdi:trash-can",
            "Récupération": "mdi:recycle",
            "Compost": "mdi:leaf",
            "Encombrants": "mdi:sofa",
            "Résidus verts": "mdi:tree",
            "Arbre de Noël": "mdi:pine-tree",
        }
        return icons.get(self.collecte_type, "mdi:calendar")

    @property
    def native_value(self) -> str | None:
        """Retourner la date de la prochaine collecte."""
        if not self.coordinator.data:
            return None

        collectes = self.coordinator.data.get('collectes', {}).get(self.collecte_type, [])
        
        if not collectes:
            return None

        # Trouver la prochaine collecte (utiliser le fuseau horaire de Rouyn-Noranda)
        tz = ZoneInfo("America/Toronto")
        now = datetime.now(tz)
        for collecte in collectes:
            if collecte['date'] >= now:
                return collecte['date'].strftime('%Y-%m-%d')

        return None

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Retourner les attributs supplémentaires."""
        if not self.coordinator.data:
            return {}

        collectes = self.coordinator.data.get('collectes', {}).get(self.collecte_type, [])
        
        if not collectes:
            return {}

        # Utiliser le fuseau horaire de Rouyn-Noranda
        tz = ZoneInfo("America/Toronto")
        now = datetime.now(tz)
        next_collecte = None
        jours_restants = None

        # Trouver la prochaine collecte
        for collecte in collectes:
            if collecte['date'] >= now:
                next_collecte = collecte
                break

        if next_collecte:
            delta = next_collecte['date'] - now
            jours_restants = delta.days

        # Préparer la liste des prochaines collectes (max 5)
        upcoming = []
        count = 0
        for collecte in collectes:
            if collecte['date'] >= now and count < 5:
                upcoming.append({
                    'date': collecte['date'].strftime('%Y-%m-%d'),
                    'summary': collecte['summary']
                })
                count += 1

        return {
            'type_collecte': self.collecte_type,
            'jours_restants': jours_restants,
            'prochaine_date': next_collecte['date'].strftime('%Y-%m-%d') if next_collecte else None,
            'description': next_collecte['description'] if next_collecte else None,
            'prochaines_collectes': upcoming,
            'derniere_mise_a_jour': self.coordinator.data.get('last_update').isoformat() if self.coordinator.data.get('last_update') else None,
            'integration': DOMAIN,
            'days_until': jours_restants,
        }

    @property
    def device_info(self):
        """Retourner les informations du périphérique."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.title,
            "manufacturer": "Ville de Rouyn-Noranda",
            "model": "Calendrier de collectes",
        }
