from __future__ import unicode_literals

from django.contrib.auth.models import User

from django.db import models
from Labels.models import *
from django.db.models.signals import pre_save, post_save, post_delete, pre_delete
from django.dispatch import receiver

"""
This app combines the Global_Equipment_library with a Project
"""

PERM_GROUPS = [('owner','owner'),
                ('admin','admin'),
                ('read', 'read'),
                ('write', 'write')]


class Venue(models.Model):
    """
    if each show is assigned to a venue, we can collect data about each venue
    for others to use.

    Should a tour be a "venue" for designers to select with a bogus address? Or should
    we make "tour stop" model?
    """
    name = models.CharField(max_length=300)
    country = models.CharField(max_length=10)
    streetAddress = models.CharField(max_length=200)
    streetAddress2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return self.name


class Project(models.Model):
    """
    the highest level parent to all the rest of the work that happens in designdb
    """
    description = models.CharField(max_length=200)
    owner = models.ForeignKey(User)
    venue = models.ForeignKey(Venue, related_name='venue')

    def __unicode__(self):
        return self.description


class ProjectSettings(models.Model):
    """
    holds defaults for things like labels, etc.
    """
    BUNDLES = [('Bundle', 'Bundle'),
            ('Loom', 'Loom'),
            ('Multicore', 'Multicore')]
    project = models.ForeignKey(Project, related_name='projectSettingsProject')
    smallLabelTemplate = models.ForeignKey(LabelTemplate, related_name='small_label_template')
    largeLabelTemplate = models.ForeignKey(LabelTemplate, related_name='large_label_template')
    mediumLabelTemplate = models.ForeignKey(LabelTemplate, related_name='medium_label_template')
    bundlesLoomsMulticore = models.CharField(max_length=50, choices=BUNDLES, default='Bundle') # this will be used heavily to "translate" between bundles/looms/multicores in templates
    UIStyle = models.CharField(max_length=25, choices=(('Standard', 'Standard'), ('Dark', 'Dark')), default='Standard')
    lengthUnits = models.CharField(max_length=20, choices=(('feet', 'feet'), ('meters', 'meters')), default='feet')
    tagBundleEnds = models.BooleanField(default=False)


@receiver(post_save, sender=Project)
def postSaveProject(sender, instance, created, *args, **kwargs):
    """
    this autocreates the settings object for the project
    """
    if created == True:
        s = ProjectSettings()
        small, created = LabelTemplate.objects.get_or_create(name='Avery 5167')
        large, created = LabelTemplate.objects.get_or_create(name='Avery 5160')
        s.project = instance
        s.smallLabelTemplate = small
        s.largeLabelTemplate = large
        s.mediumLabelTemplate = large
        s.save()
        # assign an Project Owner with admin access to the project
        ppg = ProjectPermissionGroup.objects.create(parentProject=instance, permissionType='owner')
        ppgm = ProjectPermissionGroupMember.objects.create(permissionGroup=ppg, user=instance.owner)
    return


class ProjectEmployee(models.Model):
    """
    used to hold titles and names of people working on the project.
    TODO: A post_save method will link users to this project to gain read-only access to the project
    """
    project = models.ForeignKey(Project)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=100)
    emailAddress = models.EmailField(max_length=200, blank=True)

    def __unicode__(self):
        return self.firstName + ' ' + self.title


class ProjectPermissionGroup(models.Model):
    """
    Used to handle access to projects.  
    The groups will be auto-created when a project is created.
    """
    parentProject = models.ForeignKey(Project)
    permissionType = models.CharField(max_length=100, choices=PERM_GROUPS, default='read')

    def __unicode__(self):
        return self.parentProject.description + ' ' + self.permissionType


class ProjectPermissionGroupMember(models.Model):
    """
    self-explanatory - this model is used to handle 
    adding permissions to a project
    Need to limit one user per permission - 
        when changing perms, if elevating from read-only to read/write, remove the read-only permission

    test this 
    """
    permissionGroup = models.ForeignKey(ProjectPermissionGroup, related_name='permission_group')
    user = models.ForeignKey(User, related_name='user')

    def __unicode__(self):
        return self.permissionGroup + '--' + self.user


def checkUserProjectPermission(user, project):
    """
    returns a project permission or None
    """
    groups = ProjectPermissionGroup.objects.filter(parentProject=project)
    permissionGroups = ProjectPermissionGroupMember.objects.filter(permissionGroup__in=groups, user=user)
    if permissionGroups.count() > 0:
        if permissionGroups.count() > 1:
            raise ValueError('This user has too many permissions for this project. There is a programming error.')
        else:
            return permissionGroups[0]
    else:
        return None