from typing import List, Optional, Any, Dict
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlmodel import UUID, Relationship, SQLModel, Field, Column, String, TypeDecorator
from typing import Optional
import nanoid
from uuid import UUID as PyUUID
from datetime import datetime

def generate_nanoid() -> str:
    return nanoid.generate(size=12)

class Mission(SQLModel, table=True):
    id: str = Field(
        default_factory=generate_nanoid,
        sa_column=Column(String(12), primary_key=True, index=True, nullable=False),
    )
    title: str
    repo_url: str
    instruction: str
    room_id: Optional[str] = Field(default=None, index=True)
    user_id: str = Field(index=True)
    project_id: str = Field(index=True)
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None