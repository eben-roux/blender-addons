# Repeats extrusion, rotation, scale, movement for one or more faces.
# borrowed from user liero (http://blenderartists.org/forum/showthread.php?219526-Multiple-extrusions-script)
# original source: http://dl.dropbox.com/u/16486113/Blender/mexii.py

bl_info = {
    "name": "Simple Extrude",
    "version": (1, 0, 0),
    "blender": (2, 74, 0),
    "location": "View3D > Tool Shelf",
    "description": "Repeat extrusions from faces.",
    'warning': '',
    "category": "Mesh"}
 
import bpy, bmesh, random
from random import gauss
from math import radians
from mathutils import Euler
from bpy.props import FloatProperty, IntProperty
 
def vloc(self, r):
    random.seed(self.ran + r)
    return self.extrude_offset * (1 + random.gauss(0, self.var1 / 3))
 
def vrot(self, r):
    random.seed(self.ran + r)
    return Euler((radians(self.rotx) + random.gauss(0, self.var2 / 3), \
        radians(self.roty) + random.gauss(0, self.var2 / 3), \
        radians(self.rotz) + random.gauss(0,self.var2 / 3)), 'XYZ')
 
def vsca(self, r):
    random.seed(self.ran + r)
    return self.sca * (1 + random.gauss(0, self.var3 / 3))
 
class SimpleExtrude(bpy.types.Operator):
    bl_idname = 'object.simpleextrude'
    bl_label = 'Simple Extrude'
    bl_description = 'Simple Extrude'
    bl_options = {'REGISTER', 'UNDO'}
 
    extrude_offset = FloatProperty(name='Offset', min=-2, soft_min=0.001, \
        soft_max=2, max=5, default=.5, description='Translation')
    rotx = FloatProperty(name='Rot X', min=-85, soft_min=-30, \
        soft_max=30, max=85, default=0, description='X rotation')
    roty = FloatProperty(name='Rot Y', min=-85, soft_min=-30, \
        soft_max=30, max=85, default=0, description='Y rotation')
    rotz = FloatProperty(name='Rot Z', min=-85, soft_min=-30, \
        soft_max=30, max=85, default=-0, description='Z rotation')
    offsetx = FloatProperty(name='Offset X', min=-85, soft_min=-30, \
        soft_max=30, max=85, default=0, description='X offset')
    offsety = FloatProperty(name='Offset Y', min=-85, soft_min=-30, \
        soft_max=30, max=85, default=0, description='Y offset')
    offsetz = FloatProperty(name='Offset Z', min=-85, soft_min=-30, \
        soft_max=30, max=85, default=-0, description='Z offset')
    sca = FloatProperty(name='Scale', min=0.1, soft_min=0.5, \
        soft_max=1.2, max =2, default=.9, description='Scaling')
    var1 = FloatProperty(name='Offset Var', min=-5, soft_min=-1, \
        soft_max=1, max=5, default=0, description='Offset variation')
    var2 = FloatProperty(name='Rotation Var', min=-5, soft_min=-1, \
        soft_max=1, max=5, default=0, description='Rotation variation')
    var3 = FloatProperty(name='Scale Noise', min=-5, soft_min=-1, \
        soft_max=1, max=5, default=0, description='Scaling noise')
    num = IntProperty(name='Repeat', min=1, max=50, soft_max=100, \
        default=5, description='Repetitions')
    ran = IntProperty(name='Seed', min=-9999, max=9999, default=0, \
        description='Seed to feed random values')
 
    @classmethod
    def poll(cls, context):
        obj = context.object
        return (obj and obj.type == 'MESH')
 
    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)
        column.label(text='Transformations:')
        column.prop(self, 'extrude_offset', slider=True)
        column.prop(self, 'rotx', slider=True)
        column.prop(self, 'roty', slider=True)
        column.prop(self, 'rotz', slider=True)
        column.prop(self, 'sca', slider=True)
        column = layout.column(align=True)
        column.label(text='Offsets:')
        column.prop(self, 'offsetx', slider=True)
        column.prop(self, 'offsety', slider=True)
        column.prop(self, 'offsetz', slider=True)
        column = layout.column(align=True)
        column.label(text='Variation settings:')
        column.prop(self, 'var1', slider=True)
        column.prop(self, 'var2', slider=True)
        column.prop(self, 'var3', slider=True)
        column.prop(self, 'ran')
        column = layout.column(align=False)
        column.prop(self, 'num')
 
    def execute(self, context):
        obj = bpy.context.object
        data = obj.data
        mode = obj.mode
        bpy.context.tool_settings.mesh_select_mode = [False, False, True]
 
        # bmesh operations
        bpy.ops.object.mode_set()
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        selectedFaces = [f for f in bm.faces if f.select]
 
        # faces loop
        for i, selectedFace in enumerate(selectedFaces):
            rot = vrot(self, i)
            extrude_offset = vloc(self, i)
            selectedFace.normal_update()
 
            # extrusion loop
            for r in range(self.num):
                newFace = selectedFace.copy()
                newFace.normal_update()
                newFaceNormal = newFace.normal.copy()
                newFaceCenterBounds = newFace.calc_center_bounds()
                s = vsca(self, i + r)
 
                for v in newFace.verts:
                    v.co -= newFaceCenterBounds
                    v.co.rotate(rot)
                    v.co += newFaceCenterBounds + newFaceNormal * extrude_offset
                    v.co = v.co.lerp(newFaceCenterBounds, 1 - s)
 
                # extrude code from TrumanBlending
                for a, b in zip(selectedFace.loops, newFace.loops):
                    sf = bm.faces.new((a.vert, a.link_loop_next.vert, \
                        b.link_loop_next.vert, b.vert))
                    sf.normal_update()
 
                bm.faces.remove(selectedFace)
                newFace.select_set(True)
                selectedFace = newFace
 
        for v in bm.verts: v.select = False
        for e in bm.edges: e.select = False
        bm.to_mesh(obj.data)
        obj.data.update()
 
        # restore user settings
        bpy.ops.object.mode_set(mode=mode)
 
        if not len(selectedFaces):
            self.report({'INFO'}, 'Select one or more faces...')
        return{'FINISHED'}
 
class SimpleExtrudeToolButton(bpy.types.Panel):
    bl_label = 'Simple Extrude'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
 
    def draw(self, context):
        layout = self.layout
        layout.operator('object.simpleextrude')
 
def register():
    bpy.utils.register_class(SimpleExtrude)
    bpy.utils.register_class(SimpleExtrudeToolButton)
 
def unregister():
    bpy.utils.unregister_class(SimpleExtrude)
    bpy.utils.unregister_class(SimpleExtrudeToolButton)
 
if __name__ == '__main__':
    register()
