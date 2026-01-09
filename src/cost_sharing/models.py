"""Data models for the Cost Sharing application"""

from dataclasses import dataclass


@dataclass
class User:
    """User model representing a user in the system"""
    id: int
    email: str
    name: str


@dataclass
class GroupInfo:
    """Group information model for listing user's groups"""
    id: int
    name: str
    description: str
    member_count: int
