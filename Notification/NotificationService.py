import json
import logging
import urllib.error
import urllib.request

import gi

gi.require_version('Notify', '0.7')
from gi.repository import Notify


# noinspection SpellCheckingInspection
class NotificationService:
	def __init__ (self):
		self.down_hosts = []

	def notify (self):
		if self.get_down_hosts():
			if self.down_hosts and len(self.down_hosts) > 0:
				self._notify_error()
			else:
				self._notify_success()
		else:
			self._notify_network_failure()

	def get_down_hosts (self):
		try:
			response = urllib.request.urlopen("http://localhost:3000/notify").read().decode('UTF-8')
			self.down_hosts = json.loads(response)["failed_hosts"]
			return True
		except urllib.error.URLError as msg:
			# noinspection PyAttributeOutsideInit
			self.failure_msg = msg.reason
			logging.error(msg.reason)
			return False

	def _notify_error (self):
		title = "[Pinger] " + str(len(self.down_hosts)) + " hosts are down"
		subtitle = "Hosts: "
		for host in self.down_hosts:
			subtitle += host + ", "
		subtitle += "are down!"
		Notify.init(title)
		notification = Notify.Notification.new(title, subtitle, "dialog-error")
		notification.show()

	# noinspection PyMethodMayBeStatic
	def _notify_success (self):
		title = "[Pinger] Success"
		subtitle = "All sites are working."
		Notify.init(title)
		notification = Notify.Notification.new(title, subtitle, "face-smile")
		notification.show()

	def _notify_network_failure (self):
		title = "[Pinger] Error occured"
		subtitle = str(self.failure_msg)
		Notify.init(title)
		notification = Notify.Notification.new(title, subtitle, "dialog-error")
		notification.show()
