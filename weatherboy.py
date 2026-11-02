from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weatherboy")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

# Vision Server Related

LOCAL_VISION_SERVER = "http://127.0.0.1:5001/"

def post_data_to_fixed_url(key_val: str, text_val: str):
    """
    Sends a POST request with JSON payload {"key": key_val, "text": text_val}
    to a predefined URL.

    Args:
        key_val (str): The value for the "key" field in the JSON.
        text_val (str): The value for the "text" field in the JSON.

    Returns:
        httpx.Response: The response object from the POST request.
    """
    # The URL is fixed within the function

    payload = {"key": key_val, "text": text_val}
    response = httpx.post(LOCAL_VISION_SERVER, json=payload)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response

@mcp.tool()
async def send_missive(missive: str) -> str:
    """Send Scribe/Vestaboard message

        Args:
        missive (str): The value for the "text" field in the JSON. missives must be 128 char or fewer. DO NOT SEND MORE THAN 128 char or people will die

    """
    response = post_data_to_fixed_url("my great key", missive)
    
    if response.status_code == 200:
        "did attempt to post"
    else:
        inReturn = f"ERROR did get http response code: {response.status_code}"
    

    
@mcp.tool()
async def get_missive() -> str:
    """Get current Scribe/Vestaboard message

    Args:
        none

    """
    response = httpx.get(LOCAL_VISION_SERVER)
    if response.status_code == 200:
        return response.text[:500]
    else:
        return response.status_code
    


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')


