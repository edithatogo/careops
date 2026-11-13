"""Synthetic, offline registration-assurance core. No live provider or SoCP authority."""
from .assurance import assess_engagement_coverage, assess_observation, reconcile_observations

__all__ = ["assess_engagement_coverage", "assess_observation", "reconcile_observations"]
