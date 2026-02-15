from typing import Any, Optional

import nanoid
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlmodel import Column, Field, Relationship, SQLModel
from uuid import UUID as PyUUID


def generate_nanoid() -> str:
    return nanoid.generate(size=12)


class UserConfig(SQLModel):
    default_project_id: Optional[str] = None


class ProjectConfig(SQLModel):
    default_background: Optional[str] = None


class ProjectBrainPileLink(SQLModel, table=True):
    project_id: Optional[str] = Field(
        default=None,
        foreign_key="project.id",
        primary_key=True,
    )
    pile_id: Optional[PyUUID] = Field(
        default=None,
        foreign_key="brainpile.id",
        primary_key=True,
    )


class ProjectUserLink(SQLModel, table=True):
    project_id: Optional[str] = Field(
        default=None,
        foreign_key="project.id",
        primary_key=True,
    )
    user_id: Optional[PyUUID] = Field(
        default=None,
        foreign_key="user.id",
        primary_key=True,
    )
    role: str = Field(
        default="guest",
        sa_column=Column(String(20), nullable=False),
    )


class User(SQLModel, table=True):
    id: Optional[PyUUID] = Field(default=None, primary_key=True)
    name: str

    # JSONB column should store plain JSON-serializable dict/list/values.
    config: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(MutableDict.as_mutable(JSONB), nullable=False),
    )

    projects: list["Project"] = Relationship(
        back_populates="users",
        link_model=ProjectUserLink,
    )
    piles: list["BrainPile"] = Relationship(back_populates="creator")


class Project(SQLModel, table=True):
    id: str = Field(
        default_factory=generate_nanoid,
        sa_column=Column(String(12), primary_key=True, index=True, nullable=False),
    )
    title: str
    description: Optional[str] = None

    # JSONB + MutableDict works best when Python-side value is dict.
    config: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(MutableDict.as_mutable(JSONB), nullable=False),
    )

    piles: list["BrainPile"] = Relationship(
        back_populates="projects",
        link_model=ProjectBrainPileLink,
    )
    users: list["User"] = Relationship(
        back_populates="projects",
        link_model=ProjectUserLink,
    )


class BrainPileTagLink(SQLModel, table=True):
    pile_id: Optional[PyUUID] = Field(
        default=None,
        foreign_key="brainpile.id",
        primary_key=True,
    )
    tag_id: Optional[int] = Field(
        default=None,
        foreign_key="brainpiletag.id",
        primary_key=True,
    )


class BrainPileTag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    piles: list["BrainPile"] = Relationship(
        back_populates="tags",
        link_model=BrainPileTagLink,
    )


class BrainPile(SQLModel, table=True):
    id: Optional[PyUUID] = Field(default=None, primary_key=True)
    title: str = "unnamed brain pile"
    is_archived: bool = False
    is_public: bool = False

    tags: list["BrainPileTag"] = Relationship(
        back_populates="piles",
        link_model=BrainPileTagLink,
    )
    projects: list["Project"] = Relationship(
        back_populates="piles",
        link_model=ProjectBrainPileLink,
    )
    drops: list["BrainDrop"] = Relationship(back_populates="pile")

    creator_id: Optional[PyUUID] = Field(default=None, foreign_key="user.id")
    creator: Optional[User] = Relationship(back_populates="piles")
    origin: Optional[PyUUID] = Field(default=None, foreign_key="brainpile.id")


class BrainDrop(SQLModel, table=True):
    id: Optional[PyUUID] = Field(default=None, primary_key=True)
    title: str = "unnamed brain drop"
    content_resource_id: Optional[str] = None

    pile_id: Optional[PyUUID] = Field(default=None, foreign_key="brainpile.id")
    pile: Optional[BrainPile] = Relationship(back_populates="drops")

    @property
    def is_archived(self) -> bool:
        return self.pile.is_archived
