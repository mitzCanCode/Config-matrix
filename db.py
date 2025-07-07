from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Define the database URL (SQLite database stored in a file)
DATABASE_URL = "sqlite:///computers.db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)  # Set echo=False in production

# Create a base class for model definitions
Base = declarative_base()

# Association table: Profiles <-> Apps
profile_app_association = Table(
    'profile_app_association',
    Base.metadata,
    Column('profile_id', Integer, ForeignKey('profiles.id')),
    Column('app_id', Integer, ForeignKey('apps.id'))
)

# Association table: Computers <-> Apps
computer_app_association = Table(
    'computer_app_association',
    Base.metadata,
    Column('computer_id', Integer, ForeignKey('computers.id')),
    Column('app_id', Integer, ForeignKey('apps.id'))
)

class Computers(Base):
    __tablename__ = 'computers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    deadline = Column(Date)
    profile_id = Column(Integer, ForeignKey('profiles.id'))

    profile = relationship("Profiles", back_populates="computers")
    downloaded_apps = relationship(
        "Apps", secondary=computer_app_association, back_populates="downloaded_by"
    )

class Profiles(Base):
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    apps_to_download = relationship(
        "Apps", secondary=profile_app_association, back_populates="profiles"
    )
    computers = relationship("Computers", back_populates="profile")

class Apps(Base):
    __tablename__ = 'apps'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    download_link = Column(String)  
    
    profiles = relationship(
        "Profiles", secondary=profile_app_association, back_populates="apps_to_download"
    )
    downloaded_by = relationship(
        "Computers", secondary=computer_app_association, back_populates="downloaded_apps"
    )

# Create the tables in the database
Base.metadata.create_all(engine)

# Set up session to interact with the DB
Session = sessionmaker(bind=engine)
session = Session()
