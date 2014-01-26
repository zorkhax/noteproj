from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    content = models.CharField(max_length=200, blank=False, default='Nothing')
    in_history = models.BooleanField(default=False)
    user = models.ForeignKey(User, blank=False)
    edit_date = models.DateTimeField('date published')

    def __unicode__(self):
        return self.content
