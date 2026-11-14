"""Local, append-oriented core for the CareOps improvement register."""

from .store import Register, RegisterError

__all__ = ["Register", "RegisterError"]
