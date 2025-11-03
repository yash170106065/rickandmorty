"""GraphQL client for Rick & Morty API."""
from gql import gql, Client  # type: ignore[import-untyped]
from gql.transport.aiohttp import AIOHTTPTransport  # type: ignore[import-untyped]
from typing import Any
from core.models import Character, Location, Episode
from core.ports import RickAndMortyClient
from shared.logging import logger


class RickAndMortyGraphQLClient(RickAndMortyClient):
    """GraphQL client for Rick & Morty API."""
    
    def __init__(self):
        # Store the transport URL - we'll create a new transport for each request
        # to avoid "Transport is already connected" errors
        self.graphql_url = "https://rickandmortyapi.com/graphql"
    
    async def _execute_query(self, query: Any, variable_values: dict[str, Any] = None) -> dict[str, Any]:
        """Execute a GraphQL query with a fresh client to avoid connection reuse issues."""
        # Create a new transport and client for each request
        # This avoids "Transport is already connected" errors
        transport = AIOHTTPTransport(url=self.graphql_url)
        client = Client(transport=transport, fetch_schema_from_transport=False)
        # Use async context manager to properly handle connection lifecycle
        async with client as session:
            # Set variable_values on the query object
            query.variable_values = variable_values or {}
            result = await session.execute(query)
            return result
    
    def _parse_character(self, data: dict[str, Any]) -> Character:
        """Parse GraphQL character data to Character model."""
        if not data:
            raise ValueError("Character data is None or empty")
        
        # Ensure required fields exist
        if not data.get("id"):
            raise ValueError("Character data missing required 'id' field")
        
        # Parse episodes if they're full objects (with id, name, air_date, etc.)
        episodes_data = None
        if data.get("episode") and len(data["episode"]) > 0:
            first_ep = data["episode"][0]
            # Check if first episode has full data (id and name fields indicate full object)
            if isinstance(first_ep, dict) and first_ep.get("id") is not None and first_ep.get("name") is not None:
                try:
                    episodes_data = [
                        self._parse_episode(ep) for ep in data["episode"]
                    ]
                except Exception as e:
                    logger.warning(f"Error parsing episodes_data for character {data.get('id')}: {e}")
                    episodes_data = None
        
        # Extract episode references - handle both full objects and simple references
        episode_refs = []
        for ep in data.get("episode", []):
            try:
                if isinstance(ep, dict):
                    # It's an object, get episode code or ID
                    episode_ref = ep.get("episode") or str(ep.get("id", ""))
                else:
                    episode_ref = str(ep)
                episode_refs.append(episode_ref)
            except Exception as e:
                logger.warning(f"Error parsing episode reference: {e}")
                continue
        
        # Safely parse origin and location
        origin = {}
        if data.get("origin"):
            try:
                origin = {
                    "name": data["origin"].get("name", ""),
                    "id": data["origin"].get("id")
                }
            except Exception as e:
                logger.warning(f"Error parsing origin for character {data.get('id')}: {e}")
        
        location = {}
        if data.get("location"):
            try:
                location = {
                    "name": data["location"].get("name", ""),
                    "id": data["location"].get("id")
                }
            except Exception as e:
                logger.warning(f"Error parsing location for character {data.get('id')}: {e}")
        
        return Character(
            id=int(data["id"]),
            name=data.get("name", "Unknown"),
            status=data.get("status", "Unknown"),
            species=data.get("species", "Unknown"),
            type=data.get("type") or "",
            gender=data.get("gender", "Unknown"),
            origin=origin,
            location=location,
            image=data.get("image", ""),
            episode=episode_refs,
            episodes_data=episodes_data,
            url=f"https://rickandmortyapi.com/api/character/{data['id']}",
            created=data.get("created", ""),
        )
    
    def _parse_location(self, data: dict[str, Any]) -> Location:
        """Parse GraphQL location data to Location model."""
        return Location(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            dimension=data["dimension"],
            residents=[],  # Will be populated separately
        )
    
    def _parse_episode(self, data: dict[str, Any]) -> Episode:
        """Parse GraphQL episode data to Episode model."""
        if not data:
            raise ValueError("Episode data is None or empty")
        
        if not data.get("id"):
            raise ValueError("Episode data missing required 'id' field")
        
        # Parse characters if they're full objects (with name, image, etc.)
        characters_data = None
        if data.get("characters") and len(data["characters"]) > 0:
            try:
                # Check if first character has full data (name field indicates full object)
                first_char = data["characters"][0]
                if isinstance(first_char, dict) and first_char.get("name") is not None:
                    characters_data = [
                        self._parse_character(char) for char in data["characters"]
                    ]
            except Exception as e:
                logger.warning(f"Error parsing characters_data for episode {data.get('id')}: {e}")
                characters_data = None
        
        # Extract character IDs - handle both dict objects and strings/ints
        character_ids = []
        if data.get("characters"):
            try:
                for char in data["characters"]:
                    if isinstance(char, dict):
                        char_id = char.get("id")
                        if char_id:
                            character_ids.append(str(char_id))
                    elif isinstance(char, (str, int)):
                        character_ids.append(str(char))
            except Exception as e:
                logger.warning(f"Error extracting character IDs for episode {data.get('id')}: {e}")
        
        return Episode(
            id=int(data["id"]),
            name=data.get("name", "Unknown"),
            air_date=data.get("air_date", ""),
            episode=data.get("episode", ""),
            characters=character_ids,
            characters_data=characters_data,
            url=f"https://rickandmortyapi.com/api/episode/{data['id']}",
            created=data.get("created", ""),
        )
    
    async def get_locations(self) -> list[Location]:
        """Fetch all locations using GraphQL (without nested residents)."""
        all_locations = []
        page = 1
        
        while True:
            query = gql("""
                query GetAllLocations($page: Int) {
                    locations(page: $page) {
                        info {
                            pages
                            next
                        }
                        results {
                            id
                            name
                            type
                            dimension
                            residents {
                                id
                            }
                        }
                    }
                }
            """)
            
            try:
                result = await self._execute_query(query, variable_values={"page": page})
                locations_data = result["locations"]["results"]
                
                for loc_data in locations_data:
                    location = self._parse_location(loc_data)
                    # Calculate resident count from IDs (no full details in list query)
                    resident_ids = loc_data.get("residents", [])
                    # Store empty list but we know the count from the response
                    location.residents = []  # Empty list, count calculated separately
                    # Store count as a temporary attribute for the router to use
                    location._resident_count = len(resident_ids)
                    all_locations.append(location)
                
                # Check if there are more pages
                info = result["locations"]["info"]
                if not info.get("next"):
                    break
                page += 1
                
            except Exception as e:
                logger.error(f"GraphQL error fetching locations page {page}: {e}")
                if page == 1:
                    raise
                break
        
        return all_locations
    
    async def get_locations_page(self, page: int) -> tuple[list[Location], int]:
        """Fetch a specific page of locations using GraphQL (without nested residents). Returns (locations, total_count)."""
        query = gql("""
            query GetLocationsPage($page: Int) {
                locations(page: $page) {
                    info {
                        pages
                        count
                        next
                    }
                    results {
                        id
                        name
                        type
                        dimension
                        residents {
                            id
                        }
                    }
                }
            }
        """)
        
        try:
            result = await self._execute_query(query, variable_values={"page": page})
            locations_data = result["locations"]["results"]
            info = result["locations"]["info"]
            total_count = info.get("count", 0)
            
            locations = []
            for loc_data in locations_data:
                location = self._parse_location(loc_data)
                # Calculate resident count from IDs (no full details in list query)
                resident_ids = loc_data.get("residents", [])
                location.residents = []  # Empty list, count calculated separately
                # Store count as a temporary attribute for the router to use
                location._resident_count = len(resident_ids)
                locations.append(location)
            
            return locations, total_count
        except Exception as e:
            logger.error(f"GraphQL error fetching locations page {page}: {e}")
            raise
    
    async def get_location(self, location_id: int) -> Location:
        """Fetch a specific location by ID."""
        query = gql("""
            query GetLocation($id: ID!) {
                location(id: $id) {
                    id
                    name
                    type
                    dimension
                    residents {
                        id
                        name
                        status
                        species
                        type
                        gender
                        origin {
                            name
                            id
                        }
                        location {
                            name
                            id
                        }
                        image
                        episode {
                            episode
                        }
                        created
                    }
                }
            }
        """)
        
        try:
            result = await self._execute_query(query, variable_values={"id": str(location_id)})
            loc_data = result["location"]
            if not loc_data:
                raise ValueError(f"Location {location_id} not found")
            
            location = self._parse_location(loc_data)
            if loc_data.get("residents"):
                location.residents = [
                    self._parse_character(res) for res in loc_data["residents"]
                ]
            
            return location
        except Exception as e:
            logger.error(f"GraphQL error fetching location {location_id}: {e}")
            raise
    
    async def get_character(self, character_id: int) -> Character:
        """Fetch a specific character by ID."""
        query = gql("""
            query GetCharacter($id: ID!) {
                character(id: $id) {
                    id
                    name
                    status
                    species
                    type
                    gender
                    origin {
                        name
                        id
                    }
                    location {
                        name
                        id
                    }
                    image
                    episode {
                        id
                        name
                        air_date
                        episode
                    }
                    created
                }
            }
        """)
        
        try:
            result = await self._execute_query(query, variable_values={"id": str(character_id)})
            char_data = result.get("character")
            if not char_data:
                raise ValueError(f"Character {character_id} not found")
            return self._parse_character(char_data)
        except Exception as e:
            logger.error(f"GraphQL error fetching character {character_id}: {e}")
            raise
    
    async def get_characters(self, character_ids: list[int]) -> list[Character]:
        """Fetch multiple characters by IDs."""
        if not character_ids:
            return []
        
        query = gql("""
            query GetCharacters($ids: [ID!]!) {
                charactersByIds(ids: $ids) {
                    id
                    name
                    status
                    species
                    type
                    gender
                    origin {
                        name
                        id
                    }
                    location {
                        name
                        id
                    }
                    image
                    episode {
                        id
                        name
                        air_date
                        episode
                    }
                    created
                }
            }
        """)
        
        try:
            result = await self._execute_query(query, variable_values={"ids": [str(cid) for cid in character_ids]})
            characters_data = result.get("charactersByIds", [])
            return [self._parse_character(char) for char in characters_data if char]
        except Exception as e:
            logger.error(f"GraphQL error fetching characters: {e}")
            raise
    
    async def get_all_characters(self) -> list[Character]:
        """Fetch all characters using GraphQL (without nested episodes)."""
        all_characters = []
        page = 1
        
        while True:
            query = gql("""
                query GetAllCharacters($page: Int) {
                    characters(page: $page) {
                        info {
                            pages
                            next
                        }
                        results {
                            id
                            name
                            status
                            species
                            type
                            gender
                            origin {
                                name
                                id
                            }
                            location {
                                name
                                id
                            }
                            image
                            episode {
                                episode
                            }
                            created
                        }
                    }
                }
            """)
            
            try:
                result = await self._execute_query(query, variable_values={"page": page})
                characters_data = result["characters"]["results"]
                all_characters.extend([self._parse_character(char) for char in characters_data if char])
                
                # Check if there are more pages
                info = result["characters"]["info"]
                if not info.get("next"):
                    break
                page += 1
                
            except Exception as e:
                logger.error(f"GraphQL error fetching characters page {page}: {e}")
                if page == 1:
                    raise
                break
        
        return all_characters
    
    async def get_characters_page(self, page: int) -> tuple[list[Character], int]:
        """Fetch a specific page of characters using GraphQL (without nested episodes). Returns (characters, total_pages)."""
        query = gql("""
            query GetCharactersPage($page: Int) {
                characters(page: $page) {
                    info {
                        pages
                        count
                        next
                    }
                    results {
                        id
                        name
                        status
                        species
                        type
                        gender
                        origin {
                            name
                            id
                        }
                        location {
                            name
                            id
                        }
                        image
                        episode {
                            episode
                        }
                        created
                    }
                }
            }
        """)
        
        try:
            result = await self._execute_query(query, variable_values={"page": page})
            characters_data = result["characters"]["results"]
            info = result["characters"]["info"]
            total_pages = info.get("pages", 1)
            total_count = info.get("count", 0)
            
            characters = [self._parse_character(char) for char in characters_data if char]
            return characters, total_count
        except Exception as e:
            logger.error(f"GraphQL error fetching characters page {page}: {e}")
            raise
    
    async def get_episodes(self) -> list[Episode]:
        """Fetch all episodes using GraphQL (without nested characters)."""
        all_episodes = []
        page = 1
        
        while True:
            query = gql("""
                query GetAllEpisodes($page: Int) {
                    episodes(page: $page) {
                        info {
                            pages
                            next
                        }
                        results {
                            id
                            name
                            air_date
                            episode
                            characters {
                                id
                            }
                        }
                    }
                }
            """)
            
            try:
                result = await self._execute_query(query, variable_values={"page": page})
                episodes_data = result["episodes"]["results"]
                
                for ep_data in episodes_data:
                    episode = self._parse_episode(ep_data)
                    # Calculate character count from IDs (no full details in list query)
                    character_ids = ep_data.get("characters", [])
                    episode._character_count = len(character_ids)
                    all_episodes.append(episode)
                
                # Check if there are more pages
                info = result["episodes"]["info"]
                if not info.get("next"):
                    break
                page += 1
                
            except Exception as e:
                logger.error(f"GraphQL error fetching episodes page {page}: {e}")
                if page == 1:
                    raise
                break
        
        return all_episodes
    
    async def get_episodes_page(self, page: int) -> tuple[list[Episode], int]:
        """Fetch a specific page of episodes using GraphQL (without nested characters). Returns (episodes, total_count)."""
        query = gql("""
            query GetEpisodesPage($page: Int) {
                episodes(page: $page) {
                    info {
                        pages
                        count
                        next
                    }
                    results {
                        id
                        name
                        air_date
                        episode
                        characters {
                            id
                        }
                    }
                }
            }
        """)
        
        try:
            result = await self._execute_query(query, variable_values={"page": page})
            episodes_data = result["episodes"]["results"]
            info = result["episodes"]["info"]
            total_count = info.get("count", 0)
            
            episodes = []
            for ep_data in episodes_data:
                episode = self._parse_episode(ep_data)
                # Calculate character count from IDs (no full details in list query)
                character_ids = ep_data.get("characters", [])
                episode._character_count = len(character_ids)
                episodes.append(episode)
            
            return episodes, total_count
        except Exception as e:
            logger.error(f"GraphQL error fetching episodes page {page}: {e}")
            raise
    
    async def get_episode(self, episode_id: int) -> Episode:
        """Fetch a specific episode by ID."""
        query = gql("""
            query GetEpisode($id: ID!) {
                episode(id: $id) {
                    id
                    name
                    air_date
                    episode
                    characters {
                        id
                        name
                        status
                        species
                        type
                        gender
                        origin {
                            name
                            id
                        }
                        location {
                            name
                            id
                        }
                        image
                        episode {
                            episode
                        }
                        created
                    }
                }
            }
        """)
        
        try:
            result = await self._execute_query(query, variable_values={"id": str(episode_id)})
            ep_data = result.get("episode")
            if not ep_data:
                raise ValueError(f"Episode {episode_id} not found")
            return self._parse_episode(ep_data)
        except Exception as e:
            logger.error(f"GraphQL error fetching episode {episode_id}: {e}")
            raise
    
    async def get_episodes_by_ids(self, episode_ids: list[int]) -> list[Episode]:
        """Fetch multiple episodes by IDs."""
        if not episode_ids:
            return []
        
        query = gql("""
            query GetEpisodes($ids: [ID!]!) {
                episodesByIds(ids: $ids) {
                    id
                    name
                    air_date
                    episode
                    characters {
                        id
                    }
                }
            }
        """)
        
        try:
            result = await self._execute_query(query, variable_values={"ids": [str(eid) for eid in episode_ids]})
            episodes_data = result.get("episodesByIds", [])
            return [self._parse_episode(ep) for ep in episodes_data if ep]
        except Exception as e:
            logger.error(f"GraphQL error fetching episodes: {e}")
            raise

