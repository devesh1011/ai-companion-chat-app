from fastapi import WebSocket
from typing import Dict, List
import json
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ConnectionInfo(BaseModel):
    """Stores metadata about a connected client"""

    session_id: str
    username: str
    character_id: str
    websocket: WebSocket
    connected_at: datetime
    websocket: WebSocket
    model_config = ConfigDict(arbitrary_types_allowed=True)


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, ConnectionInfo] = {}

    async def connect(
        self,
        session_id: str,
        username: str,
        character_id: str,
        websocket: WebSocket,
    ) -> None:
        """
        Register a new WebSocket connection

        Args:
            session_id: Unique session identifier
            username: User's unique ID
            character_id: AI character's unique ID
            websocket: The WebSocket connection object
        """
        connection_info = ConnectionInfo(
            session_id=session_id,
            username=username,
            character_id=character_id,
            websocket=websocket,
            connected_at=datetime.now(),
        )

        self.active_connections[session_id] = connection_info

    def disconnect(self, session_id: str) -> None:
        """
        Remove a WebSocket connection from the registry

        Args:
            session_id: Session identifier to disconnect
        """
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            print(f"✗ Client disconnected: session={session_id}")

    def get_connection(self, session_id: str) -> ConnectionInfo | None:
        """
        Get connection info by session ID

        Args:
            session_id: Session identifier

        Returns:
            ConnectionInfo if found, None otherwise
        """
        return self.active_connections.get(session_id)

    def get_connections_by_character(self, character_id: str) -> List[ConnectionInfo]:
        """
        Get all active connections for a specific character
        (useful if multiple users are chatting with same character)

        Args:
            character_id: Character's unique ID

        Returns:
            List of ConnectionInfo objects for this character
        """
        return [
            conn
            for conn in self.active_connections.values()
            if conn.character_id == character_id
        ]

    async def send_personal_message(
        self,
        session_id: str,
        message: dict | str,
    ) -> bool:
        """
        Send a message to a specific session

        Args:
            session_id: Target session identifier
            message: Message to send (dict or JSON string)

        Returns:
            True if sent successfully, False if connection not found
        """
        connection_info = self.get_connection(session_id)

        if not connection_info:
            print(f"⚠ Connection not found for session: {session_id}")
            return False

        try:
            # Convert dict to JSON if needed
            if isinstance(message, dict):
                message = json.dumps(message)

            await connection_info.websocket.send_text(message)
            return True
        except Exception as e:
            print(f"✗ Error sending message to {session_id}: {str(e)}")
            # Remove connection if sending failed
            self.disconnect(session_id)
            return False

    async def send_to_user(
        self,
        username: str,
        character_id: str,
        message: dict | str,
    ) -> bool:
        """
        Send a message to a specific user chatting with a specific character

        Args:
            username: Target user's ID
            character_id: AI character's ID
            message: Message to send

        Returns:
            True if sent successfully, False otherwise
        """
        for conn in self.active_connections.values():
            if conn.username == username and conn.character_id == character_id:
                return await self.send_personal_message(conn.session_id, message)

        print(
            f"⚠ No active connection found for user={username}, character={character_id}"
        )
        return False

    def get_active_connections_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)

    def get_active_connections_info(self) -> List[dict]:
        """Get info about all active connections (for monitoring/debugging)"""
        return [
            {
                "session_id": conn.session_id,
                "username": conn.username,
                "character_id": conn.character_id,
                "connected_at": conn.connected_at.isoformat(),
            }
            for conn in self.active_connections.values()
        ]


# Global instance (singleton)
manager = ConnectionManager()
