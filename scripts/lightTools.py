#!/usr/bin/env python
# coding=utf-8
'''
Author        : zhenghaoming
Date          : 2022-09-13 13:56:11
FilePath      : \lighttools\lightTools.py
version       : 
LastEditors   : zhenghaoming
LastEditTime  : 2022-09-16 18:17:46
'''

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtWidgets import QWidget
from functools import partial
from shiboken2 import getCppPointer
import maya.cmds as cmds
import pymel.core as pm
import os,sys,logging,re
import maya.api.OpenMaya as om
import maya.OpenMayaUI as omui

_logger = logging.getLogger(__name__)

script_path = r'Z:\Project\ScriptProjs\XYY\lightTools'

sys.path.append(script_path)
from scripts.LightCustomPreset import LightCustomPreset

class lighttoolsUtils(object):
    AR_PLUG_IN_NAME = "mtoa"
    RS_PLUG_IN_NAME = "redshift4maya"

    @classmethod
    def is_ar_plugin_loaded(cls):
        try:
            return cmds.pluginInfo(cls.AR_PLUG_IN_NAME, q=True, loaded=True)
        except:
            return

    @classmethod
    def ar_load_plugin(cls):
        if not cls.is_ar_plugin_loaded():
            try:
                cmds.loadPlugin(cls.AR_PLUG_IN_NAME)
                cmds.evalDeferred("import mtoa;")
            except:
                om.MGlobal.displayError("Failed to load arnold plug-in: {0}".format(cls.AR_PLUG_IN_NAME))
                return

        return True

    @classmethod
    def is_rs_plugin_loaded(cls):
        try:
            return cmds.pluginInfo(cls.RS_PLUG_IN_NAME, q=True, loaded=True)
        except:
            return

    @classmethod
    def rs_load_plugin(cls):
        if not cls.is_rs_plugin_loaded():
            try:
                cmds.loadPlugin(cls.RS_PLUG_IN_NAME)
            except:
                om.MGlobal.displayError("Failed to load redshift plug-in: {0}".format(cls.RS_PLUG_IN_NAME))
                return

        return True

