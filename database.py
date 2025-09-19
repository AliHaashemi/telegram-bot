import os
from supabase import create_client, Client

class SupabaseDB:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)
    
    def save_conversation(self, user_id: int, message: str, response: str):
        data = {
            "user_id": user_id,
            "message": message,
            "response": response
        }
        self.supabase.table("conversations").insert(data).execute()
    
    def get_user_history(self, user_id: int, limit: int = 5):
        response = self.supabase.table("conversations") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return response.data
