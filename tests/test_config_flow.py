"""Test the Home Assistant Utilities config flow."""
from unittest.mock import AsyncMock

from custom_components.letmeknow.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_form(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": hass.config_entries.SOURCE_USER,
        },
    )
    assert "type" in result and result["type"] == FlowResultType.FORM
    assert "errors" in result and result["errors"] == {}

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {},
    )
    await hass.async_block_till_done()

    assert "type" in result2 and result2["type"] == FlowResultType.CREATE_ENTRY
    assert "data" in result2 and result2["data"] == {}
    assert len(mock_setup_entry.mock_calls) == 1
