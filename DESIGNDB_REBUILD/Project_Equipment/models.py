from __future__ import unicode_literals

from Projects.models import *
from Global_Equipment_library.models import *
from Labels.models import *

"""
brings Projects and Equipment together to create project level equipment
"""


class ProjectEquipmentItem(models.Model):
    """
    same fields as a piece of equipment, but saved directly to 
    the project.  This allows overriding of certain fields.
    """
    project = models.ForeignKey(Project, related_name='project')
    globalEquipment = models.ForeignKey(GlobalEquipmentItem, related_name='global_equipment', blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    equipmentType = models.ForeignKey(GlobalEquipmentCategory)
    manufacturer = models.ForeignKey(GlobalManufacturer, blank=True, null=True)
    hasMainLabel = models.BooleanField(default=True)
    qtyMainLabel = models.IntegerField(default=1)
    mainLabelSize = models.CharField(max_length=50, choices=LABEL_SIZES, default='Small')

    def __unicode__(self):
        return self.project + self.globalEquipment

    @classmethod
    def buildProjectEquipmentItem(cls, project, globalItem=None, **kwargs):
        """
        use this class method to create an item simply. 
        if globalItem is not provided, raise an exception because 
        more details are needed for that.
        acceptable keys in kwargs are field names with cleaned values
        """
        if globalItem == None:
            raise ValueError('Cannot create a ProjectEquipmentItem with this classmethod. Please create it manually.')
        else:
            pEI = cls()
            # set the defaults
            pEI.globalEquipment = globalItem
            pEI.model = globalItem.model
            pEI.equipmentType = globalItem.equipmentType
            pEI.manufacturer = globalItem.manufacturer
            pEI.hasMainLabel = globalItem.hasMainLabel
            pEI.qtyMainLabel = globalItem.qtyMainLabel
            pEI.mainLabelSize = globalItem.mainLabelSize

            overriddenFields = kwargs
            for field, value in overriddenFields.items():
                pEI.field = value

            pEI.save()
            ProjectEquipmentConnection.buildConnectionsFromEquipmentItem(globalItem, pEI)
            return pEI



class ProjectEquipmentConnection(models.Model):
    """
    copies the global equipment connections, but allows overriding of both labels and connection types.
    """
    parentEquipment = models.ForeignKey(ProjectEquipmentItem, related_name='parent_equipment')
    connectionType = models.ForeignKey(GlobalConnection, related_name='connection_type')
    name = models.CharField(max_length=100)
    matesWith = models.ForeignKey(GlobalConnection, related_name='mates_with', null=True, blank=True)
    defaultLabelSize = models.CharField(max_length=50, choices=LABEL_SIZES, default='Small')

    def __unicode__(self):
        return self.parentEquipment + self.name

    @classmethod
    def buildConnectionsFromEquipmentItem(cls, globalItem, pEI, **kwargs):
        """
        automatically builds the connections from the globalItem defaults
        pEI is the parent equipment instance, probably given to this function from
        buildProjectEquipmentItem classmethod.   
        """
        try:
            connections = globalItem.GlobalEquipmentConnection_set.all()
            for connection in connections:
                pEC = cls()
                pEC.parentEquipment = pEI
                pEC.connectionType = connection.connectionType
                pEC.name = connection.name
                pEC.matesWith = connection.matesWith
                pEC.defaultLabelSize = connection.connectionType.defaultLabelSize
                pEC.save()
            return True
        except:
            return False


class ProjectEquipmentConnectionLabel(models.Model):
    """
    each connection gets a Label instance created for it.
    This allows overriding the default label outputs on a per Label basis.
    """
    theConnection = models.ForeignKey(ProjectEquipmentConnection, related_name='connection')
    labelTemplate = models.ForeignKey(LabelTemplate, related_name='label_template')
