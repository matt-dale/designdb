from django.test import TestCase
from Global_Equipment_library.models import *
from Project_Equipment.models import *

def buildSomeEquipment():
    """
    a function to populate the database
    this will be used in the setup for the tests
    """
    categories = ['Cable', 'Amplifiers', 'Signal Processing', 'Communications']
    manufacturer = GlobalManufacturer.objects.create(name='Masque Sound')
    
    for x in categories:
        c = GlobalEquipmentCategory.objects.create(description=x)

    xlrMale = GlobalConnection.objects.create(connectionType='cable mount',
                                                connectionName='XLR',
                                                gender = 'Male')
    xlrFemale = GlobalConnection.objects.create(connectionType='cable mount',
                                                connectionName='XLR',
                                                gender = 'Female')

    xlr = GlobalEquipmentItem.objects.create(description = 'XLR Cable',
                                        equipmentType = GlobalEquipmentCategory.objects.get(description='Cable'),
                                        manufacturer = GlobalManufacturer.objects.all()[0],
                                        model = 'XLR Cable')

    xlrConA = GlobalEquipmentConnection.objects.create(parentEquipment = xlr,
                                            connectionType = xlrMale,
                                            name = 'xlr male')
    xlrConA.matesWith.add(xlrFemale)
    xlrConA.save()

    xlrConB = GlobalEquipmentConnection.objects.create(parentEquipment = xlr,
                                            connectionType = xlrFemale,
                                            name = 'xlr female')
    xlrConB.matesWith.add(xlrMale)
    xlrConB.save()




class ProjectEquipmentTest(TestCase):
    def setUp(self):
        buildSomeEquipment()
        u = User.objects.create(username='a', password='Django!@#$', email='a@a.com')
        venue = Venue.objects.create(name='Masque Sound', streetAddress='21 E Union Ave', country='US', state='NJ')
        self.project = Project.objects.create(owner=u, venue=venue, description='test project')

    def testCreateProjectEquipment(self):
        result = True
        try:
            e = GlobalEquipmentItem.objects.get(description='XLR Cable')
            pEI = ProjectEquipmentItem.buildProjectEquipmentItem(self.project, e)
        except:
            result = False
        self.assertEqual(result, True)

    def testCreateProjectEquipmentConnections(self):
        e = GlobalEquipmentItem.objects.get(description='XLR Cable')
        pEI = ProjectEquipmentItem.buildProjectEquipmentItem(self.project, e)
        cons = pEI.project_equipment_connection.all()
        if cons.count() == 2:
            result =  True
        else:
            result = False
            print cons
        self.assertEqual(result, True)

    def testProjectEquipmentPatchPoints(self):
        """
        create some equipment then connections. 
        create a patch point between two connections.
        """
        e = GlobalEquipmentItem.objects.get(description='XLR Cable')
        xlrA = ProjectEquipmentItem.buildProjectEquipmentItem(self.project, e)
        xlrA.name = 'xlrA'
        xlrA.save()
        xlrB = ProjectEquipmentItem.buildProjectEquipmentItem(self.project, e)
        xlrB.name = 'xlrB'
        xlrB.save()
        xlrC = ProjectEquipmentItem.buildProjectEquipmentItem(self.project, e)
        xlrC.name = 'xlrC'
        xlrC.save()
        aToB = ProjectEquipmentPatchPoint.objects.create(connectionA=xlrA.project_equipment_connection.all()[0], 
                                                        connectionB=xlrB.project_equipment_connection.all()[1])
        aToC = ProjectEquipmentPatchPoint(connectionA=xlrA.project_equipment_connection.all()[0],
                                           connectionB=xlrC.project_equipment_connection.all()[1])
        try: 
            aToC.save()
        except ValidationError:
            return True
        else:
            return False

    def testProjectEquipmentPatchPointMatesWith(self):
        """
        create some equipment then connections. 
        create a patch point between two connections.
        """
        e = GlobalEquipmentItem.objects.get(description='XLR Cable')
        xlrA = ProjectEquipmentItem.buildProjectEquipmentItem(self.project, e)
        xlrA.name = 'xlrA'
        xlrA.save()
        xlrB = ProjectEquipmentItem.buildProjectEquipmentItem(self.project, e)
        xlrB.name = 'xlrB'
        xlrB.save()
        try: 
            aToB = ProjectEquipmentPatchPoint.objects.create(connectionA=xlrA.project_equipment_connection.all()[0], 
                                                        connectionB=xlrB.project_equipment_connection.all()[0])
        
        except ValidationError:
            return True
        else:
            return False