class lighttoolsSetting_widget(object):

    def __init__(self,parent_lay):
        self.parent_lay = parent_lay

        self.displayed_layer_name = "displayedLights"
        self.muted_layer_name = "mutedLights"

        self.lgt_types_default = LightCustomPreset.LGT_TYPES_DEFAULT
        self.lgt_types_arnold = LightCustomPreset.LGT_TYPES_ARNOLD
        self.lgt_types_redshift = LightCustomPreset.LGT_TYPES_REDSHIFT

        self.lgt_attrs_default = LightCustomPreset.LGT_ATTRS_DEFAULT
        self.lgt_attrs_arnold = LightCustomPreset.LGT_ATTRS_ARNOLD
        self.lgt_attrs_redshift = LightCustomPreset.LGT_ATTRS_REDSHIFT

        self.lgt_types = self.lgt_types_default + self.lgt_types_arnold + self.lgt_types_redshift
        self.lgt_attrs = self.lgt_attrs_default + self.lgt_attrs_arnold + self.lgt_attrs_redshift

        self.create_layout()
        self.create_widget()

    def create_layout(self):
        self.opt_main_scro_lay = cmds.columnLayout(adj=1,p=self.parent_lay)
        self.main_frame_lay = cmds.frameLayout(cll=False,bgc=[0, 0.6, 0.2],l=u'MAIN',p=self.opt_main_scro_lay)
        self.main_row1_lay = cmds.rowLayout(nc=2,adj=1,p=self.main_frame_lay)
        self.main_row2_lay = cmds.rowLayout(nc=2,adj=1,p=self.main_frame_lay)
        self.main_row3_lay = cmds.rowLayout(nc=1,adj=1,p=self.main_frame_lay)
        self.main_row4_lay = cmds.rowLayout(nc=4,adj=4,p=self.main_frame_lay)
        self.main_row5_lay = cmds.rowColumnLayout(adj=1,p=self.main_frame_lay)
        self.attri_tab_lay = cmds.tabLayout(p=self.main_frame_lay,tv=False,cr=True)
        self.attri_col_lay = cmds.columnLayout(adj=True,p=self.attri_tab_lay)

        self.linking_frame_lay = cmds.frameLayout(bgc=[0.0, 0.5, 0.4],l=u'LINKING',p=self.opt_main_scro_lay)
        self.linking_cow1_lay = cmds.rowColumnLayout(adj=1,p=self.linking_frame_lay)
        self.linking_row1_lay = cmds.rowLayout(nc=2,adj=1,p=self.linking_frame_lay)
        self.linking_cow2_lay = cmds.rowColumnLayout(adj=1,p=self.linking_frame_lay)

        self.colotframe_lay = cmds.frameLayout(bgc=[0.0, 0.7, 0.2],bv=True,l=u'COLOR OUTLINER',p=self.opt_main_scro_lay)
        self.color_row1_lay = cmds.rowLayout(h=50,nc=10,p=self.colotframe_lay)

    def create_widget(self):
        getIcon = lambda icon_name : (os.path.join(script_path,  "icon", icon_name))
        
        self.soloLight_btn = cmds.button(h=30,l=u'Solo Lights',p=self.main_row1_lay,
                                        c=self.soloLights)
        self.soloLights_hierarchy_btn = cmds.symbolCheckBox(i=u'out_MASH_Orient.png',
                                                            p=self.main_row1_lay)
        self.mutelights_btn = cmds.button(h=30,l=u'Mute Lights',c=self.muteLights,
                                        p=self.main_row2_lay)
        self.restoreLight_btn = cmds.button(h=30,l=u'Restore Lights',c=self.restoreLights,
                                        p=self.main_row2_lay)

        # self.lookThroughWindow_btn = cmds.symbolCheckBox(i=u'TTF_Option_150.png',
        #                                                 p=self.main_row3_lay)
        self.lookThrough_btn = cmds.button(h=30,l=u'Look Through',
                                c=self.lookThrough,
                                p=self.main_row3_lay)

        self.t_quickAlign_btn = cmds.symbolCheckBox(i=getIcon('Translate.png'),
                                                    p=self.main_row4_lay)

        self.r_quickAlign_btn = cmds.symbolCheckBox(i=getIcon('Rotate.png'),
                                                    p=self.main_row4_lay)

        self.s_quickAlign_btn = cmds.symbolCheckBox(i=getIcon('Scale.png'),
                                                    p=self.main_row4_lay)

        self.quickAlign_btn = cmds.button(h=30,l=u'Quick Align',
                                c=self.quickAlign,
                                p=self.main_row4_lay)

        self.selectAllLights_btn = cmds.button(h=30,l=u'Select All Lights',
                                c=self.selectAllLights,
                                p=self.main_row5_lay)
        cmds.separator(st='none',h=5,p=self.main_row5_lay)
        self.selectNotIlluminatingLights_btn = cmds.button(h=30,l=u'Select Not Illuminating Lights',
                                c=self.selectNotIlluminatingLights,
                                p=self.main_row5_lay)

        self.colorPicker_csbtn = cmds.colorSliderButtonGrp(h=30,bl=u'Set Lights Color',
                                                        p=self.attri_col_lay,
                                                        bc=self.setColorPicked)
        self.transfertLightAttributes_btn =  cmds.button(h=30,l=u'Transfert Light Attributes',
                                                        p=self.attri_col_lay,
                                                        c=self.transfertLightAttrs)

        self.createSet_btn =  cmds.button(h=30,l=u'Create Set',
                                                        p=self.linking_cow1_lay,
                                                        c=self.createSet)
        self.makeLights_btn =  cmds.button(h=30,l=u'Make Lights',
                                                        p=self.linking_row1_lay,
                                                        c=self.makeLightLinks)
        self.breakLights_btn =  cmds.button(h=30,l=u'Break Lights',
                                                        p=self.linking_row1_lay,
                                                        c=self.breakLightLinks)
        self.selectLinked_btn =  cmds.button(h=30,l=u'Select All Lights',
                                                        p=self.linking_cow2_lay,
                                                        c=self.selectLinked)
        cmds.separator(st='none',h=5,p=self.linking_cow2_lay)
        self.breakAllLinks_btn =  cmds.button(h=30,l=u'Break All Links',
                                                        p=self.linking_cow2_lay,
                                                        c=self.breakAllLinks)
        cmds.separator(st='none',h=5,p=self.linking_cow2_lay)
        self.transfertLightsLinks_btn =  cmds.button(h=30,l=u'Transfert Lights Links',
                                                        p=self.linking_cow2_lay,
                                                        c=self.transfertLightLinks)

        self.colorOutliner_R = cmds.button(w=33,h=30,bgc=[1.000, 0.500, 0.500],
                                            l='',p=self.color_row1_lay,
                                            c=partial(self.colorOutlinerSelected,"red",True))
        self.colorOutliner_O = cmds.button(w=33,h=30,bgc=[0.900, 0.700, 0.400],l='',
                                            p=self.color_row1_lay,
                                            c=partial(self.colorOutlinerSelected,"orange",True))
        self.colorOutliner_Y = cmds.button(w=33,h=30,bgc=[1.000, 1.000, 0.500],l='',
                                            p=self.color_row1_lay,
                                            c=partial(self.colorOutlinerSelected,"yellow",True))
        self.colorOutliner_G = cmds.button(w=33,h=30,bgc=[0.600, 1.000, 0.400],l='',
                                            p=self.color_row1_lay,
                                            c=partial(self.colorOutlinerSelected,"green",True))
        self.colorOutliner_T = cmds.button(w=33,h=30,bgc=[0.300, 1.000, 0.700],l='',
                                            p=self.color_row1_lay,
                                            c=partial(self.colorOutlinerSelected,"turquoise",True))
        self.colorOutliner_C = cmds.button(w=33,h=30,bgc=[0.500, 1.000, 1.000],l='',
                                            p=self.color_row1_lay,
                                            c=partial(self.colorOutlinerSelected,"cyan",True))
        self.colorOutliner_B = cmds.button(w=33,h=30,bgc=[0.300, 0.700, 1.000],l='',
                                            p=self.color_row1_lay,
                                            c=partial(self.colorOutlinerSelected,"blue",True))
        self.colorOutliner_P = cmds.button(w=33,h=30,bgc=[0.600, 0.400, 1.000],l='',
                                            p=self.color_row1_lay,
                                            c=partial(self.colorOutlinerSelected,"purple",True))
        self.colorOutliner_M = cmds.button(w=33,h=30,bgc=[1.000, 0.500, 1.000],l='',
                                            p=self.color_row1_lay,
                                            c=partial(self.colorOutlinerSelected,"magenta",True))
        self.colorOutliner_none = cmds.button(w=33,h=30,bgc=[1.0, 1.0, 1.0],l='',
                                            p=self.color_row1_lay,
                                            c=partial(self.colorOutlinerSelected,"red", False))

    def _wrapperUndoChunck(function):
        """ Create an undo Chunk and wrap it. """
        def wrapper(self, *args, **kwargs):
            try:
                pm.undoInfo(openChunk=True)
                function(self, *args, **kwargs)
            finally:
                pm.undoInfo(closeChunk=True)

        return wrapper

    def _wrapperSelected(function):
        """ Recover selection. """
        def wrapper(self, *args, **kwargs):
            selected = None
            try:
                selected = pm.selected()
                function(self, *args, **kwargs)
            finally:
                pm.select(selected)

        return wrapper

    @_wrapperUndoChunck
    @_wrapperSelected
    def soloLights(self,*args):
        self.restoreLights()
        is_hierarchy = cmds.symbolCheckBox(self.soloLights_hierarchy_btn,q=True,v=True)
        lights = { "displayed" : self._onlyLightsFromSelection(all_hierachy=is_hierarchy), "muted" : [] }

        # Return if lists them empty
        if not lights["displayed"]:
            return None

        # Get unselected lights
        all_lights = self._getAllLights()
        lights["muted"] = list(set(all_lights).difference(lights["displayed"]))

        # Create Display layer
        pm.select(clear=True)
        muted_layer = pm.createDisplayLayer(n=self.muted_layer_name)
        muted_layer.addMembers(lights["muted"])
        muted_layer.color.set(21)
        muted_layer.visibility.set(0)

        displayed_layer = pm.createDisplayLayer(n=self.displayed_layer_name)
        displayed_layer.addMembers(lights["displayed"])
        displayed_layer.color.set(22)

        self.__soloMuteLightsCSS()
        _logger.info("Lights displayed : %s" % [lgt.name() for lgt in lights["displayed"]])
        return lights["displayed"]

    @_wrapperUndoChunck
    @_wrapperSelected
    def muteLights(self,*args):
        """ Put lights selected in 'muted lights' display layer.

            Returns:
                (list): Muted lights.
        """
        is_hierarchy = cmds.symbolCheckBox(self.soloLights_hierarchy_btn,q=True,v=True)
        lights = self._onlyLightsFromSelection(all_hierachy=is_hierarchy)

        # Return if list is empty
        if not lights:
            return None

        # Create Display layer either get it
        if pm.objExists(self.muted_layer_name):
            pm.PyNode(self.muted_layer_name).addMembers(lights)
        else:
            pm.select(clear=True)
            muted_layer = pm.createDisplayLayer(n=self.muted_layer_name)
            muted_layer.addMembers(lights)
            muted_layer.color.set(21)
            muted_layer.visibility.set(0)

        self.__soloMuteLightsCSS()
        _logger.info("Lights muted : %s" % [lgt.name() for lgt in lights])
        return lights

    @_wrapperUndoChunck
    def restoreLights(self,*args):
        """ Delete Displayed/Muted display layer. """
        something_deleted = False
        if pm.objExists(self.displayed_layer_name):
            pm.delete(self.displayed_layer_name)
            something_deleted = True

        if pm.objExists(self.muted_layer_name):
            pm.delete(self.muted_layer_name)
            something_deleted = True

        if something_deleted:
            self.__soloMuteLightsCSS()
            _logger.info("Lights visibilities restored.")
            return True
        else:
            return False

    def __soloMuteLightsCSS(self):
        """ Solo/Mute Lights look. """
        if pm.objExists(self.displayed_layer_name):
            # self.pushButton_soloLights.setStyleSheet(self.css_btn_on)
            cmds.button(self.soloLight_btn,e=True,bgc=[1,0.5,0])
        else:
            cmds.button(self.soloLight_btn,e=True,bgc=[0.4,0.4,0.4])

        if pm.objExists(self.muted_layer_name):
            cmds.button(self.mutelights_btn,e=True,bgc=[1,0.5,0])
        else:
            cmds.button(self.mutelights_btn,e=True,bgc=[0.4,0.4,0.4])

    def getPanels(self):
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

    @_wrapperUndoChunck
    def lookThrough(self,*args):
        """ Light lookthrough. """
        # Get panels 
        current_panel = self.getPanels()

        # If already Through, delete cam
        looked_through = self._isLookThrough()
        if looked_through is not None:
            pm.delete(looked_through)

            # Looktrough persp
            persp_cam = [cam for cam in  pm.ls(ca=True) if "persp" in cam.name()]
            if persp_cam:
                persp_cam = persp_cam[0].getParent().name()
                cmd = "lookThroughModelPanelClipped(\"" + persp_cam + "\", \"" + current_panel + "\", 0.001, 10000)"
                pm.mel.eval(cmd)

            return

        # Return is no light found in selection
        if not self._onlyLightsFromSelection():
            return None

        # # Look Through Window
        # if cmds.symbolCheckBox(self.lookThroughWindow_btn, q=True, v=True):
        #     throughwin = lighttoolsThroughWindow()
        #     return

        # See Trough
        lights = self._onlyLightsFromSelection()
        if lights:
            light =  lights[0].name()
            cmd = "lookThroughModelPanelClipped(\"" + light + "\", \"" + current_panel + "\", 0.001, 10000)"
            pm.mel.eval(cmd)
            _logger.info("Look through : %s" % light)

    def _isLookThrough(self):
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

    @_wrapperUndoChunck
    def quickAlign(self,*args):
        """ Quick Align like 3DS Max. """
        # Get checkbox value
        t_ = cmds.symbolCheckBox(self.t_quickAlign_btn,q=True,v=True)
        r_ = cmds.symbolCheckBox(self.r_quickAlign_btn,q=True,v=True)
        s_ = cmds.symbolCheckBox(self.s_quickAlign_btn,q=True,v=True)

        # Return if no one checkbox checked
        if not t_ and not r_ and not s_:
            _logger.warning("Nothing checked in UI")
            return None

        # Get selection then check it
        selected = pm.selected()
        if not selected:
            _logger.warning("Nothing selected")
            return None

        elif len(selected) < 2:
            _logger.warning("Only one object selected")
            return None

        master = selected[-1]
        slaves = selected[:-1]
        if t_:  # Match translation
            for slave in slaves :
                pm.matchTransform(slave, master, position=True)

        if r_:  # Match rotation
            for slave in slaves :
                pm.matchTransform(slave, master, rotation=True)

        if s_:  # Match scale
            for slave in slaves :
                pm.matchTransform(slave, master, scale=True)

        pm.select(slaves)
        _logger.info("%s aligned to %s" % (slaves, master))
        return True

    def selectAllLights(self,*args):
        """ Select all standard/Arnold lights from scene """
        all_lights = self._getAllLights()
        pm.select(all_lights, add=True)
        return all_lights

    def selectNotIlluminatingLights(self,*args):
        """ Select not Illuminating lights """
        not_illuminating = []
        for light in self._getAllLights():
            if not pm.lightlink(light=light):
                not_illuminating.append(light)

        if not not_illuminating:
            _logger.info("all Lights is linked")
            return

        pm.select(not_illuminating)
        _logger.info("%s illuminate nothing" % [lgt.name() for lgt in not_illuminating])

    @_wrapperUndoChunck
    def setColorPicked(self,*args):
        """ Set lights color. """
        self.color_picked = cmds.colorSliderButtonGrp(self.colorPicker_csbtn,q=True,rgb=True)
        for light in self._onlyLightsFromSelection():
            pm.setAttr("%s.color" % light, self.color_picked)
            _logger.info("Color : %s" % self.color_picked)

    @_wrapperUndoChunck
    def transfertLightAttrs(self,*args):
        """ Transfert attributes from first light selected to others light(s) selected. """
        # Get lights
        lights = self._onlyLightsFromSelection(get_shapes=True)
        if not lights:
            return None

        driver = lights[0]
        slaves = lights[1:]
        copy_attr = None

        for attr_ in self.lgt_attrs:
            # Copy attributes
            if pm.objExists("%s.%s" % (driver, attr_)):
                copy_attr = pm.getAttr("%s.%s" % (driver, attr_))
            else:
                continue

            # Set attributes
            for slave in slaves:
                if pm.objExists("%s.%s" % (slave, attr_)):
                    pm.setAttr("%s.%s" % (slave, attr_), copy_attr)

        pm.select(slaves)
        _logger.info("%s attributes transfered to %s" % (driver.name(), [node.name() for node in slaves]))
        return True

    @_wrapperUndoChunck
    def createSet(self,*args):
        """ Create Set then put transform node selected. """
        # GET SELECTED
        include_type = ["mesh", "aiStandIn", "pgYetiMaya"]
        selected = pm.selected()
        pre_setname = selected[-1].name().split("_")[0]

        shapes = []
        for node in selected:
            shapes.extend([node for node in node.getChildren(ad=True, s=True) if pm.nodeType(node.name()) in include_type])

        transforms = [shape.getParent() for shape in shapes]

        if not transforms:
            _logger.warning("Invalid selection")
            return None

        # Prompt Dialog
        result = pm.promptDialog(
            title='Create Set',
            message='Name:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel',
            text=pre_setname,
        )

        if result == 'OK':
            input_ = pm.promptDialog(query=True, text=True)
        else:
            _logger.warning("Set need a name")
            return None

        # ROOT SET
        if pm.objExists("root_SETS"):
            root_set = pm.PyNode("root_SETS")
        else:
            pm.select(cl=True)
            root_set = pm.sets(n="root_SETS")

        # CREATE SET
        if re.search(r'[A-Za-z0-9_]+(_SETS)', input_) is None:
            input_ = "%s_SET" % input_

        pm.select(cl=True)
        set_ = pm.sets(n=input_)
        set_.addMembers(transforms)
        pm.sets(root_set, fe=set_)

        pm.select(selected)
        _logger.info("%s" % set_)
        return set_

    @_wrapperSelected
    def makeLightLinks(self,*args):
        """ cmds.MakeLightLinks Maya Command. Link only to transform. """
        selected = pm.selected()
        set_children = []
        for node in selected:
            if pm.nodeType(node) == "objectSet":
                set_children.extend(node.members(True))
                selected.remove(node)

        pm.select(selected)
        pm.select(set_children, add=True)
        pm.cmds.MakeLightLinks()
        _logger.info("lights linked")

    @_wrapperSelected
    def breakLightLinks(self,*args):
        """ cmds.BreakLightLinks Maya Command """
        selected = pm.selected()
        set_children = []
        for node in selected:
            if pm.nodeType(node) == "objectSet":
                set_children.extend(node.members(True))
                selected.remove(node)

        pm.select(selected)
        pm.select(set_children, add=True)
        pm.cmds.BreakLightLinks()
        _logger.info("lights breaked")

    def selectLinked(self,*args):
        """ Toggle function between:
            pm.cmds.SelectLightsIlluminatingObject()
            pm.cmds.SelectObjectsIlluminatedByLight()
        """
        selected = pm.selected()
        if not selected:
            _logger.warning("Nothing selected")
            return None

        if pm.nodeType(pm.selected()[0].getShape().name()) in self.lgt_types:
            pm.cmds.SelectObjectsIlluminatedByLight()
            if not pm.selected():
                _logger.warning("%s illuminate nothing" % [node.name() for node in selected])
                pm.select(selected)
                return None
        else:
            pm.cmds.SelectLightsIlluminatingObject()
            if not pm.selected():
                _logger.warning("%s is not illuminated" % [node.name() for node in selected])
                pm.select(selected)
                return None

        _logger.info("link : %s " % [node.name() for node in pm.selected()])
        return selected

    def breakAllLinks(self,*args):
        """ Unlink lights from all """
        lights = self._onlyLightsFromSelection()
        for light in lights:
            object_linked = pm.lightlink(q=True, light=light)
            pm.lightlink(light=light, object=object_linked, b=True)

        _logger.info("%s breaked from all" % [node.name() for node in lights])
        return light

    @_wrapperUndoChunck
    def transfertLightLinks(self,*args):
        """ Transfert all links from first light selected to others lights selected. """
        # Get lights selected
        lights = self._onlyLightsFromSelection()

        # Check light selection
        if not lights:
            _logger.warning("Nothing selected")
            return None

        elif len(lights) < 2:
            _logger.warning("Only one light selected")
            return None

        driver = lights[0]
        slaves = lights[1:]

        type_ = ["mesh", "aiStandIn", "pgYetiMaya"]
        object_linked = pm.lightlink(q=True, light=driver)
        sorted_link = [shape for shape in object_linked if pm.nodeType(shape) in type_]

        for slave in slaves:
            object_linked = pm.lightlink(light=slave)
            pm.lightlink(light=slave, object=object_linked, b=True)
            pm.lightlink(light=slave, object=sorted_link, m=True)

        pm.select(slaves)
        _logger.info("Link from %s copyied to %s" % (driver.name(), [slave.name() for slave in slaves]))
        return True

    def _getAllLights(self, get_shapes=False):
        lights = []
        for lgt_type in self.lgt_types:
            lights.extend(pm.ls(type=lgt_type))

        # Return if list is empty
        if not lights:
            _logger.warning("No lights in scene")
            return None

        # Get Transform if not 'get_shapes'
        if not get_shapes:
            lights = [shape.getParent() for shape in lights]

        _logger.debug("_getAllLights : %s" % lights)
        return lights

    def _onlyLightsFromSelection(self, get_shapes=False, all_hierachy=False):
        # Get either selection or selection + children
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
            if pm.nodeType(node.name()) in self.lgt_types:
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

    def colorOutlinerSelected(self, color_, enable=True,*args):
        """ Colorize Item selected in outliner. """
        # PREPROCESS
        selected = pm.selected()
        set_color = None
        if color_ == "red":
            set_color = (1.000, 0.500, 0.500)

        elif color_ == "orange":
            set_color = (0.900, 0.700, 0.400)

        elif color_ == "yellow":
            set_color = (1.000, 1.000, 0.500)

        elif color_ == "green":
            set_color = (0.600, 1.000, 0.400)

        elif color_ == "turquoise":
            set_color = (0.300, 1.000, 0.700)

        elif color_ == "cyan":
            set_color = (0.500, 1.000, 1.000)

        elif color_ == "blue":
            set_color = (0.300, 0.700, 1.000)

        elif color_ == "purple":
            set_color = (0.600, 0.400, 1.000)

        elif color_ == "magenta":
            set_color = (1.000, 0.500, 1.000)

        else:
            set_color = (0.000, 0.000, 0.000)

        # Return if selection is empty
        if not selected:
            _logger.warning("Nothing selected")
            return

        # Remove Color outliner
        if not enable:
            for node in selected:
                node.useOutlinerColor.set(False)
            _logger.info("Color Outliner disabled")
            pm.mel.eval("AEdagNodeCommonRefreshOutliners()")
            return

        # Set Color outliner
        for node in selected:
            node.useOutlinerColor.set(True)
            node.outlinerColor.set(set_color)

        pm.mel.eval("AEdagNodeCommonRefreshOutliners()")
        _logger.info("Color Outliner success")

