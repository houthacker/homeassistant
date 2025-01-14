"""Test the Forecast.Solar config flow."""

from unittest.mock import AsyncMock

import pytest

from homeassistant.components.forecast_solar.const import (
    CONF_AZIMUTH,
    CONF_DAMPING_EVENING,
    CONF_DAMPING_MORNING,
    CONF_DECLINATION,
    CONF_INVERTER_SIZE,
    CONF_MODULES_POWER,
    DOMAIN,
)
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from tests.common import MockConfigEntry


async def test_user_flow(hass: HomeAssistant, mock_setup_entry: AsyncMock) -> None:
    """Test the full user configuration flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_NAME: "Name",
            CONF_LATITUDE: 52.42,
            CONF_LONGITUDE: 4.42,
            CONF_AZIMUTH: 142,
            CONF_DECLINATION: 42,
            CONF_MODULES_POWER: 4242,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY

    config_entry = result["result"]
    assert config_entry.title == "Name"
    assert config_entry.unique_id is None
    assert config_entry.data == {
        CONF_LATITUDE: 52.42,
        CONF_LONGITUDE: 4.42,
    }
    assert config_entry.options == {
        CONF_AZIMUTH: 142,
        CONF_DECLINATION: 42,
        CONF_MODULES_POWER: 4242,
    }

    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.usefixtures("mock_setup_entry")
async def test_options_flow_invalid_api(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test options config flow when API key is invalid."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_API_KEY: "solarPOWER!",
            CONF_DECLINATION: 21,
            CONF_AZIMUTH: 22,
            CONF_MODULES_POWER: 2122,
            CONF_DAMPING_MORNING: 0.25,
            CONF_DAMPING_EVENING: 0.25,
            CONF_INVERTER_SIZE: 2000,
        },
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_API_KEY: "invalid_api_key"}

    # Ensure we can recover from this error
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_API_KEY: "SolarForecast150",
            CONF_DECLINATION: 21,
            CONF_AZIMUTH: 22,
            CONF_MODULES_POWER: 2122,
            CONF_DAMPING_MORNING: 0.25,
            CONF_DAMPING_EVENING: 0.25,
            CONF_INVERTER_SIZE: 2000,
        },
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        CONF_API_KEY: "SolarForecast150",
        CONF_DECLINATION: 21,
        CONF_AZIMUTH: 22,
        CONF_MODULES_POWER: 2122,
        CONF_DAMPING_MORNING: 0.25,
        CONF_DAMPING_EVENING: 0.25,
        CONF_INVERTER_SIZE: 2000,
    }


@pytest.mark.usefixtures("mock_setup_entry")
async def test_options_flow(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test config flow options."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    # With the API key
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_API_KEY: "SolarForecast150",
            CONF_DECLINATION: 21,
            CONF_AZIMUTH: 22,
            CONF_MODULES_POWER: 2122,
            CONF_DAMPING_MORNING: 0.25,
            CONF_DAMPING_EVENING: 0.25,
            CONF_INVERTER_SIZE: 2000,
        },
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        CONF_API_KEY: "SolarForecast150",
        CONF_DECLINATION: 21,
        CONF_AZIMUTH: 22,
        CONF_MODULES_POWER: 2122,
        CONF_DAMPING_MORNING: 0.25,
        CONF_DAMPING_EVENING: 0.25,
        CONF_INVERTER_SIZE: 2000,
    }


@pytest.mark.usefixtures("mock_setup_entry")
async def test_options_flow_without_key(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test config flow options."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    # Without the API key
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_DECLINATION: 21,
            CONF_AZIMUTH: 22,
            CONF_MODULES_POWER: 2122,
            CONF_DAMPING_MORNING: 0.25,
            CONF_DAMPING_EVENING: 0.25,
            CONF_INVERTER_SIZE: 2000,
        },
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        CONF_API_KEY: None,
        CONF_DECLINATION: 21,
        CONF_AZIMUTH: 22,
        CONF_MODULES_POWER: 2122,
        CONF_DAMPING_MORNING: 0.25,
        CONF_DAMPING_EVENING: 0.25,
        CONF_INVERTER_SIZE: 2000,
    }
