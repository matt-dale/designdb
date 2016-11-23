from __future__ import unicode_literals

from Projects.models import *
from Global_Equipment_library.models import *
from Labels.models import *

from django.db.models.signals import pre_save, post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.db.models import Q

from django.core.exceptions import ValidationError

"""
brings Projects and Equipment together to create project level equipment
"""

FONT_STYLES = (('regular', 'regular'),
                ('bold', 'bold'),
                ('italic', 'italic'),
                ('underline', 'underline'))

class ProjectEquipmentItem(models.Model):
    """
    same fields as a piece of equipment, but saved directly to 
    the project.  This allows overriding of certain fields.
    """
    project = models.ForeignKey(Project, related_name='project')
    globalEquipment = models.ForeignKey(GlobalEquipmentItem, related_name='global_equipment', blank=True, null=True)
    model = models.CharField(max_length=100, blank=True)
    equipmentType = models.ForeignKey(GlobalEquipmentCategory)
    manufacturer = models.ForeignKey(GlobalManufacturer, blank=True, null=True)
    hasMainLabel = models.BooleanField(default=True)
    qtyMainLabel = models.IntegerField(default=1)
    mainLabelSize = models.CharField(max_length=50, choices=LABEL_SIZES, default='Small')
    name = models.CharField(max_length=100, blank=True)
    # if the item is a cable or mult
    length = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return str(self.project) + ' ' +str(self.globalEquipment)

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
            pEI.project = project
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
    parentEquipment = models.ForeignKey(ProjectEquipmentItem, related_name='project_equipment_connection')
    connectionType = models.ForeignKey(GlobalConnection, related_name='project_connection_type')
    name = models.CharField(max_length=100)
    matesWith = models.ManyToManyField(GlobalConnection, related_name='project_mates_with', blank=True)
    defaultLabelSize = models.CharField(max_length=50, choices=LABEL_SIZES, default='Small')

    def __unicode__(self):
        return str(self.parentEquipment.name) + '-' +self.name


    @classmethod
    def buildConnectionsFromEquipmentItem(cls, globalItem, pEI, **kwargs):
        """
        automatically builds the connections from the globalItem defaults
        pEI is the parent equipment instance, probably given to this function from
        buildProjectEquipmentItem classmethod.   
        """
        connections = globalItem.globalequipmentconnection_set.all()
        for connection in connections:
            settings = pEI.project.projectSettingsProject.all()[0]
            pEC = cls()
            pEC.parentEquipment = pEI
            pEC.connectionType = connection.connectionType
            pEC.name = connection.name
            pEC.defaultLabelSize = connection.connectionType.defaultLabelSize
            pEC.save()
            for x in connection.matesWith.all():
                pEC.matesWith.add(x)
                    # create the equipment's connection labels
            if pEC.defaultLabelSize == 'Large':
                labelTemplate = settings.largeLabelTemplate
            elif pEC.defaultLabelSize == 'Small':
                labelTemplate = settings.smallLabelTemplate
            elif pEC.defaultLabelSize == 'Medium':
                labelTemplate = settings.mediumLabelTemplate
            newConLabel = ProjectEquipmentConnectionLabel.objects.create(theConnection=pEC, labelTemplate=labelTemplate)
            nCTB = ProjectEquipmentConnectionLabelTextBox.objects.create(parentLabelObject=newConLabel, text=pEC.name)




"""
Label Explanation:
    Labels have templates seen in Labels.models that hold information
    regarding size, and name
    Labels can have LabelTextBoxes that actually hold the text and styling
    of the label text
    The following models are only used to relate Label Templates and Textboxes 
    to actual equipment pieces and connections
"""

class ProjectEquipmentLabel(models.Model):
    """
    every equipment item gets its own label
    """
    theEquipment = models.ForeignKey(ProjectEquipmentItem, related_name='theEquipment')
    labelTemplate = models.ForeignKey(LabelTemplate, related_name='labelTemplate')

    def getTextBoxes(self):
        """
        returns all children text boxes
        """
        return ProjectEquipmentLabelTextBox.objects.filter(parentLabelObject=self)

        
