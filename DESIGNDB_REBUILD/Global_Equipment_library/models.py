from __future__ import unicode_literals

from django.db import models

"""
PYTHON 2.7.10, please

This app provides the base templates for all objects that are created or used in designdb project.
"""

LABEL_SIZES = [('Small', 'Small'),
                ('Medium', 'Medium'),
                ('Large', 'Large'),
                ('Custom', 'Custom')]

class GlobalManufacturer(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


class GlobalEquipmentCategory(models.Model):
    """
    """
    description = models.CharField(max_length=100)

    def __unicode__(self):
        return self.description

class GlobalConnection(models.Model):
    """
    represents the various types of connections possible
    XLR, Ethercon, RJ45, etc. just connector types
    """
    connectionType = models.CharField(max_length=100) #panel mount or cable mount
    connectionName = models.CharField(max_length=100) # XLR, NL4 etc.
    gender = models.CharField(max_length=50) # male, female or neither
    defaultLabelSize = models.CharField(max_length=50, choices=LABEL_SIZES, default='Small')

    def __unicode__(self):
        return self.name


class GlobalEquipmentItem(models.Model):
    """
    This is the template that will be used when adding a piece of equipment to 
    a project.  
    Cables are pieces of equipment.
    """
    description = models.CharField(max_length=200)
    equipmentType = models.ForeignKey(GlobalEquipmentCategory)
    manufacturer = models.ForeignKey(GlobalManufacturer, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True)
    # the following fields could be placed in a separate Attributes table
    hasMainLabel = models.BooleanField(default=True)
    qtyMainLabel = models.IntegerField(default=1)
    mainLabelSize = models.CharField(max_length=50, choices=LABEL_SIZES, default='Small') # how do we deal with custom label templates? 

    def __unicode__(self):
        if self.manufacturer:
            return self.manufacturer.name+' '+self.description
        else:
            return self.description


class GlobalEquipmentConnection(models.Model):
    """
    represents the type and gender of a piece of equipment
    """
    parentEquipment = models.ForeignKey(GlobalEquipmentItem)
    connectionType = models.ForeignKey(GlobalConnection, related_name='connection_type')
    name = models.CharField(max_length=100)
    matesWith = models.ManyToManyField(GlobalConnection, related_name='mates_with')

    def __unicode__(self):
        return self.parentEquipment.description+' '+self.connectionType.name
