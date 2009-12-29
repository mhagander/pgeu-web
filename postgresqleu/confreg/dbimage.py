import base64
from django.db import connection, transaction

from django.core.files.storage import Storage
from django.core.files import File

class SpeakerImageStorage(Storage):
	def __init__(self):
		pass

	def _open(self, name, mode='rb'):
		curs = connection.cursor()
		curs.execute("SELECT photo FROM confreg_speaker_photo WHERE id=%(id)s", {
			'id': name,
		})
		rows = curs.fetchall()
		if len(rows) != 1:
			return None
		return File(base64.b64decode(rows[0][0]))

	def _save(self, name, content):
		content.seek(0)
		curs = connection.cursor()
		params = {
			'id': name,
			'photo': base64.b64encode(content.read()),
		}
		curs.execute("UPDATE confreg_speaker_photo SET photo=%(photo)s WHERE id=%(id)s", params)
		if curs.rowcount == 0:
			curs.execute("INSERT INTO confreg_speaker_photo (id, photo) VALUES (%(id)s, %(photo)s)", params)
		transaction.commit_unless_managed()
		return name

	def exists(self, name):
		print "Exists vcheck for '%s'" % name
		return False

	def get_available_name(self, name):
		print "Get available name '%s' called" % name
		return name

	def delete(self, name):
		curs = connection.cursor()
		curs.execute("DELETE FROM confreg_speaker_photo WHERE id=%(id)s" % {'id': name})
		transaction.commit_unless_managed()

	def url(self, name):
		return "/events/speaker/%s/photo/" % name

	def size(self, name):
		return None

	def path(self):
		return None


from django.forms.widgets import Widget
from django.utils.safestring import mark_safe

class InlinePhotoWidget(Widget):
	def render(self, name, value, attrs=None):
		return mark_safe(u'<img src="data:image/png;base64,%s"/>' % value)

	def value_from_datadict(self, data, files, name):
		return self.original_value

