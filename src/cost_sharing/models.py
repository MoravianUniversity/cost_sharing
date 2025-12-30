"""Data models for the Cost Sharing application"""

from dataclasses import dataclass


@dataclass
class User:
    """User model representing a user in the system"""
    id: int
    email: str
    name: str
    oauth_provider_id: str
