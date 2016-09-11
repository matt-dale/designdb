from django.test import TestCase
from Projects.models import *

class ProjectTest(TestCase):
    
    def setUp(self):
        self.u1 = User.objects.create(username='another', password='Django!@#$', email='a@a.com')
        self.u2 = User.objects.create(username='bee', password='Django!@#$', email='b@a.com')
        venue = Venue.objects.create(name='Masque Sound', streetAddress='21 E Union Ave', country='US', state='NJ')
        self.project = Project.objects.create(owner=self.u1, venue=venue, description='test project')

    def testThatSettingsExist(self):
        if self.project.projectSettingsProject.all().count() == 1:
            results = True
        else:
            results = False
        self.assertEqual(results, True)

    def testOwnerPermissions(self):
        permGroup = checkUserProjectPermission(self.u1, self.project)
        self.assertEqual(permGroup.permissionGroup.permissionType, 'owner')

    def testNoPermissions(self):
        permGroup = checkUserProjectPermission(self.u2, self.project)
        self.assertEqual(permGroup, None)