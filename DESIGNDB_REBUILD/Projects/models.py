from __future__ import unicode_literals

from django.contrib.auth.models import User

from django.db import models

"""
This app combines the Global_Equipment_library with a Project
"""

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
    streetAddress2 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)

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


class ProjectPermissionGroup(models.Model):
    """
    Used to handle access to projects.  
    The groups will be auto-created when a project is created.
    """
    parentProject = models.ForeignKey(Project)
    permissionType = models.CharField(max_length=100, default='Read-only')

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