import logging
import os

import vtk

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin


#
# PointSelector
#

class PointSelector(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "PointSelector"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["PointSelector"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Saima Safdar"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
This module help user select a point on a model and then move to the next model using a shortcut key ctrl+k  <a href="https://github.com/organization/projectname#PointSelector">module documentation</a>.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """

"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # PointSelector1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='PointSelector',
        sampleName='PointSelector1',
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, 'PointSelector1.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames='PointSelector1.nrrd',
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums='SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
        # This node name will be used when the data set is loaded
        nodeNames='PointSelector1'
    )

    # PointSelector2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='PointSelector',
        sampleName='PointSelector2',
        thumbnailFileName=os.path.join(iconsPath, 'PointSelector2.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames='PointSelector2.nrrd',
        checksums='SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
        # This node name will be used when the data set is loaded
        nodeNames='PointSelector2'
    )


#
# PointSelectorWidget
#

class PointSelectorWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """
    
    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False
        
    

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/PointSelector.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = PointSelectorLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).
        #self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        #self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
      

        # Buttons
        self.ui.undoButton.connect('clicked(bool)', self.onUndoPress)
        self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)
        
        #self.ui.P4PushButton.connect('clicked(bool)', lambda: self.onPointPushButton('P4'))
        
        

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self):
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self):
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self):
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    def onSceneStartClose(self, caller, event):
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event):
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.GetNodeReference("InputVolume"):
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if inputParameterNode:
            self.logic.setDefaultParameters(inputParameterNode)

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self._parameterNode is not None and self.hasObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode):
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        self._updatingGUIFromParameterNode = True

        # Update node selectors and sliders
        #self.ui.inputSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
        #self.ui.outputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
       

        # Update buttons states and tooltips
        if self._parameterNode.GetNodeReference("InputVolume") and self._parameterNode.GetNodeReference("OutputVolume"):
            self.ui.applyButton.toolTip = "Compute output volume"
            self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = "Select input and output volume nodes"
            self.ui.applyButton.enabled = True

        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

        #self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputSelector.currentNodeID)
        #self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)
        

        self._parameterNode.EndModify(wasModified)
    
        
    def onPointPushButton(self, button):
        slicer.modules.markups.logic().SetActiveListID(self.markup_node)
        n_point = self.markup_node.GetNumberOfControlPoints()
        index = None
        for i in range(n_point):
            label = self.markup_node.GetNthControlPointLabel(i)
            if label == button:
                index = i
                print('Index: ', index)
                break
        if not index:
            raise ValueError('Point {0} not found.'.format(button))
        self.markup_node.UnsetNthControlPointPosition(index)
        self.markup_node.SetControlPointPlacementStartIndex(index)
        self.markup_node.SetNthControlPointLabel(index, button)
        slicer.modules.markups.logic().StartPlaceMode(0)
    
    def onUndoPress(self):
        self.logic.undoCommand()
        
    def onApplyButton(self):
        """
        Run processing when user clicks "Apply" button.
        """
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):

            # Compute output
            inputDir = self.ui.plyDir.directory
            nodeCounter = self.ui.nodeCounter.value
            self.logic.process(inputDir, nodeCounter)#, self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode())

            # Compute inverted output (if needed)
            # if self.ui.invertedOutputSelector.currentNode():
            #     # If additional output volume is selected then result with inverted threshold is written there
            #     self.logic.process(self.ui.inputSelector.currentNode(), self.ui.invertedOutputSelector.currentNode(),
            #                        self.ui.imageThresholdSliderWidget.value, not self.ui.invertOutputCheckBox.checked, showResult=False)


#
# PointSelectorLogic
#

class PointSelectorLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    
    """
    import pandas as pd
    df = pd.DataFrame()
    N_POINT = 3
    INDEX_DATA = 0
    modelDir = ''
    csv_input = " "
    index = 0
    pointCount = 0
    nodeCounter = 0
    
    def initialize_points(self):
        slicer.modules.markups.logic().SetActiveListID(self.markup_node)
        self.markup_node.SetControlPointLabelFormat('P%d')
        for i in range(1, self.N_POINT + 1):
            self.markup_node.AddControlPoint([0, 0, 0])
        self.markup_node.UnsetAllControlPoints()
        self.markup_node.SetMaximumNumberOfControlPoints(self.N_POINT)
        
        
    def switchNextModel(self):
        print("switching next model")
        self.pointCount = 0
        #getting the index of the model and getting the model name on that index
        self.INDEX_DATA = self.INDEX_DATA+1
        print("inside")
        print(self.modelDir)
        print(self.INDEX_DATA)
        print(self.df)
        
        #add a check if all the model files in the folder are loaded if yes then exit the program and user should not press the shortcut anymore
        #getting the length of the df
        lengthDF = len(self.df)
        print("length")
        print(lengthDF)
        if lengthDF == self.INDEX_DATA:
            exit(0)
        
        nextModelIndex = self.df.index.get_loc(self.INDEX_DATA) #nodeTotal will be the number of fiducials added from there you get to know how many models done and what is the next index of the model
        nextModel = self.df.iloc[self.INDEX_DATA].FileNames     # this will give the name of the file to be loaded from the folder 
        #modelDir = "/media/useradmin/Disk2/Slicer-5.3.0-2023-01-21-linux-amd64/Case1"  #directory remains the same but how to get the directory name here not hard coded
        
        #switching back the curser to non placement mode to select the location of the new model again
        # placeModePersistence = 0
        # slicer.modules.markups.logic().StartPlaceMode(placeModePersistence) 
        #before loading the next model clear the scene
        slicer.mrmlScene.Clear(0)
      
        #loading the next model
        modelNode = slicer.util.loadModel(self.modelDir + "/" + nextModel)
        size = len(nextModel)
        nextModel = nextModel[:size - 4]
        fidNode = slicer.util.loadMarkups(self.modelDir + "/" + nextModel + ".mrk.json")
        fidNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent, self.onMarkupEndInteraction)
        #saving file name (model file name). 
        self.csv_input.loc[self.INDEX_DATA,"FileName"]= nextModel+".ply"
        self.csv_input.to_csv(self.modelDir+"/landmarks.csv", index=False)
        
        
    def addNewNode(self):
        slicer.modules.markups.logic().SetActiveListID(self.markup_node)
        n_point = self.markup_node.GetNumberOfControlPoints()
        placeModePersistence = 1
        slicer.modules.markups.logic().StartPlaceMode(placeModePersistence)  
        
        for i in range(n_point):
            self.markup_node.UnsetNthControlPointPosition(i)
            self.markup_node.SetControlPointPlacementStartIndex(i)
            self.markup_node.SetNthControlPointLabel(index, "p"+i)
            
        slicer.modules.markups.logic().StartPlaceMode(0)
        
    def onMarkupsAdded(self, caller, event):
        index=0
        print(index)
        index+=1
        modelFileExt = "ply"
        
        print(index)
        modelDir = "/media/useradmin/Disk2/Slicer-5.3.0-2023-01-21-linux-amd64/Case1"
        modelFiles = list(f for f in os.listdir(modelDir) if f.endswith("."+modelFileExt))
        print(modelFiles)
        placeModePersistence = 0
        slicer.modules.markups.logic().StartPlaceMode(placeModePersistence) 
        modelNode = slicer.util.loadModel(modelDir + "/" + modelFiles[index])
        
    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)

    def setDefaultParameters(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        if not parameterNode.GetParameter("Threshold"):
            parameterNode.SetParameter("Threshold", "100.0")
        if not parameterNode.GetParameter("Invert"):
            parameterNode.SetParameter("Invert", "false")


    def onMarkupEndInteraction(self, caller, event):
        import csv
        markupsNode = caller
        markupsNodeindex = int(caller.GetAttribute('Markups.MovingMarkupIndex'))
        pos = [0,0,0]
        markupsNode.GetNthControlPointPosition(markupsNodeindex, pos)
        #sliceView = markupsNode.GetAttribute("Markups.MovingInSliceView")
        #movingMarkupIndex = markupsNode.GetDisplayNode().GetActiveControlPoint()
        print(markupsNodeindex)
        print(pos)
        #saving file name (model file name). index which is selected by the user and the position x,y,z coordinates
        import pandas as pd
        #df=pd.DataFrame({})
        #.loc[row, column] = some thing
        self.index = self.index+1
        
        modelFileName =  self.df.iloc[self.INDEX_DATA].FileNames
        # self.csv_input.loc[self.index,"FileName"]= modelFileName
        # self.csv_input.loc[self.index,"Index_no"]= markupsNodeindex
        # self.csv_input.loc[self.index, "Position/location-x,y,z"] = str(pos)
        position = str(pos)
        print(modelFileName+","+str(markupsNodeindex)+","+ str(pos))
        #new_data= {'FileName':modelFileName, 'Index_no':str(markupsNodeindex), 'Position/location-x,y,z':position}
        #df=pd.DataFrame([new_data])
        #self.csv_input.to_csv(self.modelDir+"/landmarks.csv", index=False)
        #df.to_csv(self.modelDir+"/landmarks.csv", index=False, mode='a')
        #print(movingMarkupIndex)
        #logging.info("End interaction: point ID = {0}, slice view = {1}".format(movingMarkupIndex, sliceView))
        self.pointCount = self.pointCount+1
        if self.pointCount<=self.nodeCounter:
            with open(self.modelDir+"/landmarks.csv", 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([modelFileName, markupsNodeindex, position])
        else:
            print("no adding of points allowed")
       
    def undoCommand(self):
        import csv
        #run when undo button pressed
        if self.pointCount > self.nodeCounter:
            self.pointCount = self.pointCount-2
            f = open(self.modelDir+"/landmarks.csv", "r+")
            lines = f.readlines()
            lines.pop()
            f = open(self.modelDir+"/landmarks.csv", "w+")
            f.writelines(lines)
        elif self.pointCount <= self.nodeCounter:
            self.pointCount = self.pointCount-1
            f = open(self.modelDir+"/landmarks.csv", "r+")
            lines = f.readlines()
            lines.pop()
            f = open(self.modelDir+"/landmarks.csv", "w+")
            f.writelines(lines)
        elif self.pointCount == 0:
            print("dont do any more subtraction")
        print(self.pointCount)
        
        
        
    def process(self, inputDir, nodeCounter):#, inputVolume, outputVolume):
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: volume to be thresholded
        :param outputVolume: thresholding result
        :param imageThreshold: values above/below this threshold will be set to 0
        :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
        :param showResult: show output volume in slice viewers
        """
        global index
        print(inputDir)
        #if not inputVolume or not outputVolume:
        #    raise ValueError("Input or output volume is invalid")

        import time
        startTime = time.time()
        logging.info('Processing started')
        logging.info('Search for .ply files')
        self.modelDir = inputDir
        modelFileExt = "ply"
        
        import math
        import os
        
        modelFiles = list(f for f in os.listdir(self.modelDir) if f.endswith("."+modelFileExt))
        print(modelFiles)
        
        import pandas as pd
        
        #dataframe to store all the ply files name along with index
        self.df = pd.DataFrame(list(zip(modelFiles)), columns =['FileNames'])
        
        filepath = inputDir+"/models_ids.csv"
        self.df.to_csv(filepath, index=True)
        
        #creating another dataframe empty initially to store the filename, index of the point selected by the user and the position x y z coordinates saving the file csv
        # filePath2 = inputDir+"/landmarks.csv"
        # df = pd.DataFrame(list(zip(" ", " ", " ")), columns =['FileName', 'Index_no', 'Position/location-x,y,z'])
        # df.to_csv(filePath2, index=True)
        #setting the node counter for all the models
        self.nodeCounter = nodeCounter
        import csv
        with open(self.modelDir+"/landmarks.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['FileName', 'Index_no', 'Position/Location-x,y,z'])
        
        #load models and show in 3D view
        print(self.INDEX_DATA)
        modelFileName =  self.df.iloc[self.INDEX_DATA].FileNames
        
        #saving the filename in the landmarks csv file the first column
        #self.csv_input = pd.read_csv(inputDir+"/landmarks.csv")
        #self.csv_input.loc[self.INDEX_DATA,"FileName"]= modelFileName
        #self.csv_input.to_csv(inputDir+"/landmarks.csv", index=False)
      
        #loading the first model in the list
        modelNode = slicer.util.loadModel(self.modelDir + "/" + modelFileName)
        
        
        size = len(modelFileName)
        modelFileName = modelFileName[:size - 4]
        #loading the fiducials (control ppoint) relevant to the model
        fidNode = slicer.util.loadMarkups(self.modelDir+"/"+modelFileName+".mrk.json")
        
        
        fidNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent, self.onMarkupEndInteraction)
        #now turning on the node placement mode and then placcing the fiducial at the specified point on the model
        # node_id = slicer.modules.markups.logic().AddNewFiducialNode('modelFileName') #modelFileName frm the list dataframe
        # self.markup_node = slicer.mrmlScene.GetNodeByID(node_id)
        # self.initialize_points()
                
        #placeModePersistence = 1
        #slicer.modules.markups.logic().StartPlaceMode(placeModePersistence) 
        #markup_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
        
        import qt
        # shortcut1 = qt.QShortcut(qt.QKeySequence('p'), slicer.util.mainWindow())
        # shortcut1.connect('activated()', self.addNewNode)
        
       
                    
        #markup_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
        
        #markup_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointAddedEvent, self.onMarkupsAdded)
        
        shortcut = qt.QShortcut(slicer.util.mainWindow())
        shortcut.setKey(qt.QKeySequence('ctrl+k'))
        shortcut.connect( 'activated()', self.switchNextModel)

        
        #placeModePersistence = 0
        #slicer.modules.markups.logic().StartPlaceMode(placeModePersistence)    
        #slicer.util.updateMarkupsControlPointsFromArray(markup_node, np.random.rand(10,3))
        #markup_node.GetDisplayNode().SetTextScale(0)    
        #markup_node.GetDisplayNode().SetPointLabelsVisibility(False)
       

        # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
        # cliParams = {
        #     'InputVolume': inputVolume.GetID(),
        #     'OutputVolume': outputVolume.GetID(),
        #     'ThresholdValue': imageThreshold,
        #     'ThresholdType': 'Above' if invert else 'Below'
        # }
        # cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
        # # We don't need the CLI module node anymore, remove it to not clutter the scene with it
        # slicer.mrmlScene.RemoveNode(cliNode)

        stopTime = time.time()
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')


#
# PointSelectorTest
#

class PointSelectorTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_PointSelector1()

    def test_PointSelector1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        import SampleData
        registerSampleData()
        inputVolume = SampleData.downloadSample('PointSelector1')
        self.delayDisplay('Loaded test data set')

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = PointSelectorLogic()

        # Test algorithm with non-inverted threshold
        logic.process(inputVolume, outputVolume, threshold, True)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], threshold)

        # Test algorithm with inverted threshold
        logic.process(inputVolume, outputVolume, threshold, False)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], inputScalarRange[1])

        self.delayDisplay('Test passed')
