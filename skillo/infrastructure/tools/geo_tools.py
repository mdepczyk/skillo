from geopy.distance import geodesic  # type: ignore
from geopy.geocoders import Nominatim  # type: ignore
from langchain.tools import tool


@tool
def calculate_distance_tool(cities: str) -> str:
    """Calculate distance between two cities."""
    try:
        if " | " not in cities:
            return "Error: Please provide cities in format 'City1 | City2'"

        city1, city2 = cities.split(" | ")
        city1, city2 = city1.strip(), city2.strip()

        if not city1 or not city2:
            return "Error: Both city names are required"

        geolocator = Nominatim(user_agent="skillo", timeout=10)

        coords1 = geolocator.geocode(city1)
        coords2 = geolocator.geocode(city2)

        if not coords1:
            return f"Error: Could not find coordinates for {city1}"

        if not coords2:
            return f"Error: Could not find coordinates for {city2}"

        distance_km = geodesic(
            (coords1.latitude, coords1.longitude),
            (coords2.latitude, coords2.longitude),
        ).kilometers

        return f"Distance between {city1} and {city2}: {distance_km:.1f} km"

    except Exception as e:
        return f"Error calculating distance: {str(e)}"
