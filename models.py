import os
from sqlalchemy import *
from sqlalchemy.orm import (
        sessionmaker, 
        relationship,
        scoped_session,
        backref,
        )
from sqlalchemy.ext.declarative import declarative_base

sql_url = 'sqlite:///' + os.getcwd() + '/digest.db'
Base = declarative_base()


engine = create_engine(sql_url, echo=True)
session = scoped_session(sessionmaker(bind=engine,
                                      autoflush=False,
                                      autocommit=False,))

class EmailMessage(Base):
    __tablename__ = "email_message"
    hexdigest = Column(String, primary_key=True)
    everything = Column(String, )
    approved = Column(Boolean)
    
    def __init__(self, everything):
        self.everything = everything
        self.approved = False
    
if __name__ == "__main__":
    Base.metadata.create_all(engine)
