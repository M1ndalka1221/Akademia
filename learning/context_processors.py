"""Context processors for the Learning application."""

from typing import Any, Dict
from django.http import HttpRequest
from learning.models import calculate_learning_streak


def learning_streak(request: HttpRequest) -> Dict[str, Any]:
    """Inject active learning streak count into template context."""
    user = getattr(request, "user", None)
    streak_days = calculate_learning_streak(user=user)
    return {
        "streak_days": streak_days
    }
