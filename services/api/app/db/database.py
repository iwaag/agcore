import os
from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine, select

from models.models import BrainDrop, BrainPile, Project, ProjectUserLink, UserConfig, UserConfig, User



SQL_TYPE = os.getenv("SQL_TYPE")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_HOST = os.getenv("SQL_HOST")
SQL_PORT = os.getenv("SQL_PORT")
SQL_DB = os.getenv("SQL_DB")
sql_url = f"{SQL_TYPE}://{SQL_USER}:{SQL_PASSWORD}@{SQL_HOST}:{SQL_PORT}/{SQL_DB}"
engine = create_engine(sql_url)
SQLModel.metadata.create_all(engine)

def get_user_config(user_id: str):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if user is None:
            raise ValueError(f"User with id {user_id} not found")
        return user.config

def set_user_config(user_id: str, user_config: UserConfig):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if user is None:
            user = User(id=user_id, config=user_config)
            session.add(user)
        else:
            user.config = user_config
            session.add(user)
            session.commit()

def new_project(creator_user_id: str, title:str) -> Project:
    new_project = Project(title=title)
    with Session(engine) as session:
        session.add(new_project)
        session.flush()
        link = ProjectUserLink(project_id=new_project.id, user_id=creator_user_id, role="admin")
        session.add(link)
        session.commit()
        session.refresh(new_project)
        return new_project

def list_projects() -> list[Project]:
    with Session(engine) as session:
        return session.exec(select(Project)).all()

def set_project_title(project_id:str, title:str) -> None:
    with Session(engine) as session:
        project = session.get(Project, project_id)
        project.title = title
        session.add(project)

def new_brain_pile(title:str, project_id:str) -> BrainPile:
    new_pile = BrainPile(title=title)
    new_pile.projects.append(project_id)
    with Session(engine) as session:
        session.add(new_pile)
        session.commit()
        session.refresh(new_pile)
        return new_pile

def remove_brain_pile(pile_id: str) -> None:
    with Session(engine) as session:
        pile = session.get(BrainPile, pile_id)
        session.delete(pile)
        session.commit()


def add_brain_drop(pile_id: str, title:str, content_url: str) -> None:
    new_drop= BrainDrop(title=title, content_resource_id=content_url, pile_id=pile_id)
    with Session(engine) as session:
        session.add(new_drop)
        session.commit()
        session.refresh(new_drop)
        return new_drop
    
def remove_brain_drop(drop_id: str) -> None:
    with Session(engine) as session:
        drop = session.get(BrainDrop, drop_id)
        session.delete(drop)
        session.commit()


def set_brain_drop_content(drop_id: str, content_url: str) -> None:
    with Session(engine) as session:
        drop = session.get(BrainDrop, drop_id)
        drop.content_resource_id = content_url
        session.add(drop)
        session.commit()