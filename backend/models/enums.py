"""
SYRA AI - Enumeration Types
Module: backend/models/enums.py

String enumerations used across request/response schemas.
"""

from enum import Enum


class TaskMode(str, Enum):
    QA = "qa"
    SUMMARIZATION = "summarization"
    CLASSIFICATION = "classification"


class Provider(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"


class PromptType(str, Enum):
    BASIC = "basic"
    IMPROVED = "improved"
    CONTEXT_GROUNDED = "context_grounded"
    BULLET_POINTS = "bullet_points"
    CUSTOM = "custom"
