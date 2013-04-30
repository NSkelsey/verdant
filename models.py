from sqlalchemy import *

from sqlalchemy.ext.declarative import declarative_base

sql_url = 'sqlite:///' + os.getcwd() + '/digest.db'
Base = declarative_base()


engine = create_engine(sql_url, echo=True)
session = scoped_session(sessionmaker(bind=engine,
                                      autoflush=False,
                                      autocommit=False,))

class Hexdigest(Base):
    used_digest = Column(String)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
