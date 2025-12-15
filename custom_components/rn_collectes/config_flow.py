"""Config flow pour Rouyn-Noranda Collectes."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import DOMAIN
from .collector import CollectesCollector

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Valider l'entrée utilisateur."""
    collector = CollectesCollector(
        street=data["street"],
        civic_number=data["civic_number"]
    )

    # Tenter de récupérer les données pour valider l'adresse
    try:
        collectes = await collector.async_get_collectes()
        if not collectes:
            raise InvalidAddress
    except Exception as err:
        _LOGGER.error("Erreur lors de la validation: %s", err)
        raise CannotConnect from err

    # Retourner un titre pour l'intégration
    return {"title": f"Collectes {data['street']} {data['civic_number']}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gérer le flux de configuration."""

    VERSION = 1

    def __init__(self):
        """Initialiser le flux de configuration."""
        self._streets = []
        self._selected_street = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Gérer l'étape de sélection de la rue."""
        errors: dict[str, str] = {}
        
        # Récupérer la liste des rues si on ne l'a pas encore
        if not self._streets:
            self._streets = await CollectesCollector.async_get_streets()
            
            # Si on ne peut pas récupérer les rues, permettre la saisie manuelle
            if not self._streets:
                _LOGGER.warning("Impossible de récupérer la liste des rues, passage en mode manuel")
                return await self.async_step_manual()
        
        if user_input is not None:
            self._selected_street = user_input["street"]
            return await self.async_step_civic_number()

        # Créer le schéma avec la liste déroulante des rues
        data_schema = vol.Schema(
            {
                vol.Required("street"): SelectSelector(
                    SelectSelectorConfig(
                        options=self._streets,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"num_streets": str(len(self._streets))},
        )

    async def async_step_civic_number(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Gérer l'étape de sélection du numéro civique."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Combiner les données des deux étapes
            full_data = {
                "street": self._selected_street,
                "civic_number": user_input["civic_number"],
            }
            
            try:
                info = await validate_input(self.hass, full_data)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAddress:
                errors["base"] = "invalid_address"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Erreur inattendue")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=full_data)

        # Essayer de récupérer les numéros civiques pour cette rue
        civic_numbers = await CollectesCollector.async_get_civic_numbers(self._selected_street)
        
        if civic_numbers:
            # Si on a une liste, utiliser un sélecteur
            data_schema = vol.Schema(
                {
                    vol.Required("civic_number"): SelectSelector(
                        SelectSelectorConfig(
                            options=civic_numbers,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            )
        else:
            # Sinon, permettre la saisie manuelle
            data_schema = vol.Schema(
                {
                    vol.Required("civic_number"): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.TEXT)
                    ),
                }
            )

        return self.async_show_form(
            step_id="civic_number",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"street": self._selected_street},
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Permettre la saisie manuelle si les listes ne sont pas disponibles."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAddress:
                errors["base"] = "invalid_address"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Erreur inattendue")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required("street"): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
                vol.Required("civic_number"): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
            }
        )

        return self.async_show_form(
            step_id="manual", data_schema=data_schema, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Erreur pour indiquer que nous ne pouvons pas nous connecter."""


class InvalidAddress(HomeAssistantError):
    """Erreur pour indiquer qu'il y a une adresse invalide."""
