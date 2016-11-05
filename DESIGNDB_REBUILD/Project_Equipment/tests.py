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

    # Test of creating an image and adding it to a global equipment item

    anImage = GlobalEquipmentBlockDiagramImage.objects.create(blockImage='test-svgwrite.svg')

    galileo = GlobalEquipmentItem.objects.create(description = 'Galileo 616',
                                        equipmentType = GlobalEquipmentCategory.objects.get(description='Signal Processing'),
                                        manufacturer = GlobalManufacturer.objects.all()[0],
                                        model = 'Galileo 616',
                                        blockDiagramImage=anImage)

    xlrFPanel = GlobalConnection.objects.create(connectionType='panel mount',
                                                connectionName='XLR Female Panel Mount',
                                                gender = 'Female')

    xlrMPanel = GlobalConnection.objects.create(connectionType='panel mount',
                                                connectionName='XLR Male Panel Mount',
                                                gender = 'Male')

    galileoA = GlobalEquipmentConnection.objects.create(parentEquipment = galileo,
                                            connectionType = xlrFPanel,
                                            name = 'Input A')
    galileoA.matesWith.add(xlrMale)
    galileoA.save()

    galileoB = GlobalEquipmentConnection.objects.create(parentEquipment = galileo,
                                            connectionType = xlrFPanel,
                                            name = 'Input B')
    galileoB.matesWith.add(xlrMale)
    galileoB.save()

    galileoC = GlobalEquipmentConnection.objects.create(parentEquipment = galileo,
                                            connectionType = xlrFPanel,
                                            name = 'Input C')
    galileoC.matesWith.add(xlrMale)
    galileoC.save()

    galileoD = GlobalEquipmentConnection.objects.create(parentEquipment = galileo,
                                            connectionType = xlrFPanel,
                                            name = 'Input D')
    galileoD.matesWith.add(xlrMale)
    galileoD.save()

    galileoE = GlobalEquipmentConnection.objects.create(parentEquipment = galileo,
                                            connectionType = xlrFPanel,
                                            name = 'Input E')
    galileoE.matesWith.add(xlrMale)
    galileoE.save()

    galileoF = GlobalEquipmentConnection.objects.create(parentEquipment = galileo,
                                            connectionType = xlrFPanel,
                                            name = 'Input F')
    galileoF.matesWith.add(xlrMale)
    galileoF.save()

    outputs = 16
    for x in range(1, outputs):
        num = str(x)
        w = GlobalEquipmentConnection.objects.create(parentEquipment=galileo,
                                                connectionType = xlrMPanel,
                                                name = 'Output '+num)
        w.matesWith.add(xlrFemale)
        w.save()




class ProjectEquipmentTest(TestCase):
    def setUp(self):
        buildSomeEquipment()
        u = User.objects.create(username='a', password='Django!@#$', email='a@a.com')
        venue = Venue.objects.create(name='Masque Sound', streetAddress='21 E Union Ave', country='US', state='NJ')
        self.project = Project.objects.create(owner=u, venue=venue, description='test project')

    def testCreateProjectEquipment(self):
        result = True
        #try:
        e = GlobalEquipmentItem.objects.get(description='XLR Cable')
        pEI = ProjectEquipmentItem.buildProjectEquipmentItem(self.project, e)
        #except:
        result = False
        #self.assertEqual(result, True)

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
        # this connection pairing only works becuase they are all the same type.  the .all() index won't normally work reliably
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