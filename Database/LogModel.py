from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# noinspection SpellCheckingInspection
class LogModel(Base):
	__tablename__ = 'Log'
	id = Column(Integer, primary_key=True)
	date = Column(String(250), nullable=False)
	hosts = Column(String(), nullable=False)
	failed_hosts = Column(String(), nullable=True)
	log = Column(String(), nullable=False)