class lighttoolsGroupName_widget(object):
    def __init__(self,parent_Lay,renderer):
        self.parent_Lay = parent_Lay
        self.renderer = renderer
        self.create_widget()
        
    def create_widget(self):
        self.lgn_lay = cmds.columnLayout(adj=True,p=self.parent_Lay)
        self.lgn_name_le = cmds.textFieldGrp(cw=[[1, 40]],adj=2,l=u'Name: ')
        self.lgn_sep = cmds.separator(h=10)
        self.lgn_btn = cmds.button(h=30,l=u'Set Light Group Name',
                        c=partial(self.set_light_group_name,self.renderer))
        cmds.setParent("..")

    def set_light_group_name(self,*args):
        sel_shapes = cmds.ls(sl=True,dag=True,fl=True,s=True)
        lgn_tx = cmds.textFieldGrp(self.lgn_name_le,q=True,tx=True)

        for s in range(len(sel_shapes)):
            if self.renderer == "arnold":
                if cmds.objExists("%s.aiAov"% sel_shapes[s]):
                    cmds.setAttr("%s.aiAov"% sel_shapes[s] ,lgn_tx,type="string" ) 
            if self.renderer == "redshift":
                if cmds.objExists("%s.aovLightGroup"% sel_shapes[s]):
                    cmds.setAttr("%s.aovLightGroup"% sel_shapes[s] ,lgn_tx,type="string" ) # rsAovLightGroup
                elif cmds.objExists("%s.rsAovLightGroup"% sel_shapes[s]):
                    cmds.setAttr("%s.rsAovLightGroup"% sel_shapes[s] ,lgn_tx,type="string" )

