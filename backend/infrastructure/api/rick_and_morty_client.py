"""Rick & Morty API client implementation."""
import httpx
from typing import Any
from core.models import Character, Location, Episode
from core.ports import RickAndMortyClient
from shared.config import settings
from shared.logging import logger


class RickAndMortyRESTClient(RickAndMortyClient):
    """HTTP client for Rick & Morty API."""
    
    def __init__(self):
        self.base_url = settings.rick_and_morty_api_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def _fetch_all_pages(self, endpoint: str) -> list[dict[str, Any]]:
        """Fetch all pages from a paginated endpoint."""
        all_results = []
        url = f"{self.base_url}/{endpoint}"
        
        while url:
            try:
                response = await self.client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if "results" in data:
                    all_results.extend(data["results"])
                else:
                    all_results.append(data)
                
                url = data.get("info", {}).get("next")
            except httpx.HTTPError as e:
                logger.error(f"Error fetching {url}: {e}")
                break
        
        return all_results
    
    def _parse_character(self, data: dict[str, Any]) -> Character:
        """Parse API response to Character model."""
        return Character(
            id=data["id"],
            name=data["name"],
            status=data["status"],
            species=data["species"],
            type=data.get("type") or "",
            gender=data["gender"],
            origin=data.get("origin") or {},
            location=data.get("location") or {},
            image=data["image"],
            episode=data.get("episode") or [],
            url=data["url"],
            created=data["created"],
        )
    
    def _parse_location(self, location_data: dict[str, Any]) -> Location:
        """Parse location data."""
        return Location(
            id=location_data["id"],
            name=location_data["name"],
            type=location_data["type"],
            dimension=location_data["dimension"],
            residents=[],  # Will be populated separately
        )
    
    async def get_locations(self) -> list[Location]:
        """Fetch all locations."""
        locations_data = await self._fetch_all_pages("location")
        locations = [self._parse_location(loc) for loc in locations_data]
        
        # Fetch residents for each location
        for location in locations:
            location_data = next(
                (loc for loc in locations_data if loc["id"] == location.id),
                None
            )
            if location_data and location_data.get("residents"):
                resident_urls = location_data["residents"]
                character_ids = [
                    int(url.split("/")[-1]) for url in resident_urls
                ]
                if character_ids:
                    characters = await self.get_characters(character_ids)
                    location.residents = characters
        
        return locations
    
    async def get_location(self, location_id: int) -> Location:
        """Fetch a specific location."""
        try:
            response = await self.client.get(
                f"{self.base_url}/location/{location_id}"
            )
            response.raise_for_status()
            location_data = response.json()
            
            location = self._parse_location(location_data)
            
            # Fetch residents
            if location_data.get("residents"):
                character_ids = [
                    int(url.split("/")[-1])
                    for url in location_data["residents"]
                ]
                if character_ids:
                    characters = await self.get_characters(character_ids)
                    location.residents = characters
            
            return location
        except httpx.HTTPError as e:
            logger.error(f"Error fetching location {location_id}: {e}")
            raise
    
    async def get_character(self, character_id: int) -> Character:
        """Fetch a specific character."""
        try:
            response = await self.client.get(
                f"{self.base_url}/character/{character_id}"
            )
            response.raise_for_status()
            data = response.json()
            return self._parse_character(data)
        except httpx.HTTPError as e:
            logger.error(f"Error fetching character {character_id}: {e}")
            raise
    
    async def get_characters(self, character_ids: list[int]) -> list[Character]:
        """Fetch multiple characters."""
        if not character_ids:
            return []
        
        # API supports batch fetching if IDs are consecutive
        # For simplicity, fetch individually or in batches
        characters = []
        
        # Try batch fetch first (for consecutive IDs)
        try:
            ids_str = ",".join(map(str, character_ids))
            response = await self.client.get(
                f"{self.base_url}/character/{ids_str}"
            )
            response.raise_for_status()
            data = response.json()
            
            # API returns list or single object
            if isinstance(data, list):
                characters = [self._parse_character(char) for char in data]
            else:
                characters = [self._parse_character(data)]
        except httpx.HTTPError:
            # Fallback to individual fetches
            for char_id in character_ids:
                try:
                    character = await self.get_character(char_id)
                    characters.append(character)
                except Exception as e:
                    logger.warning(f"Failed to fetch character {char_id}: {e}")
        
        return characters
    
    async def get_all_characters(self) -> list[Character]:
        """Fetch all characters."""
        try:
            characters_data = await self._fetch_all_pages("character")
            if not characters_data:
                logger.warning("No characters data returned from API")
                return []
            characters = []
            for char_data in characters_data:
                try:
                    character = self._parse_character(char_data)
                    characters.append(character)
                except Exception as e:
                    logger.warning(f"Failed to parse character data: {e}, data: {char_data}")
                    continue
            return characters
        except Exception as e:
            logger.error(f"Error fetching all characters: {e}")
            raise
    
    def _parse_episode(self, data: dict[str, Any]) -> Episode:
        """Parse API response to Episode model."""
        return Episode(
            id=data["id"],
            name=data["name"],
            air_date=data["air_date"],
            episode=data["episode"],
            characters=data["characters"],
            url=data["url"],
            created=data["created"],
        )
    
    async def get_episodes(self) -> list[Episode]:
        """Fetch all episodes."""
        episodes_data = await self._fetch_all_pages("episode")
        return [self._parse_episode(ep) for ep in episodes_data]
    
    async def get_episode(self, episode_id: int) -> Episode:
        """Fetch a specific episode."""
        try:
            response = await self.client.get(
                f"{self.base_url}/episode/{episode_id}"
            )
            response.raise_for_status()
            data = response.json()
            return self._parse_episode(data)
        except httpx.HTTPError as e:
            logger.error(f"Error fetching episode {episode_id}: {e}")
            raise
    
    async def get_episodes_by_ids(self, episode_ids: list[int]) -> list[Episode]:
        """Fetch multiple episodes by IDs."""
        if not episode_ids:
            return []
        
        try:
            ids_str = ",".join(map(str, episode_ids))
            response = await self.client.get(
                f"{self.base_url}/episode/{ids_str}"
            )
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                return [self._parse_episode(ep) for ep in data]
            else:
                return [self._parse_episode(data)]
        except httpx.HTTPError:
            # Fallback to individual fetches
            episodes = []
            for ep_id in episode_ids:
                try:
                    episode = await self.get_episode(ep_id)
                    episodes.append(episode)
                except Exception as e:
                    logger.warning(f"Failed to fetch episode {ep_id}: {e}")
            return episodes

