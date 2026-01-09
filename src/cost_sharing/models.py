"""Data models for the Cost Sharing application"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class User:
    """User model representing a user in the system"""
    id: int
    email: str
    name: str


@dataclass
class Group:
    """Group model representing a cost-sharing group"""
    id: int
    name: str
    description: str
    created_by: User
    members: List[User]