class reset_attri_widget(object):
    def __init__(self,reset_le,attr_name,attr_v,parent_Lay):
        self.reset_le = reset_le
        self.attr_v = attr_v
        self.attr_name = attr_name
        self.parent_Lay = parent_Lay

        self.create_attri_widgets()
    
    def create_attri_widgets(self):
        self.ar_reset_attri_rowlay = cmds.rowLayout("ar_reset_attri_rowlay",bgc = [0.2,0.2,0.2],
                                        nc = 2,p=self.parent_Lay,
                                        cw = [[2, 100]],adj=1)
        self.attr_le = cmds.text(w=100,bgc=[0.1, 0.1, 0.1],al='center',l=self.reset_le[0])
        self.attr_reset_btn = cmds.button(w = 70,l=self.reset_le[1],c=partial(self.reset_all_attris))

    def reset_all_attris(self,*args):
        for sel in cmds.ls(sl=True,dag=True,fl=True,s=True):
            for attri in range(len(self.attr_name)):
                cmds.setAttr(("{0}.{1}".format(sel,self.attr_name[attri][1])),self.attr_v[attri])

class attri_control_widget(object):
    def __init__(self, type_le,attr_v,parent_Lay):
        self.type_le = type_le
        self.attr_v = attr_v
        self.parent_Lay = parent_Lay

        self.turn_off = LightCustomPreset.TURN_ATTRI_POWER

        self.create_attri_widgets()
    
    def create_attri_widgets(self):
        self.optRowLay = cmds.rowLayout(("{0}_rowLay".format(self.type_le)),bgc = [0.2,0.2,0.2],
                                        nc = 3,p=self.parent_Lay,
                                        cw = [[2, 100], [3, 100]],adj=1)
        self.attr_le = cmds.text(w=100,bgc=[0.4, 0.4, 0.4],al='center',l=self.type_le)
        self.attr_on_btn = cmds.button(w = 70,l=self.turn_off[0],c=partial(self.set_attri_on_modified))
        self.attr_off_btn = cmds.button(w = 70,l=self.turn_off[1],c=partial(self.set_attri_off_modified))
        cmds.setParent("..")

    def set_attri_on_modified(self,*args):
        self.sels = cmds.ls(sl=True,dag=True,fl=True,s=True)
        if self.sels:
            for sel in range(len(self.sels)):
                cmds.setAttr("{0}.{1}".format(self.sels[sel],self.attr_v),1)

    def set_attri_off_modified(self,*args):
        self.sels = cmds.ls(sl=True,dag=True,fl=True,s=True)
        if self.sels:
            for sel in range(len(self.sels)):
                cmds.setAttr("{0}.{1}".format(self.sels[sel],self.attr_v),0)

