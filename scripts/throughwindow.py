
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya import OpenMayaUI as omui
import pymel.core as pm
import maya.cmds as cmds
import logging
try:
    from PySide.QtGui import *
    from PySide.QtCore import *
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *

_lookThroughWindow = None
_logger = logging.getLogger(__name__)

class LookThroughWindow(MayaQWidgetDockableMixin, QWidget):
    THROUGH_NAME = "lighttoolsThroughWindow"
    
    """ LookThrough window. """
    def __init__(self):
        """ Initialize JMLookThroughWindow. """
        super(LookThroughWindow, self).__init__(parent=None)
        self.setWindowFlags(Qt.Tool)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setObjectName(LookThroughWindow.THROUGH_NAME)
        self.starting_size = QSize(300, 300)
        self.minimum_size = QSize(100, 100)
        self.preferredSize = self.starting_size
        self.resize(self.preferredSize)
        self.panel = None

        self.deleteThroughCam()

        # Create Panel layout
        layout = QVBoxLayout()
        layout.setObjectName(self.objectName() + "VerticalBoxLayout")
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        btn = QPushButton()
        btn.setText("Select Light")
        btn.setMinimumHeight(35)
        btn.clicked.connect(self.selectLight)
        layout.addWidget(btn)

        self.setLayout(layout)

        # Get layout name
        layout_name = omui.MQtUtil.fullName(long(getCppPointer(layout)[0]))
        old_parent = pm.setParent(query=True)
        pm.cmds.setParent(layout_name)

        # Either create or get panel
        panel_name = self.objectName() + "ModelPanelLabel"
        previous_panel = pm.cmds.getPanel(withLabel=panel_name)
        self.panel = pm.cmds.modelPanel()
        pm.cmds.modelPanel(self.panel, edit=True, label=panel_name, parent=layout)

        # Delete previous panel
        if previous_panel is not None:
            pm.deleteUI(previous_panel, panel=True)

        # Edit panel
        editor = pm.cmds.modelPanel(self.panel, query=True, modelEditor=True)
        pm.cmds.modelEditor(editor, edit=True, displayAppearance="smoothShaded", locators=True)

        # Set Parent
        pm.cmds.setParent(old_parent)



    def dockCloseEventTriggered(self):
        """ Close event. """
        global _lookThroughWindow
        _lookThroughWindow = None
        self.deleteThroughCam()

    def deleteThroughCam(self):
        """ Delete Camera created by looktrough. """
        looked_through = self._isLookThrough()
        if looked_through is not None:
            pm.delete(looked_through)

    def selectLight(self):
        """ Select light from look through window. """
        pm.select(self.lightname)

    def lookThroughSelectedLight(self):
        self.lightname = None
        selected = _onlyLightsFromSelection()
        if selected:
            self.lightname = selected[-1].name()

        if self.lightname and self.panel:
            self.setWindowTitle(self.lightname)
            cmd = "lookThroughModelPanelClipped(\"" + self.lightname + "\", \"" + self.panel + "\", 0.001, 1000)"
            pm.mel.eval(cmd)
            _logger.info("Look through : %s" % self.lightname)

            if pm.objExists("cameraShape1"):
                pm.setAttr("cameraShape1.farClipPlane", 1000000)
                pm.setAttr("cameraShape1.nearClipPlane", 0.001)

        else:
            self.setWindowTitle("NO LIGHT")

    # def _onlyLightsFromSelection(self, get_shapes=False, all_hierachy=False):
    #     """ Isolate Lights From Selection.

    #         Args:
    #             get_shapes (bool): Return 'shape' if True, otherwrise return 'transform'.
    #             all_hierachy (bool): Get all selection children if True.

    #         Returns:
    #             (list): Selected lights
    #     """
    #     # Get either selection or selection + children
    #     selection = []
    #     if all_hierachy:
    #         for node in pm.selected():
    #             children = [nde for nde in node.getChildren(ad=True) if pm.nodeType(nde.name()) != "transform"]
    #             selection.extend(children)
    #     else:
    #         selection.extend(pm.selected())

    #     lights = []
    #     for node in selection:
    #         # Get shape
    #         if pm.nodeType(node.name()) == "transform":
    #             node = node.getShape()
    #             if node is None:
    #                 continue

    #         # Check node type then append it to 'lights' list if is a light node
    #         if pm.nodeType(node.name()) in self.lgt_types:
    #             lights.append(node)

    #     # Return if list is empty
    #     if not lights:
    #         _logger.warning("No lights selected")
    #         return None

    #     # Get Transform if not 'get_shapes'
    #     if not get_shapes:
    #         lights = [shape.getParent() for shape in lights]

    #     _logger.debug("_onlyLightsFromSelection : %s" % lights)
    #     return lights

    def _isLookThrough(self):

        self.lgt_types = [
        "ambientLight",
        "pointLight",
        "spotLight",
        "areaLight",
        "directionalLight",
        "volumeLight"
        ]
        """ Get looked through camera.

            Returns:
                (camera): looked through camera
        """
        looked_through = None
        for cam in pm.ls(ca=True):
            shape = cam.getParent().getShape()
            if shape is None:
                continue

            if pm.nodeType(shape) in self.lgt_types:
                looked_through = cam
                break

        return looked_through

    # def lookThroughWindowClosed(self):
    #     """ Hook up callback when the through window is closed. """
    #     global _lookThroughWindow

    #     if _lookThroughWindow:
    #         self.deleteThroughCam()
    #         _lookThroughWindow = None

    # def lookThroughWindowChanged(self):
    #     """ Hook up callback when the through window is moved and resized. """
    #     global _lookThroughWindow
    #     self.saveWindowState(_lookThroughWindow, LookThroughWindow.THROUGH_NAME + "State")

    # def createLookThroughWindow(self):
    #     """ Show through Window. """
    #     global _lookThroughWindow

    #     if (_lightToolkitWindow is None) and not (self._onlyLightsFromSelection()):
    #         return None

    #     control = LookThroughWindow.THROUGH_NAME + "WorkspaceControl"
    #     if pm.workspaceControl(control, q=True, exists=True) and _lookThroughWindow is None:
    #         pm.workspaceControl(control, e=True, close=True)
    #         pm.deleteUI(control)

    #     if _lookThroughWindow is None:
    #         _lookThroughWindow = LookThroughWindow()
    #         _lookThroughWindow.windowStateChanged.connect(self.lookThroughWindowChanged)

    #     required_control = _lightToolkitWindow.objectName() + 'WorkspaceControl'
    #     _lookThroughWindow.show(dockable=True, controls=required_control,
    #         closeCallback='import throughwindow\ntest = throughwindow()\ntest.lookThroughWindowClosed()')

    #     self.lookThroughSelectedLight()
    #     return _lookThroughWindow

    # def saveWindowState(self,editor, optionVar):
    #     windowState = editor.showRepr()
    #     pm.cmds.optionVar(sv=(optionVar, windowState))

