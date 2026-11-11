from .session import SessionFactory
from .setup import setup_database

InternalSession = SessionFactory()
ExternalSession = SessionFactory()
UnifiedSession  = SessionFactory()

__all__ = ["InternalSession", "ExternalSession", "UnifiedSession", "setup_database"]
