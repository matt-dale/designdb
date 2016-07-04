from __future__ import unicode_literals

from django.db import models
from Global_Equipment_library.models import LABEL_SIZES

class LabelTemplate(models.Model):
    """
    used to keep track of Label types, 
    like Avery 5160, 5167 or the Australian labels and custom labels
    """
    name = models.CharField(max_length=100)
    size = models.CharField(max_length=10, choices=LABEL_SIZES)

    def __unicode__(self):
        return self.name

