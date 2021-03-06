from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Database.LogModel import Base, LogModel


# noinspection SpellCheckingInspection
class Database:
	def __init__ (self):
		self.engine = create_engine('sqlite:///pinger.db')
		Base.metadata.create_all(self.engine)
		dbsession = sessionmaker(bind=self.engine)
		self.session = dbsession()

	def log (self, date, hosts, log, failed_hosts=None):
		model = LogModel(date=date, hosts=hosts, log=log, failed_hosts=failed_hosts)
		self.session.add(model)
		self.session.commit()
