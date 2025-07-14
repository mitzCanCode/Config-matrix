from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Define the database URL (SQLite database stored in a file)
DATABASE_URL = "sqlite:///computers.db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)  # Set echo=False in production

# Create a base class for model definitions
Base = declarative_base()

# Association table: Profiles <-> SetupSteps
profile_step_association = Table(
    'profile_step_association',
    Base.metadata,
    Column('profile_id', Integer, ForeignKey('profiles.id')),
    Column('step_id', Integer, ForeignKey('setup_steps.id'))
)

# Association table: Computers <-> SetupSteps
computer_step_association = Table(
    'computer_step_association',
    Base.metadata,
    Column('computer_id', Integer, ForeignKey('computers.id')),
    Column('step_id', Integer, ForeignKey('setup_steps.id'))
)

# Association table: Computers <-> Technicians (many-to-many)
computer_technician_association = Table(
    'computer_technician_association',
    Base.metadata,
    Column('computer_id', Integer, ForeignKey('computers.id')),
    Column('technician_id', Integer, ForeignKey('technicians.id'))
)

class Technicians(Base):
    __tablename__ = 'technicians'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)

    # Many-to-many relationship with computers
    assigned_computers = relationship(
        "Computers", secondary=computer_technician_association, back_populates="technicians"
    )
    
    # Keep the old one-to-many relationship for backward compatibility (deprecated)
    computers = relationship("Computers", back_populates="technician")

class Computers(Base):
    __tablename__ = 'computers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    deadline = Column(DateTime)
    profile_id = Column(Integer, ForeignKey('profiles.id'), nullable=True)
    technician_id = Column(Integer, ForeignKey('technicians.id'), nullable=True)  # Keep for backward compatibility
    notes = Column(String, nullable=True)

    profile = relationship("Profiles", back_populates="computers")
    
    # Many-to-many relationship with technicians
    technicians = relationship(
        "Technicians", secondary=computer_technician_association, back_populates="assigned_computers"
    )
    
    # Keep the old one-to-many relationship for backward compatibility (deprecated)
    technician = relationship("Technicians", back_populates="computers")
    
    setup_steps = relationship(
        "SetupSteps", secondary=computer_step_association, back_populates="completed_by"
    )

class Profiles(Base):
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    setup_steps_to_follow = relationship(
        "SetupSteps", secondary=profile_step_association, back_populates="profiles"
    )
    computers = relationship("Computers", back_populates="profile")

class SetupSteps(Base):
    __tablename__ = 'setup_steps'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    download_link = Column(String)  
    
    profiles = relationship(
        "Profiles", secondary=profile_step_association, back_populates="setup_steps_to_follow"
    )
    completed_by = relationship(
        "Computers", secondary=computer_step_association, back_populates="setup_steps"
    )

# Create the tables in the database
Base.metadata.create_all(engine)

# Set up session to interact with the DB
Session = sessionmaker(bind=engine)
session = Session()
