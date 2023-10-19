import maya.cmds as cmds
from PySide2 import QtWidgets, QtGui, QtCore
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

# UI Stuff

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class BuildFenceUI(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(BuildFenceUI, self).__init__(parent)

        self.setWindowTitle("Fence Builder!")
        self.setFixedSize(250, 150)

        self.fence_count = 0

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        title_label = QtWidgets.QLabel("Fence Builder!")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_font = QtGui.QFont()
        title_font.setBold(True)
        title_label.setFont(title_font)

        self.normal_fence_radio = QtWidgets.QRadioButton("Normal Fence")
        self.scalloped_fence_radio = QtWidgets.QRadioButton("Scalloped Fence")

        self.counter_label = QtWidgets.QLabel("Fences Built: 0")
        self.counter_label.setAlignment(QtCore.Qt.AlignCenter)

        self.build_fence_button = QtWidgets.QPushButton("Build Fence")

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.normal_fence_radio)
        main_layout.addWidget(self.scalloped_fence_radio)
        main_layout.addWidget(self.counter_label)
        main_layout.addWidget(self.build_fence_button)

    def create_layouts(self):
        pass

    def create_connections(self):
        self.build_fence_button.clicked.connect(self.on_build_fence_clicked)
        self.normal_fence_radio.toggled.connect(self.on_fence_type_changed)
        self.scalloped_fence_radio.toggled.connect(self.on_fence_type_changed)

    def on_build_fence_clicked(self):
        x_offset = self.fence_count * 26
        if self.normal_fence_radio.isChecked():
            build_normal_fence(x_offset)
        elif self.scalloped_fence_radio.isChecked():
            build_scalloped_fence(x_offset)
        self.fence_count += 1

        self.counter_label.setText(f"Fences Built: {self.fence_count}")

    def on_fence_type_changed(self):
        pass

#Fence functions for the radio buttons

def build_normal_fence(x_offset=0):
    p_width = 0.4
    p_height = 4.0
    p_depth = 0.1
    p_spacing = 0.5
    num_pickets = 10
    p_name = "picket#"
    cross_section_height = 0.4
    cross_section_depth = 0.15
    num_cross_sections = 2
    cross_section_offset = 0.4
    cross_section_spacing = 2.0
    cross_section_name = "crossSection#"
    num_fence_sections = 3
    section_spacing = 0.2
    fence_section_group_name = "fenceSection#"
    fence_sections = []

    for x in range(num_fence_sections):
        pickets = build_pickets(p_width, p_height, p_depth, p_spacing, p_name, num_pickets)
        fence_section_group = cmds.group(empty=True, world=True, n=fence_section_group_name)
        group_objects(pickets, fence_section_group)

        cross_sections = build_cross_sections(cross_section_height, cross_section_depth, num_cross_sections,
                                              fence_section_group, cross_section_name, cross_section_offset,
                                              cross_section_spacing)
        group_objects(cross_sections, fence_section_group)
        fence_sections.append(fence_section_group)

    for i in range(len(fence_sections)):
        section_width, section_height, section_depth = get_dimensions(fence_sections[i])
        cmds.move((section_width + section_spacing) * i + x_offset, fence_sections[i], moveX=True)
        cmds.select(clear=True)

def build_pickets(pw, ph, pd, ps, pn, num_pickets):
    pickets = []
    for x in range(num_pickets):
        picket = cmds.polyCube(w=pw, h=ph, d=pd, ch=False, name=pn)
        picket = picket[0]
        cmds.move(ph / 2, picket, moveY=True)
        cmds.move(pw / 2, picket, moveX=True)
        pickets.append(picket)
    for x in range(len(pickets)):
        cmds.move((pw + ps) * x, pickets[x], moveX=True, relative=True)
    cmds.select(clear=True)
    return pickets

def build_cross_sections(cs_height, cs_depth, num_cs, fence_section_group, cs_name, cs_offset, cs_spacing):
    section_width, section_height, section_depth = get_dimensions(fence_section_group)
    cross_sections = []
    for x in range(num_cs):
        cs = cmds.polyCube(w=section_width, h=cs_height, d=cs_depth, ch=False, name=cs_name)
        cs = cs[0]
        cmds.move(section_width / 2.0, cs, moveX=True)
        cmds.move(cs_height / 2.0, cs, moveY=True)
        cmds.move(-cs_depth / 2.0, cs, moveZ=True)
        cmds.move(-section_depth / 2.0, cs, moveZ=True, relative=True)
        cross_sections.append(cs)
    for x in range(num_cs):
        cmds.move(((cs_height + cs_spacing) * x) + cs_offset, cross_sections[x], moveY=True, relative=True)
    cmds.select(clear=True)
    return cross_sections

def get_boundingbox(obj):
    xmin, ymin, zmin, xmax, ymax, zmax = cmds.xform(obj, query=True, bb=True)
    return xmin, ymin, zmin, xmax, ymax, zmax

def get_dimensions(obj):
    bb = get_boundingbox(obj)
    width = round(bb[3] - bb[0], 5)
    height = round(bb[4] - bb[1], 5)
    depth = round(bb[5] - bb[2], 5)
    return width, height, depth

def group_objects(objects, the_group):
    for each in objects:
        cmds.parent(each, the_group)

import maya.cmds as cmds


def build_scalloped_fence(x_offset=0):
    pickets = []
    for x in range(10):
        p = cmds.polyCube(w=1.0, d=0.2, h=5.0, ch=False, name="picket#")
        cmds.move((1.0 + 0.2) * x + x_offset, 5.0 / 2, 0, p, absolute=True)
        pickets.append(p[0])

    for each in pickets:
        cmds.select(each, add=True)

    lattice = cmds.lattice(divisions=(3, 3, 2), objectCentered=True)
    cmds.select(lattice[1] + ".pt[1][2][0:1]", r=True)
    cmds.move(2.0, moveY=True, relative=True)

    for each in pickets:
        cmds.select(each, add=True)

    cmds.delete(constructionHistory=True)
    cmds.select(clear=True)

try:
    ui.close()
except:
    pass

ui = BuildFenceUI()
ui.show()
