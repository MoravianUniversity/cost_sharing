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


# R0902 indicates too many instance variables but we need it to match the database schema
@dataclass
class Expense:  # pylint: disable=R0902
    """Expense model representing an expense in a group"""
    id: int
    group_id: int
    description: str
    amount: float
    date: str
    paid_by: User
    split_between: List[User]
    per_person_amount: float = None
