import os
from typing import Optional

class Settings:
    """Application settings"""
    
    # Supabase settings
    SUPABASE_URL: str = "https://szsolezkvaccxqkclrket.supabase.co"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN6c29lenZrYWNjeHFrY2xya2V0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ3MTc3MTYsImV4cCI6MjA3MDI5MzcxNn0.SJmXw6GtXzzAB9eCoFMsNun7aI4pc_CHs-jM0OQffWQ"
    
    # API settings
    API_TITLE: str = "Persona API"
    API_DESCRIPTION: str = "API for managing personas"
    API_VERSION: str = "1.0.0"
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS settings
    ALLOWED_ORIGINS: list = ["*"]  # Configure properly for production
    
    def validate_required_settings(self) -> None:
        """Validate that required settings are present"""
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is required")
        if not self.SUPABASE_ANON_KEY:
            raise ValueError("SUPABASE_ANON_KEY is required")

# Create global settings instance
settings = Settings()
