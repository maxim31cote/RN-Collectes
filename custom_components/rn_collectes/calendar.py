"""Calendrier pour Rouyn-Noranda Collectes."""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import logging

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configurer le calendrier depuis une entrée de configuration."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([CollectesCalendar(coordinator, entry)])


class CollectesCalendar(CoordinatorEntity, CalendarEntity):
    """Calendrier des collectes."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialiser le calendrier."""
        super().__init__(coordinator)
        self._entry = entry
        # Utiliser le numéro affiché pour distinguer plusieurs adresses
        displayed_number = entry.data.get("displayed_number", entry.data.get("civic_number", ""))
        self._attr_name = f"{displayed_number} - Calendrier"
        self._attr_unique_id = f"{entry.entry_id}_calendar"

    @property
    def event(self) -> CalendarEvent | None:
        """Retourner le prochain événement."""
        if not self.coordinator.data:
            return None

        all_events = self.coordinator.data.get('all_events', [])
        
        if not all_events:
            return None

        # Trouver le prochain événement (utiliser le fuseau horaire de Rouyn-Noranda)
        tz = ZoneInfo("America/Toronto")
        now = datetime.now(tz)
        for event_data in all_events:
            if event_data['date'] >= now:
                return CalendarEvent(
                    start=event_data['date'],
                    end=event_data['date'] + timedelta(days=1),
                    summary=event_data['summary'],
                    description=event_data.get('description', ''),
                )

        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Retourner les événements entre deux dates."""
        if not self.coordinator.data:
            return []

        all_events = self.coordinator.data.get('all_events', [])
        
        events = []
        for event_data in all_events:
            event_date = event_data['date']
            
            # Vérifier si l'événement est dans la plage de dates
            if start_date <= event_date <= end_date:
                events.append(
                    CalendarEvent(
                        start=event_date,
                        end=event_date + timedelta(days=1),
                        summary=event_data['summary'],
                        description=event_data.get('description', ''),
                    )
                )

        return events

    @property
    def device_info(self):
        """Retourner les informations du périphérique."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.title,
            "manufacturer": "Ville de Rouyn-Noranda",
            "model": "Calendrier de collectes",
        }