class ProjectEquipmentLabelTextBox(LabelTextBox):
    """
    hold the actual text and details for the text on the label
    """
    parentLabelObject = models.ForeignKey(ProjectEquipmentLabel, related_name='ParentProjectEquipmentLabel')


class ProjectEquipmentConnectionLabel(models.Model):
    """
    each connection gets a Label instance created for it.
    This allows overriding the default label outputs on a per Label basis.
    """
    theConnection = models.ForeignKey(ProjectEquipmentConnection, related_name='ProjectEquipmentConnectionForLabel')
    labelTemplate = models.ForeignKey(LabelTemplate, related_name='label_template')

    def getTextBoxes(self):
        """
        returns all text boxes that are children of this label
        """
        return ProjectEquipmentConnectionLabelTextBox.objects.filter(parentLabelObject=self)


class ProjectEquipmentConnectionLabelTextBox(LabelTextBox):
    """
    This holds each piece of text on the label.
    Inherited from Labels.models
    """
    parentLabelObject = models.ForeignKey(ProjectEquipmentConnectionLabel, related_name='ParentProjectEquipmentConnectionLabel')



@receiver(post_save, sender=ProjectEquipmentItem)
def presaveProjectEquipmentHandler(sender, instance, created, *args, **kwargs):
    """
    this autocreates the labels for the piece of equipment
    """
    if created == True:
        # create the labels for the equipment
        # get the template from the project settings
        settings = instance.project.projectSettingsProject.all()[0]
        if instance.hasMainLabel == True:
            newLabel = ProjectEquipmentLabel(theEquipment=instance)
            if instance.mainLabelSize == 'Large':
                newLabel.labelTemplate = settings.largeLabelTemplate
            elif instance.mainLabelSize == 'Small':
                newLabel.labelTemplate = settings.smallLabelTemplate
            elif instance.mainLabelSize == 'Medium':
                newLabel.labelTemplate = settings.mediumLabelTemplate
            elif instance.mainLabelSize == 'Custom':
                pass
            newLabel.save()
            # create a text box
            nT = ProjectEquipmentLabelTextBox.objects.create(parentLabelObject=newLabel, text=instance.name)



class ProjectEquipmentPatchPoint(models.Model):
    """
    describes the connection between one item to another
    uses some validation to make sure the two can be mated.
    """
    connectionA = models.ForeignKey(ProjectEquipmentConnection, related_name='connectionA')
    connectionB = models.ForeignKey(ProjectEquipmentConnection, related_name='connectionB')

    def __unicode__(self):
        return self.connectionA + '-' + self.connectionB

    def save(self, *args, **kwargs):
        """
        validates that the connection can be made with the mateswith field,
        also determines if there is already a patch made to the connection B
        """
        # first determine if connection B already has a patch point
        #projectEquipment = ProjectEquipment.objects.filter(project=self.connectionA.parentEquipment.project)
        #connections = ProjectEquipmentConnection.objects.filter(parentEquipment__in=projectEquipment)
        patchPoints = ProjectEquipmentPatchPoint.objects.filter(
            Q(connectionA=self.connectionA)|Q(connectionB=self.connectionB)|Q(connectionB=self.connectionA)|Q(connectionA=self.connectionB))
        if patchPoints.count() > 0:
            validationText = 'Patching Error: '
            i = patchPoints[0]
            validationText += '{0} is already patched to {1}'.format(str(i.connectionA), str(i.connectionB))
            raise ValidationError(validationText)
        # now determine if these things can be patched together
        if self.connectionA.connectionType not in self.connectionB.matesWith.all():
            validationText = "{0} can't be patched with {1}".format(str(self.connectionA.connectionType), str(self.connectionB.connectionType))
            raise ValidationError(validationText) 
        else:
            super(ProjectEquipmentPatchPoint, self).save(*args, **kwargs) # Call the "real" save() method.