def lookThroughWindowClosed():
    """ Hook up callback when the through window is closed. """
    global _lookThroughWindow

    if _lookThroughWindow:
        LookThroughWindow.deleteThroughCam()
        _lookThroughWindow = None

def lookThroughWindowChanged():
    """ Hook up callback when the through window is moved and resized. """
    global _lookThroughWindow
    THROUGH_NAME = "lighttoolsThroughWindow"
    saveWindowState(_lookThroughWindow, THROUGH_NAME + "State")

def createLookThroughWindow():
    """ Show through Window. """
    global _lookThroughWindow
    THROUGH_NAME = "lighttoolsThroughWindow"
    
    if not (_onlyLightsFromSelection()):
        return None

    control = THROUGH_NAME + "WorkspaceControl"
    if pm.workspaceControl(control, q=True, exists=True) and _lookThroughWindow is None:
        pm.workspaceControl(control, e=True, close=True)
        pm.deleteUI(control)

    if _lookThroughWindow is None:
        _lookThroughWindow = LookThroughWindow()
        _lookThroughWindow.windowStateChanged.connect(lookThroughWindowChanged)

    required_control = THROUGH_NAME + 'WorkspaceControl'
    _lookThroughWindow.show(required_control)
    # _lookThroughWindow.show(dockable=True, controls=required_control,
    #     closeCallback='import jmLightToolkit\njmLightToolkit.lookThroughWindowClosed()')

    _lookThroughWindow.lookThroughSelectedLight()
    return _lookThroughWindow

def saveWindowState(editor, optionVar):
    windowState = editor.showRepr()
    cmds.optionVar(sv=(optionVar, windowState))

def getPanels():
    """ Get current viewport panel. """
    # Get Panel, if persp found, throught this cam
    all_panels = [ui for ui in pm.getPanel(vis=True) if "modelPanel" in ui.name()]
    current_panel = None
    for panel in all_panels:
        if "persp" in pm.windows.modelPanel(panel, query=True, camera=True):
            current_panel = panel
            break

    else:  # if modelPanel4 find, throught this cam
        for panel in all_panels:
            if panel.name() == "modelPanel4":
                current_panel = panel
                break
        else:
            current_panel = all_panels[-1]
    
    return current_panel

def _onlyLightsFromSelection(get_shapes=False, all_hierachy=False):
    lgt_deftypes = [
        "ambientLight",
        "pointLight",
        "spotLight",
        "areaLight",
        "directionalLight",
        "volumeLight"
    ]

    selection = []
    if all_hierachy:
        for node in pm.selected():
            children = [nde for nde in node.getChildren(ad=True) if pm.nodeType(nde.name()) != "transform"]
            selection.extend(children)
    else:
        selection.extend(pm.selected())

    lights = []
    for node in selection:
        # Get shape
        if pm.nodeType(node.name()) == "transform":
            node = node.getShape()
            if node is None:
                continue

        # Check node type then append it to 'lights' list if is a light node
        if pm.nodeType(node.name()) in lgt_deftypes:
            lights.append(node)

    # Return if list is empty
    if not lights:
        _logger.warning("No lights selected")
        return None

    # Get Transform if not 'get_shapes'
    if not get_shapes:
        lights = [shape.getParent() for shape in lights]

    _logger.debug("_onlyLightsFromSelection : %s" % lights)
    return lights

def _run():

    current_panel = getPanels()

    createLookThroughWindow()

    # See Trough
    lights = _onlyLightsFromSelection()
    if lights:
        light =  lights[0].name()
        cmd = "lookThroughModelPanelClipped(\"" + light + "\", \"" + current_panel + "\", 0.001, 10000)"
        pm.mel.eval(cmd)
        _logger.info("Look through : %s" % light)

_run()