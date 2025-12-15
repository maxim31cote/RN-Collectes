"""Collecteur de données pour Rouyn-Noranda."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
import re
import aiohttp
from icalendar import Calendar
import recurring_ical_events

from .const import BASE_URL, COLLECTE_TYPES

_LOGGER = logging.getLogger(__name__)


class CollectesCollector:
    """Classe pour récupérer les données de collecte."""

    def __init__(self, street: str = None, civic_number: str = None) -> None:
        """Initialiser le collecteur."""
        self.street = street
        self.civic_number = civic_number
        self._session = None

    @staticmethod
    async def async_get_streets() -> list[str]:
        """Récupérer la liste des rues disponibles."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{BASE_URL}/calendrier-de-collectes") as response:
                    html = await response.text()
                    
                    # Chercher les options de rue dans le HTML
                    # Pattern pour trouver les options du select
                    pattern = r'<option[^>]*value="([^"]+)"[^>]*>([^<]+)</option>'
                    matches = re.findall(pattern, html)
                    
                    streets = []
                    for value, text in matches:
                        # Filtrer les options vides et garder seulement les rues
                        if value and value.strip() and not value.startswith('--'):
                            streets.append(text.strip())
                    
                    # Si on ne trouve pas d'options, retourner une liste vide
                    if not streets:
                        _LOGGER.warning("Aucune rue trouvée dans le HTML")
                    
                    return sorted(set(streets))  # Retirer les doublons et trier
                    
            except Exception as err:
                _LOGGER.error("Erreur lors de la récupération des rues: %s", err)
                return []

    @staticmethod
    async def async_get_civic_numbers(street: str) -> list[str]:
        """Récupérer la liste des numéros civiques pour une rue donnée."""
        async with aiohttp.ClientSession() as session:
            try:
                # Appeler l'API AJAX d'OctoberCMS pour obtenir les numéros civiques
                headers = {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-OCTOBER-REQUEST-HANDLER': 'addressPicker::onChangeStreet',
                    'X-OCTOBER-REQUEST-PARTIALS': 'addressPicker::dropdown_civic',
                }
                
                data = {
                    'addresses_street': street,
                }
                
                async with session.post(
                    f"{BASE_URL}/calendrier-de-collectes",
                    headers=headers,
                    data=data
                ) as response:
                    result = await response.json()
                    
                    # Extraire les numéros civiques du HTML retourné
                    html_content = result.get('addressPicker::dropdown_civic', '')
                    
                    # Parser le HTML pour extraire les numéros civiques
                    pattern = r'<option value="[^"]*"\s*>([^<]+)</option>'
                    matches = re.findall(pattern, html_content)
                    
                    # Filtrer et nettoyer les numéros civiques
                    civic_numbers = []
                    for match in matches:
                        match = match.strip()
                        if match and match != "Saisir un no. civique":
                            civic_numbers.append(match)
                    
                    return civic_numbers
                
            except Exception as err:
                _LOGGER.error("Erreur lors de la récupération des numéros civiques: %s", err)
                return []

    async def async_get_collectes(self) -> dict[str, any]:
        """Récupérer les données de collecte."""
        try:
            # Créer la session si elle n'existe pas
            if self._session is None:
                self._session = aiohttp.ClientSession()

            # Soumettre le formulaire en AJAX pour obtenir le calendrier
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'X-OCTOBER-REQUEST-HANDLER': 'avisComposanteCollectes0::onSubmitAddressFromPicker',
                'X-OCTOBER-REQUEST-PARTIALS': 'avisComposanteCollectes0::schedule',
            }
            
            form_data = {
                "addresses_street": self.street,
                "addresses_civic": self.civic_number,
            }

            async with self._session.post(
                f"{BASE_URL}/calendrier-de-collectes",
                headers=headers,
                data=form_data,
                allow_redirects=True
            ) as response:
                result = await response.json()
                
                # Extraire le HTML du calendrier
                html_content = result.get('avisComposanteCollectes0::schedule', '')
                if not html_content:
                    html_content = result.get('#schedule', '')
                
                if not html_content:
                    _LOGGER.error("Aucune donnée de calendrier retournée")
                    return {}
                
                # Extraire l'URL du fichier .ics
                ics_match = re.search(r'href="(webcal://[^"]+\.ics[^"]*)"', html_content)
                if not ics_match:
                    ics_match = re.search(r'https://citoyen\.rouyn-noranda\.ca/avis/collectes/calendrier\.ics\?secteurs=(\d+)', html_content)
                    if ics_match:
                        secteur = ics_match.group(1)
                        ics_url = f"{BASE_URL}/avis/collectes/calendrier.ics?secteurs={secteur}"
                    else:
                        _LOGGER.error("Impossible de trouver le lien .ics dans la réponse")
                        return {}
                else:
                    ics_url = ics_match.group(1).replace('webcal://', 'https://')
                
                # Télécharger le fichier .ics
                async with self._session.get(ics_url) as ics_response:
                    ics_content = await ics_response.read()

            # Parser le fichier .ics
            return await self._parse_ics(ics_content)

        except Exception as err:
            _LOGGER.error("Erreur lors de la récupération des données: %s", err)
            raise

    async def _parse_ics(self, ics_content: bytes) -> dict[str, any]:
        """Parser le contenu ICS."""
        try:
            calendar = Calendar.from_ical(ics_content)
            
            # Obtenir les événements des 365 prochains jours
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=365)
            
            events = recurring_ical_events.of(calendar).between(start_date, end_date)
            
            # Organiser les événements par type de collecte
            collectes = {collecte_type: [] for collecte_type in COLLECTE_TYPES}
            all_events = []
            
            for event in events:
                summary = str(event.get('SUMMARY', ''))
                dtstart = event.get('DTSTART').dt
                
                # Convertir en datetime si c'est une date
                if isinstance(dtstart, datetime):
                    event_date = dtstart
                else:
                    event_date = datetime.combine(dtstart, datetime.min.time())
                
                event_data = {
                    'date': event_date,
                    'summary': summary,
                    'description': str(event.get('DESCRIPTION', '')),
                }
                
                all_events.append(event_data)
                
                # Associer l'événement à un type de collecte
                for collecte_type in COLLECTE_TYPES:
                    if collecte_type.lower() in summary.lower():
                        collectes[collecte_type].append(event_data)
                        break
            
            # Trier les événements par date
            for collecte_type in collectes:
                collectes[collecte_type].sort(key=lambda x: x['date'])
            
            all_events.sort(key=lambda x: x['date'])
            
            return {
                'collectes': collectes,
                'all_events': all_events,
                'last_update': datetime.now()
            }
            
        except Exception as err:
            _LOGGER.error("Erreur lors du parsing ICS: %s", err)
            raise

    async def async_close(self):
        """Fermer la session."""
        if self._session:
            await self._session.close()
