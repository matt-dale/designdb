from django.test import TestCase
from Projects.models import *

class ProjectTest(TestCase):
    
    def setUp(self):
        self.u1 = User.objects.create(username='a', password='Django!@#$', email='a@a.com')
        self.u2 = User.objects.create(username='a', password='Django!@#$', email='b@a.com')
        venue = Venue.objects.create(name='Masque Sound', streetAddress='21 E Union Ave', country='US', state='NJ')
        self.project = Project.objects.create(owner=u, venue=venue, description='test project')


