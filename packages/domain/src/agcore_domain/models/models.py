from typing import List, Optional, Any, Dict
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlmodel import UUID, Relationship, SQLModel, Field, Column, String, TypeDecorator
from typing import Optional
import nanoid
from uuid import UUID as PyUUID

def generate_nanoid():
    return nanoid.generate(size=12)

class ProjectBrainPileLink(SQLModel, table=True):
    project_id: Optional[str] = Field(
        default=None, foreign_key="project.id", primary_key=True
    )
    pile_id: Optional[PyUUID] = Field(
        default=None, foreign_key="brainpile.id", primary_key=True
    )

class ProjectUserLink(SQLModel, table=True):
    project_id: Optional[str] = Field(
        default=None, foreign_key="project.id", primary_key=True
    )
    user_id: Optional[PyUUID] = Field(
        default=None, foreign_key="user.id", primary_key=True, index=True
    )
    role: str = Field(default="guest", sa_column=Column(String(20), nullable=False))

class UserConfig(SQLModel):
    default_project_id: Optional[str] = None

class UserConfigDecorator(TypeDecorator):
    impl = JSONB
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.model_dump()
    def process_result_value(self, value, dialect):
        if value is None:
            return UserConfig()
        return UserConfig.model_validate(value)

class User(SQLModel, table=True):
    id: Optional[PyUUID] = Field(default=None, primary_key=True)
    name: str
    config: UserConfig = Field(
        default_factory=UserConfig, 
        sa_column=Column(UserConfigDecorator)
    )
    projects: List["Project"] = Relationship(
        back_populates="users",
        link_model=ProjectUserLink,
    )
    piles: List["BrainPile"] = Relationship(back_populates="creator")

class ProjectConfig(SQLModel):
    description: Optional[str] = "no description"

class ProjectConfigDecorator(TypeDecorator):
    impl = JSONB
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.model_dump()
    def process_result_value(self, value, dialect):
        if value is None:
            return ProjectConfig()
        return ProjectConfig.model_validate(value)

class Project(SQLModel, table=True):
    id: str = Field(
        default_factory=generate_nanoid,
        sa_column=Column(String(12), primary_key=True, index=True, nullable=False),
    )
    title: str
    description: Optional[str] = None
    config: ProjectConfig = Field(
        default_factory=ProjectConfig, 
        sa_column=Column(ProjectConfigDecorator)
    )
    piles: List["BrainPile"] = Relationship(
        back_populates="projects",
        link_model=ProjectBrainPileLink,
    )
    users: List["User"] = Relationship(
        back_populates="projects",
        link_model=ProjectUserLink,
    )


class BrainPileTagLink(SQLModel, table=True):
    pile_id: Optional[PyUUID] = Field(
        default=None, foreign_key="brainpile.id", primary_key=True
    )
    tag_id: Optional[int] = Field(
        default=None, foreign_key="brainpiletag.id", primary_key=True
    )

class BrainPileTag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    piles: List["BrainPile"] = Relationship(
        back_populates="tags",
        link_model=BrainPileTagLink,
    )
    
class BrainPile(SQLModel, table=True):
    id: Optional[PyUUID] = Field(default=None, primary_key=True)
    title: str = "unnamed brain pile"
    is_archived: bool = False
    is_public: bool = False
    tags: List["BrainPileTag"] = Relationship(
        back_populates="piles",
        link_model=BrainPileTagLink,
    )
    projects: List["Project"] = Relationship(
        back_populates="piles",
        link_model=ProjectBrainPileLink,
    )
    drops: List["BrainDrop"] = Relationship(back_populates="pile")
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
