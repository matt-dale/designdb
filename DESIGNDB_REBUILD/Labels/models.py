from __future__ import unicode_literals

from django.db import models
from Global_Equipment_library.models import LABEL_SIZES

FONT_TYPES = [('Impact','Impact'),
                ('Palatino','Palatino'),
                ('Tahoma','Tahoma'),
                ('Century Gothic', 'Century Gothic'),
                ('Lucida Sans Unicode', 'Lucida Sans Unicode'),
                ('Arial Black', 'Arial Black'),
                ('Times New Roman', 'Times New Roman'),
                ('Arial Narrow', 'Arial Narrow'),
                ('Verdana', 'Verdana'),
                ('Copperplate', 'Copperplate'),
                ('Lucida Console', 'Lucida Console'),
                ('Gill Sans', 'Gill Sans'),
                ('Trebuchet MS', 'Trebuchet MS'),
                ('Courier', 'Courier'),
                ('Arial', 'Arial')]

class LabelTemplate(models.Model):
    """
    used to keep track of Label types, 
    like Avery 5160, 5167 or the Australian labels and custom labels
    """
    name = models.CharField(max_length=100, unique=True)
    size = models.CharField(max_length=10, choices=LABEL_SIZES)

    def __unicode__(self):
        return self.name

class LabelTextBox(models.Model):
    """
    a generic text box that allows settings to be overridden
    """
    text = models.CharField(max_length=100, blank=True)
    font = models.CharField(max_length=100, choices=FONT_TYPES)
    bold = models.BooleanField(default=False)
    italic = models.BooleanField(default=False)
    underline = models.BooleanField(default=False)
    fontSize = models.IntegerField(default=12)
    xPoint = models.IntegerField(default=0)
    yPoint = models.IntegerField(default=0)

    def __unicode__(self):
        return self.text


