"""Database service for interacting with Supabase."""
import os
import logging
from typing import Optional, Dict, Any
from supabase import create_client, Client
from backend.config import SUPABASE_URL, SUPABASE_ANON_KEY

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    """Get a Supabase client instance."""
    try:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        return client
    except Exception as e:
        logger.error(f"Error initializing Supabase client: {e}")
        raise

class DatabaseService:
    def __init__(self):
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Supabase client: {e}")
            raise

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile from the database."""
        try:
            response = self.supabase.table("user_profiles").select("*").eq("id", user_id).single().execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None

    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile in the database."""
        try:
            response = self.supabase.table("user_profiles").update(updates).eq("id", user_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False

    def save_spreadsheet_id(self, user_id: str, spreadsheet_id: str) -> bool:
        """Save Google Sheets spreadsheet ID for a user."""
        try:
            updates = {"spreadsheet_id": spreadsheet_id}
            return self.update_user_profile(user_id, updates)
        except Exception as e:
            logger.error(f"Error saving spreadsheet ID: {e}")
            return False

    def get_spreadsheet_id(self, user_id: str) -> Optional[str]:
        """Get Google Sheets spreadsheet ID for a user."""
        try:
            profile = self.get_user_profile(user_id)
            if profile:
                return profile.get("spreadsheet_id")
            return None
        except Exception as e:
            logger.error(f"Error getting spreadsheet ID: {e}")
            return None