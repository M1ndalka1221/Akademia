"""Forms for the learning application."""

from typing import Any
from django import forms
from learning.models import Essay


class EssayForm(forms.ModelForm):
    """Form for writing and submitting Polish essays."""

    class Meta:
        model = Essay
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": (
                        "w-full p-4 border border-slate-300 dark:border-slate-700 rounded-xl "
                        "focus:ring-2 focus:ring-indigo-500 focus:border-transparent "
                        "bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 "
                        "font-sans shadow-sm transition-all duration-200"
                    ),
                    "rows": 12,
                    "placeholder": "Napisz swój esej po polsku tutaj...",
                }
            ),
        }
        labels = {
            "content": "Treść Eseju (Essay Content)",
        }