class lighttoolsUi(object):

    WINDOW_TITLE = "Light Tools"
    UI_NAME = "lighttools"

    WINDOW_SIZE = [380,655]

    @classmethod
    def get_workspace_control_name(cls):
        return "{0}WorkspaceControl".format(cls.UI_NAME)
    
    def __init__(self):
        super(lighttoolsUi, self).__init__()

        self.default_light_type = LightCustomPreset.DEFAULT_LIGHT_TYPE
        self.ar_light_type = LightCustomPreset.ARNOLD_LIGHT_TYPE
        self.rs_light_type = LightCustomPreset.REDSHIFT_LIGHT_TYPE
        
        self.windowObjName = "{0}WorkspaceControl".format(lighttoolsUi.UI_NAME)

        self.mainwindow()
        self.create_widget()
        self.create_layout()
        self.create_attri_widget()

        if lighttoolsUtils.ar_load_plugin():
            cmds.checkBoxGrp('render_cb',e=True,v1=True)

        if lighttoolsUtils.rs_load_plugin():
            cmds.checkBoxGrp('render_cb',e=True,v2=True)

        cmds.window(self.windowObjName,e=True,wh=lighttoolsUi.WINDOW_SIZE)

    def mainwindow(self):
        cmds.window(self.windowObjName,s=False,t=lighttoolsUi.WINDOW_TITLE)
        cmds.showWindow(self.windowObjName)

    def create_layout(self):

        main_layout = cmds.formLayout('main_layout')
        self.main_tab_lay = cmds.tabLayout('main_tab_lay',scr=True,cr=True)
        default_tab_lay = cmds.columnLayout(adj=True, p=self.main_tab_lay)
        arnold_tab_lay = cmds.columnLayout(adj=True, p=self.main_tab_lay)
        redshift_tab_lay = cmds.columnLayout(adj=True, p=self.main_tab_lay)

        self.default_lig_frame_lay = cmds.frameLayout(cll=True,l=u'Light',p=default_tab_lay)
        self.default_renstats_frame_lay = cmds.frameLayout(cll=True,l=u'Render Stats',p=default_tab_lay)
        self.default_renstats_scrol_lay = cmds.scrollLayout(h=260,cr=True,p=self.default_renstats_frame_lay)
        self.default_lig_row_lay = cmds.formLayout(p=self.default_lig_frame_lay)

        self.ar_lig_frame_lay = cmds.frameLayout(cll=True,l=u'Light',p=arnold_tab_lay)
        self.ar_renstats_frame_lay = cmds.frameLayout(cll=True,l=u'Render Stats',p=arnold_tab_lay)
        self.ar_renstats_scrol_lay = cmds.scrollLayout(h=260,cr=True,p=self.ar_renstats_frame_lay)
        self.ar_ligObjGrp_frame_lay = cmds.frameLayout(cll=True,l=u'Light Group Name',p=arnold_tab_lay)
        self.ar_lig_row_lay = cmds.formLayout(p=self.ar_lig_frame_lay)
        lighttoolsGroupName_widget(self.ar_ligObjGrp_frame_lay,"arnold")

        self.rs_lig_frame_lay = cmds.frameLayout(cll=True,l=u'Light',p=redshift_tab_lay)
        self.rs_renstats_frame_lay = cmds.frameLayout(cll=True,l=u'Render Stats',p=redshift_tab_lay)
        self.rs_renstats_scrol_lay = cmds.scrollLayout(h=260,cr=True,p=self.rs_renstats_frame_lay)
        self.rs_ligObjGrp_frame_lay = cmds.frameLayout(cll=True,l=u'Light Group Name',p=redshift_tab_lay)
        self.rs_lig_row_lay = cmds.formLayout(p=self.rs_lig_frame_lay)
        lighttoolsGroupName_widget(self.rs_ligObjGrp_frame_lay,"redshift")
        lighttoolsSetting_widget(self.main_tab_lay)

        cmds.formLayout(main_layout,e=1,
                        af=[[self.ren_pulgin_cb, 'top', 5], 
                            [self.ren_pulgin_cb, 'left', 5], 
                            [self.ren_pulgin_cb, 'right', 5], 
                            [self.main_tab_lay, 'left', 5], 
                            [self.main_tab_lay, 'right', 5], 
                            [self.main_tab_lay, 'bottom', 5]],
                        ac=[[self.main_tab_lay, 'top', 5, self.ren_pulgin_cb]])

        cmds.tabLayout(self.main_tab_lay,e=True,
                        tli = [(1,"Default"),
                            (2,"Arnold"),
                            (3,"Redshift"),
                            (4,"Opt")])

    def create_widget(self):

        self.ren_pulgin_cb = cmds.checkBoxGrp('render_cb',ncb=2,
                                            l1=u'Arnold Plugin',l2=u'Redshift Plugin',
                                            on1=partial(self.set_load_plugin,1),
                                            on2=partial(self.set_load_plugin,2),
                                            adj=1)

    def create_attri_widget(self):
        self.default_attris = LightCustomPreset.DEFAULT_ATTRI_LOOKUP
        self.arnold_attris = LightCustomPreset.ARNOLD_ATTRI_LOOKUP
        self.redshift_attris = LightCustomPreset.REDSHIFT_ATTRI_LOOKUP
        
        getIcon = lambda icon_name : (os.path.join(script_path,  "icon", icon_name))

        default_distance = 100/len(self.default_light_type.keys())
        for k in range(len(self.default_light_type.keys())):
            distance = default_distance*k
            btn_icon = self.default_light_type.get(self.default_light_type.keys()[k])[0]
            default_lig = cmds.iconTextButton(('%s_default_lig' % self.default_light_type.keys()[k]), i=getIcon(btn_icon),
                                                    p=self.default_lig_row_lay,
                                                    st='iconAndTextVertical',
                                                    c=partial(self.create_default_light,self.default_light_type.keys()[k]))
            cmds.formLayout(self.default_lig_row_lay,e=True,
                                af=[[default_lig,'top',5]],
                                ap=[[default_lig,'left',2,distance]])

        ar_distance = 100/len(self.ar_light_type.keys())
        for ar_k in range(len(self.ar_light_type.keys())):
            btnar_icon = self.ar_light_type.get(self.ar_light_type.keys()[ar_k])[0]
            btnar_type1 = self.ar_light_type.get(self.ar_light_type.keys()[ar_k])[1]
            btnar_type2 = self.ar_light_type.keys()[ar_k]
            ardefault_lig = cmds.iconTextButton(('%s_ar_lig' % self.ar_light_type.keys()[ar_k]), i=getIcon(btnar_icon),
                                                    p=self.ar_lig_row_lay,
                                                    st='iconAndTextVertical',
                                                    c=partial(self.create_arnold_light,btnar_type1,btnar_type2))
            cmds.formLayout(self.ar_lig_row_lay,e=True,
                                af=[[ardefault_lig,'top',5]],
                                ap=[[ardefault_lig,'left',2,ar_distance*ar_k]])
                                        
        rs_distance = 100/len(self.rs_light_type.keys())
        for rs_k in range(len(self.rs_light_type.keys())):
            btnrs_icon = self.rs_light_type.get(self.rs_light_type.keys()[rs_k])[0]
            btnrs_type1 = self.rs_light_type.get(self.rs_light_type.keys()[rs_k])[1]
            btnrs_type2 = self.rs_light_type.get(self.rs_light_type.keys()[rs_k])[2]
            rsdefault_lig = cmds.iconTextButton(('%s_rs_lig' % self.rs_light_type.keys()[rs_k]), i=getIcon(btnrs_icon),
                                                    p=self.rs_lig_row_lay,
                                                    st='iconAndTextVertical',
                                                    c=partial(self.create_redshift_light,btnrs_type1,btnrs_type2))
            cmds.formLayout(self.rs_lig_row_lay,e=True,
                                af=[[rsdefault_lig,'top',5]],
                                ap=[[rsdefault_lig,'left',2,rs_distance*rs_k]])


        for def_attri in self.default_attris:
            attri_control_widget(def_attri[0],def_attri[1],self.default_renstats_scrol_lay)    
        reset_attri_widget(LightCustomPreset.ATTRI_RESET_LEBAL,
                            self.default_attris,
                            LightCustomPreset.DEFAULT_ATTRI_VALUE,
                            self.default_renstats_scrol_lay)

        for ar_attri in self.arnold_attris:
            attri_control_widget(ar_attri[0],ar_attri[1],self.ar_renstats_scrol_lay)
        reset_attri_widget(LightCustomPreset.ATTRI_RESET_LEBAL,
                            self.arnold_attris,
                            LightCustomPreset.ARNOLD_ATTRI_DEFAULT_VALUE,
                            self.ar_renstats_scrol_lay)

        for rs_attri in self.redshift_attris:
            attri_control_widget(rs_attri[0],rs_attri[1],self.rs_renstats_scrol_lay)
            
        reset_attri_widget(LightCustomPreset.ATTRI_RESET_LEBAL,
                            self.arnold_attris,
                            LightCustomPreset.REDSHIFT_ATTRI_DEFAULT_VALUE,
                            self.rs_renstats_scrol_lay)

    def set_load_plugin(self,*args):
        if args == 1:
            lighttoolsUtils.ar_load_plugin()
            cmds.checkBoxGrp('render_cb',e=True,v1=True)
        if args == 2:
            lighttoolsUtils.rs_load_plugin()
            cmds.checkBoxGrp('render_cb',e=True,v2=True)

    def create_default_light(self,kind,*args):

        if kind == 'spot':
            new_light = cmds.spotLight()
        elif kind == 'dir':
            new_light = cmds.directionalLight()
        elif kind == 'point':
            new_light = cmds.pointLight()
        elif kind == 'amb':
            new_light = cmds.ambientLight()
        elif kind == 'area':
            new_light = cmds.shadingNode ('areaLight', asLight=True)
        return new_light

    def create_arnold_light(self,*args):
        self.arlight = cmds.shadingNode(args[0], al=True, n=("%sShape" % args[0]))
        if args[1] == "physicalsky":
            ar_physicalsky = cmds.shadingNode("aiPhysicalSky", al=True, n=("%s_aiphysky" % args[1]))
            cmds.connectAttr("%s.outColor"%(ar_physicalsky),
                            "%s.color"%(self.arlight),f=True)
           
    def create_redshift_light(self,*args):
        self.light = cmds.shadingNode(args[1], al=True, n=("%sShape" % args[0]))
        self.light_type = {'directionalLight':3,'areaLight':0,'pointLight':1,'spotLight':2}
        if self.light :
            if self.light in self.light_type.keys():
                cmds.setAttr(("%s.lightType" % self.light),self.light_type[self.light])

if __name__ == "__main__":

    workspace_control_name = lighttoolsUi.get_workspace_control_name()
    if cmds.window(workspace_control_name,ex=True):
        cmds.deleteUI(workspace_control_name)

    zap_test_ui = lighttoolsUi()
