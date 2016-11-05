# pdfLabelPrinter
import labels as labelPrinter
from reportlab.graphics import shapes
from reportlab.pdfbase.pdfmetrics import registerFont, stringWidth
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()
style = styles["Normal"]

import os
from pdfrw import PdfReader, PdfWriter
import random
from reportlab.lib import colors
from decimal import Decimal

from designDb.models import Label

"""
PRINT SETTINGS TODO:
Small Label Template 
Large Label Template
Default font

"""

"""
writer = PdfWriter()

files = [x for x in os.listdir('mypdfs') if x.endswith('.pdf')]
for fname in sorted(files):
  writer.addpages(PdfReader(os.path.join('mypdfs', fname)).pages)

writer.write("output.pdf")


p = Paragraph(text, style=preferred_style)
width, height = p.wrapOn(self.canvas, aW, aH)
p.drawOn(self.canvas, x_pos, y_pos)

1Point = 0.352778 mm
"""


class DesignDbLabelPrinter(object):
    """
    determines the label type and creates the PDFs for each product type,
    then concatenates the PDFs into one, and deletes the others.
    """

    def __init__(self, project):
        self.pointsToMM = Decimal(0.352778) # 1 point = this many mm
        self.project = project
        self.settings = project.projectsettings_set.all()[0]
        self.small5167 = labelPrinter.Specification(215.9, 279.4, 4, 20, 44.45, 12.7, 
                                    left_margin=7.35, 
                                    column_gap=7.94, row_gap=0, 
                                    top_margin=12, corner_radius=1)

        self.large5160 = labelPrinter.Specification(215.9, 279.4, 3, 10, 66.675, 25.4, 
                            left_margin=4.7625, 
                            left_padding=2,
                            right_padding=2,
                            column_gap=3.175, row_gap=0, 
                            top_margin=12.3, corner_radius=1)

        self.oneBlock5160 = labelPrinter.Specification(279.4, 215.9, 10, 3, 25.4, 66.675,  
                            left_margin=12.3, 
                            left_padding=2,
                            right_padding=2,
                            column_gap=0, row_gap=3.175, 
                            top_margin=4.7625, corner_radius=1)

        self.fonts = ['Helvetica', 'Times', 'Courier']
        if self.settings.font in self.fonts:
            self.font = self.settings.font
        else:
            self.font = 'Helvetica'

        if self.settings.smallLabelTemplate == 'Avery 5167':
            self.smallSpecs = self.small5167

        if self.settings.largeLabelTemplate == 'Avery 5160':
            self.largeSpecs = self.large5160

        self.drawBorder = False

        self.tagEnds = self.settings.tagBundleEnds
        base_path = os.getcwd() + '/printJobs/printjob_'+str(self.project.id)+'_'+str(random.randrange(1,1000))+'/'
        os.mkdir(base_path)
        self.printdirectory = base_path
        self.smallSheets = []
        self.largeSheets = []
        self.smallPageCount = 0
        self.largePageCount = 0

    def draw_aux_label(self, label, width, height, obj):
        """
        just fill the label with the text
        """
        fontSize = 22
        if width > 127:
            fontSize = 40
        textWidth = stringWidth(obj, self.font, fontSize)
        while textWidth > (width - 10):
            fontSize *= 0.5
            textWidth = stringWidth(obj, self.font, fontSize)
        label.add(shapes.String(width/2.0, height-(fontSize+fontSize/5.0), obj, textAnchor="middle", fontSize=fontSize))

    def draw_cable_label(self, label, width, height, obj):
        """
        Split the label into 4 quads, calculate the maximum size that the 
        main center label can be.  
        """
        topLeft = str(obj[0])
        bottomLeft = str(obj[1])
        topRight = str(obj[2])
        bottomRight = str(obj[3])
        middleCenter = str(obj[4])
        bottomCenter = str(obj[5])
        isBundle = obj[6]
        largeOrSmall = obj[7]
        font = self.font
        fillColor = colors.HexColor("#00000")
        if isBundle == True:
            if self.tagEnds == True:
                fillColor = colors.HexColor("#FFFFFF")
                r = shapes.Rect(0, 0, width, height)
                r.fillColor = colors.HexColor("#00000")
                r.strokeColor = None
                label.add(r)
        horizontalCenterLine = width/2.0
        verticalCenterLine = height/2.0

        if largeOrSmall == 'Large':
            largeFontSize = 32
            smallFontSize = 10
        elif largeOrSmall == 'Small':
            largeFontSize = 22
            smallFontSize = 7

        middleCenterTextWidth = stringWidth(middleCenter, font, largeFontSize) # start with large font size of 22
        middleCenterTextHeight = largeFontSize*self.pointsToMM

        leftVerticalLimit = verticalCenterLine - middleCenterTextWidth/2.0
        rightVerticalLimit = verticalCenterLine + middleCenterTextWidth/2.0

        label.add(shapes.String(5, height-smallFontSize, topLeft, fontName=font, fontSize=smallFontSize, fillColor=fillColor))
        label.add(shapes.String(2, 2, bottomLeft, fontName=font, fontSize=smallFontSize, fillColor=fillColor))
        name_width = stringWidth(topRight, font, smallFontSize)
        label.add(shapes.String(width-(name_width+2), height-smallFontSize, topRight, fontName=font, fontSize=smallFontSize, fillColor=fillColor))
        name2_width = stringWidth(bottomRight, font, smallFontSize)
        label.add(shapes.String(width-(name2_width+2), 2, bottomRight, fontName=font, fontSize=smallFontSize, fillColor=fillColor))
        if largeOrSmall == 'Large':
            label.add(shapes.String(width/2.0, height-(largeFontSize+largeFontSize/2.0), middleCenter, textAnchor="middle", fontSize=largeFontSize, fillColor=fillColor))
        elif largeOrSmall == 'Small':
            label.add(shapes.String(width/2.0, height-(largeFontSize+largeFontSize/5.0), middleCenter, textAnchor="middle", fontSize=largeFontSize, fillColor=fillColor))

    def draw_oneBlock_label(self, label, width, height, obj):
        """
        Split the label into 4 quads, calculate the maximum size that the 
        main center label can be.  
        """
        topLeft = str(obj[0])
        bottomLeft = str(obj[1])
        topRight = str(obj[2])
        bottomRight = str(obj[3])
        middleCenter = str(obj[4])
        bottomCenter = str(obj[5])
        isBundle = obj[6]
        largeOrSmall = obj[7]
        font = self.font
        fillColor = colors.HexColor("#00000")
        if isBundle == True:
            if self.tagEnds == True:
                fillColor = colors.HexColor("#FFFFFF")
                r = shapes.Rect(0, 0, width, height)
                r.fillColor = colors.HexColor("#00000")
                r.strokeColor = None
                label.add(r)
        horizontalCenterLine = width/2.0
        verticalCenterLine = height/2.0

        if largeOrSmall == 'Large':
            largeFontSize = 28
            smallFontSize = 8
        if largeOrSmall == 'OneBlock':
            largeFontSize = 20
            smallFontSize = 7
        elif largeOrSmall == 'Small':
            largeFontSize = 22
            smallFontSize = 7

        topLeftText = shapes.String(5, height-smallFontSize, topLeft, fontName=font, fontSize=smallFontSize, fillColor=fillColor)
        label.add(topLeftText)

        bottomLeftText = shapes.String(2, height-height/3.0+smallFontSize, bottomLeft, fontName=font, fontSize=smallFontSize, fillColor=fillColor)
        label.add(bottomLeftText)

        topLeftTextWidth = stringWidth(topLeft, font, smallFontSize)

        topRightText = shapes.String(width-(topLeftTextWidth+2), height-smallFontSize, topRight, fontName=font, fontSize=smallFontSize, fillColor=fillColor)
        label.add(topRightText)

        bottomLeftTextWidth = stringWidth(bottomLeft, font, smallFontSize)

        bottomRightText = shapes.String(width-(bottomLeftTextWidth+2), height-height/3.0, bottomRight, fontName=font, fontSize=smallFontSize, fillColor=fillColor)
        label.add(bottomRightText)

        middleTextWidth = stringWidth(middleCenter, font, largeFontSize)
        if len(middleCenter) > 4:
            topFour = middleCenter[0:4]
            bottomFour = middleCenter[4:8]
        if len(middleCenter) > 8:
            lowFour = middleCenter[8:]
        else:
            topFour = middleCenter
            bottomFour = ''
            lowFour = ''

        middleText = shapes.String(2, (height-height/4.0)+2.0, middleCenter, fontSize=largeFontSize, fillColor=fillColor)
        label.add(middleText)
    
    def save_cable_sheet(self, labelsToPrint, smallOrLarge):
        cables = labelsToPrint
        if smallOrLarge == 'Small':
            sheet = labelPrinter.Sheet(self.smallSpecs, self.draw_cable_label, border=self.drawBorder)
        elif smallOrLarge == 'Large':
            sheet = labelPrinter.Sheet(self.largeSpecs, self.draw_cable_label, border=self.drawBorder)
        elif smallOrLarge == 'OneBlock':
            sheet = labelPrinter.Sheet(self.oneBlock5160, self.draw_oneBlock_label, border=self.drawBorder)

        for cable in cables:
            # loop through twice, first for origin, second for destination
            #cableType = topLeft
            topLeft = str(cable.cable.cableType) +' '+ str(cable.length)
            try:
                bottomLeft = str(cable.getOriginGender())+'@'+cable.origin.locationDescription
            except:
                bottomLeft = str(cable.getOriginGender())
            if cable.aBundle != None:
                bottomRight = cable.aBundle.name
                aBundle = True
            else:
                bottomRight = ''
                aBundle = False
            if smallOrLarge == 'OneBlock':
                name = cable.code
            else:
                if len(cable.cableName) > 11:
                    name = cable.code
                else:
                    name = cable.cableName
            data = [topLeft, bottomLeft, '', bottomRight, name, '', aBundle, smallOrLarge]
            sheet.add_label(data)
        
        # add a label break here. Origins Up here, Destinations down here 
        # we should pad the row so that it works for both template types
        # pad the row until it is a new row
        currentPosition = sheet._position # returns [row#, column#]

        if smallOrLarge == 'Small':
            columnCount = self.smallSpecs.columns
        elif smallOrLarge == 'Large':
            columnCount = self.largeSpecs.columns
        elif smallOrLarge == 'OneBlock':
            columnCount = self.largeSpecs.columns
        # if the current column# doesn't equal the amount of columns, pad out the labels
        while currentPosition[1] != columnCount:
            sheet.add_label(['','','','','','','', smallOrLarge])
            currentPosition = sheet._position
        if smallOrLarge == 'Small' or smallOrLarge == 'Large':
            sheet.add_label(['','','','','Origin Above', '', '', smallOrLarge])
            sheet.add_label(['','','','','__Destination__', '', '', smallOrLarge])
            sheet.add_label(['','','','','Labels Below', '', '', smallOrLarge])
            if smallOrLarge == 'Small':
                if self.settings.smallLabelTemplate == 'Avery 5167':
                    sheet.add_label(['','','','','','','', smallOrLarge])

        for cable in cables:
            # loop through twice, first for origin, second for destination
            #cableType = topLeft
            topLeft = str(cable.cable.cableType) + str(cable.length)
            try:
                bottomLeft = str(cable.getDestinationGender())+'@'+cable.destination.locationDescription
            except:
                bottomLeft = str(cable.getDestinationGender())
            if cable.aBundle != None:
                bottomRight = cable.aBundle.name
            else:
                bottomRight = ''
            if smallOrLarge == 'OneBlock':
                name = cable.code
            else:
                if len(cable.cableName) > 11:
                    name = cable.code
                else:
                    name = cable.cableName
            aBundle = False
            data = [topLeft, bottomLeft, '', bottomRight, name, '', aBundle, smallOrLarge]
            sheet.add_label(data)

        if smallOrLarge == 'Large':
            theSheet = self.printdirectory+'03'+smallOrLarge+'CableLabels.pdf'
            self.largeCableLabels = theSheet
            self.largeSheets.append(theSheet)
            self.largePageCount += sheet.page_count
            
        if smallOrLarge == 'OneBlock':
            theSheet = self.printdirectory+'04'+smallOrLarge+'CableLabels.pdf'
            self.largeCableLabels = theSheet
            #self.largeSheets.append(theSheet)
            self.largePageCount += sheet.page_count
            
        elif smallOrLarge == 'Small':
            theSheet = self.printdirectory+'00'+smallOrLarge+'CableLabels.pdf'
            self.smallSheets.append(theSheet)
            self.smallCableLabels = theSheet
            self.smallPageCount += sheet.page_count
            

        sheet.save(theSheet)
        return sheet

    def draw_breakout_tail_label(self, label, width, height, obj):
        """
        Split the label into 4 quads, calculate the maximum size that the 
        main center label can be.  
        """
        topLeft = str(obj[0])
        bottomLeft = str(obj[1])
        topRight = str(obj[2])
        bottomRight = str(obj[3])
        middleCenter = str(obj[4])
        bottomCenter = str(obj[5])

        font = self.font
        fillColor = colors.HexColor("#00000")

        largeFontSize = 22
        smallFontSize = 7

        label.add(shapes.String(5, height-smallFontSize, topLeft, fontName=font, fontSize=smallFontSize, fillColor=fillColor))
        label.add(shapes.String(2, 2, bottomLeft, fontName=font, fontSize=smallFontSize, fillColor=fillColor))
        name_width = stringWidth(topRight, font, smallFontSize)
        label.add(shapes.String(width-(name_width+2), height-smallFontSize, topRight, fontName=font, fontSize=smallFontSize, fillColor=fillColor))
        name2_width = stringWidth(bottomRight, font, smallFontSize)
        label.add(shapes.String(width-(name2_width+2), 2, bottomRight, fontName=font, fontSize=smallFontSize, fillColor=fillColor))
        label.add(shapes.String(width/2.0, height-(largeFontSize+largeFontSize/5.0), middleCenter, textAnchor="middle", fontSize=largeFontSize, fillColor=fillColor))
        label.add(shapes.String(width/2.0, 2, bottomCenter, textAnchor="middle", fontSize=smallFontSize))

    def save_breakout_sheet(self, labelsToPrint):
        breakouts = labelsToPrint

        SmallSheetHeads = labelPrinter.Sheet(self.smallSpecs, self.draw_cable_label, border=self.drawBorder)

        LargeSheetHeads = labelPrinter.Sheet(self.largeSpecs, self.draw_cable_label, border=self.drawBorder)

        BreakoutTailSheet = labelPrinter.Sheet(self.smallSpecs, self.draw_breakout_tail_label, border=self.drawBorder)

        OneBlockSheet = labelPrinter.Sheet(self.oneBlock5160, self.draw_oneBlock_label, border=self.drawBorder)
        # create lists of various things to print

        # first print small label heads
        smallLabelHeads = []
        # then print large label heads
        largeLabelHeads = []
        # then print male breakout tails
        maleBreakoutTails = []
        # then print female breakout tails
        femaleBreakoutTails = []

        for breakout in breakouts:
            if breakout.cableBreakout.mainLabelType == Label.objects.get(description__icontains='5167'):
                smallLabelHeads.append(breakout)
            if breakout.cableBreakout.mainLabelType == Label.objects.get(description__icontains='5160'):
                largeLabelHeads.append(breakout)
            breakoutTails = breakout.projectcablebreakoutpair_set.all()
            if 'Male' in breakout.cableBreakout.gender:
                maleBreakoutTails.append(breakoutTails)
            if 'Female' in breakout.cableBreakout.gender:
                femaleBreakoutTails.append(breakoutTails)
        """
        topLeft = str(obj[0])
        bottomLeft = str(obj[1])
        topRight = str(obj[2])
        bottomRight = str(obj[3])
        middleCenter = str(obj[4])
        bottomCenter = str(obj[5])
        """
        for b in smallLabelHeads:
            cable = b.cable
            topLeft = b.cableBreakout.breakoutName + ' '+ b.cableBreakout.gender
            try:
                if b.originOrDestination == 'origin':
                    bottomLeft = '@'+cable.origin.locationDescription
                else:
                    bottomLeft = '@'+cable.destination.locationDescription
            except:
                bottomLeft = ''
            bottomRight = ''
            aBundle = False
            if len(cable.cableName) > 11:
                name = cable.code
            else:
                name = cable.cableName
            data = [topLeft, bottomLeft, '', bottomRight, name, '', aBundle, 'Small']
            SmallSheetHeads.add_label(data)

        if SmallSheetHeads.page_count != 0:
            theSheet = self.printdirectory+'01SmallBreakoutHeadLabels.pdf'
            SmallSheetHeads.save(theSheet)
            self.smallSheets.append(theSheet)
            self.smallPageCount += SmallSheetHeads.page_count

        for b in largeLabelHeads:
            cable = b.cable
            topLeft = b.cableBreakout.breakoutName + ' '+ b.cableBreakout.gender
            try:
                if b.originOrDestination == 'origin':
                    bottomLeft = '@'+cable.origin.locationDescription
                else:
                    bottomLeft = '@'+cable.destination.locationDescription
            except:
                bottomLeft = ''
            aBundle = False
            bottomRight = ''
            if len(cable.cableName) > 11:
                name = cable.code
            else:
                name = cable.cableName
            data = [topLeft, bottomLeft, '', bottomRight, name, '', aBundle, 'Large']
            if cable.cable.cableType in ['06Pr Mult', '03Pr Mult']:
                print cable
                data[4] = cable.code
                OneBlockSheet.add_label(data)
            else:
                LargeSheetHeads.add_label(data)

        if LargeSheetHeads.page_count != 0:
            theSheet = self.printdirectory+'05LargeBreakoutHeadLabels.pdf'
            LargeSheetHeads.save(theSheet)
            self.largeSheets.append(theSheet)
            self.largePageCount += LargeSheetHeads.page_count

        if OneBlockSheet.page_count != 0:
            theSheet = self.printdirectory+'07LargeBreakoutHeadLabels.pdf'
            OneBlockSheet.save(theSheet)
            self.largeSheets.append(theSheet)
            self.largePageCount += OneBlockSheet.page_count


        for x in maleBreakoutTails:
            for b in x:
                """
                topLeft = str(obj[0])
                bottomLeft = str(obj[1])
                topRight = str(obj[2])
                bottomRight = str(obj[3])
                middleCenter = str(obj[4])
                bottomCenter = str(obj[5])

                <div class="SmallLabelRightNumber">{{ pair.tailPairNumber }}</div>
                <div class="SmallLabelLeftUpperText">@ {{ pair.breakout.whichEnd }}</div>
                <div class="SmallLabelCenterText">{{ pair.tailLabel|sliceLabel:'10' }}</div>
                <div class="SmallLabelLeftText">{{ pair.breakout.cableBreakout.getShortName }}</div>
                <div class="SmallLabelRightText">{{ pair.breakout.cable.cableName }}</div>
                """
                printObj = []
                topLeft = '@ '+b.breakout.whichEnd
                bottomLeft = ''
                topRight = b.breakout.cableBreakout.getShortName()
                name = b.breakout.cable.cableName
                if len(name) > 10:
                    name = b.breakout.cable.code
                #bottomRight = name
                middleCenter = b.tailLabel
                bottomCenter = name + ' '+b.tailPairNumber
                printObj = [topLeft, bottomLeft, topRight, bottomRight, middleCenter, bottomCenter]
                BreakoutTailSheet.add_label(printObj)

        for x in femaleBreakoutTails:
            for b in x:
                """
                topLeft = str(obj[0])
                bottomLeft = str(obj[1])
                topRight = str(obj[2])
                bottomRight = str(obj[3])
                middleCenter = str(obj[4])
                bottomCenter = str(obj[5])

                <div class="SmallLabelRightNumber">{{ pair.tailPairNumber }}</div>
                <div class="SmallLabelLeftUpperText">@ {{ pair.breakout.whichEnd }}</div>
                <div class="SmallLabelCenterText">{{ pair.tailLabel|sliceLabel:'10' }}</div>
                <div class="SmallLabelLeftText">{{ pair.breakout.cableBreakout.getShortName }}</div>
                <div class="SmallLabelRightText">{{ pair.breakout.cable.cableName }}</div>
                """
                printObj = []
                topLeft = '@ '+b.breakout.whichEnd
                bottomLeft = ''
                topRight = b.breakout.cableBreakout.getShortName()
                name = b.breakout.cable.cableName
                if len(name) > 10:
                    name = b.breakout.cable.code
                #bottomRight = name
                middleCenter = b.tailLabel
                bottomCenter = name + ' '+b.tailPairNumber
                printObj = [topLeft, bottomLeft, topRight, bottomRight, middleCenter, bottomCenter]
                BreakoutTailSheet.add_label(printObj)

        theSheet = self.printdirectory+'02BreakoutTailLabels.pdf'
        BreakoutTailSheet.save(theSheet)
        self.smallSheets.append(theSheet)
        self.smallPageCount += BreakoutTailSheet.page_count


    def consolidateAllSheets(self, subDir=None):
        """
        not sure if this is neccessary or maybe I can send multiple sheets to the browser
        """
        writer = PdfWriter()
        if subDir != None:
            directory = self.printdirectory+subDir
        else:
            directory = self.printdirectory

        files = [x for x in os.listdir(directory) if x.endswith('.pdf')]
        for fname in sorted(files):
          writer.addpages(PdfReader(os.path.join(directory, fname)).pages)

        writer.write(directory+"output.pdf")

        for x in os.listdir(directory):
            if x == 'output.pdf':
                continue
            else:
                os.remove(directory+x)

    def saveAuxLabelSheet(self, auxLabels):
        """
        create the aux labels and return a consolidated sheet
        """
        SmallSheet = labelPrinter.Sheet(self.smallSpecs, self.draw_aux_label, border=self.drawBorder)
        LargeSheet = labelPrinter.Sheet(self.largeSpecs, self.draw_aux_label, border=self.drawBorder)

        largeLabel =  Label.objects.get(description__icontains='5160')
        smallLabel =  Label.objects.get(description__icontains='5167')

        # make the subdirectory for aux labels
        auxDir = self.printdirectory+'auxLabels/'
        if os.path.isdir(auxDir) == False:
            os.mkdir(auxDir)

        for auxLabel in auxLabels:
            if auxLabel.label == smallLabel:
                for x in range(auxLabel.quantityToPrint):
                    SmallSheet.add_label(auxLabel.labelText)
            elif auxLabel.label == largeLabel:
                for x in range(auxLabel.quantityToPrint):
                    LargeSheet.add_label(auxLabel.labelText)

        if SmallSheet.page_count > 0:
            theSheet = auxDir+'100AuxLabelsSmall.pdf'
            SmallSheet.save(theSheet)
        if LargeSheet.page_count > 0:
            theSheet = auxDir+'100AuxLabelsLarge.pdf'
            LargeSheet.save(theSheet)

        self.consolidateAllSheets(subDir='auxLabels/')
        return auxDir



    def printCablesBreakouts(self, cables=None, breakouts=None):
        """
        """
        largeCables = []
        oneBlockCables = []
        smallCables = []
        oneblocks = ['06Pr Mult', '03Pr Mult']

        if self.smallSpecs == self.small5167:
            smallLabel = Label.objects.get(description__icontains='5167')
        if self.largeSpecs == self.large5160:
            largeLabel = Label.objects.get(description__icontains='5160')
        for c in cables:
            if c.cable.label == smallLabel:
                smallCables.append(c)
            elif c.cable.label == largeLabel:
                if c.cable.cableType in oneblocks:
                    oneBlockCables.append(c)
                else:
                    largeCables.append(c)

        if cables != None:
            if len(largeCables) > 0:
                self.save_cable_sheet(largeCables, 'Large')
            if len(oneBlockCables) > 0:
                self.save_cable_sheet(oneBlockCables, 'OneBlock')
            if len(smallCables) > 0:
                self.save_cable_sheet(smallCables, 'Small')
        if breakouts != None:
            self.save_breakout_sheet(breakouts)

        self.consolidateAllSheets()

        return self.printdirectory, self.smallPageCount, self.largePageCount

