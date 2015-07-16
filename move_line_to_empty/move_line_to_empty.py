bl_info = {
	"name": "Move line to empty",
	"category": "Object"}

import bpy
from bpy.types import Operator
from mathutils import Matrix

class OBJECT_OT_move_line_to_empty(Operator):
	bl_idname = "mesh.move_line_to_empty"
	bl_label = "Move line to empty"
	bl_options = {'REGISTER', 'UNDO'}

	percentage = bpy.props.FloatProperty(name="Percentage", default=100, min=0, max=100, step=10)

	def execute(self, context):
		empty = bpy.data.objects["empty"]
		line = bpy.data.objects["line"]
		
		mw = line.matrix_world
		ev = empty.location
		
		lv0 = mw * line.data.vertices[0].co
		lv1 = mw * line.data.vertices[1].co
		
		lv = (lv0 - lv1)
		
		evt = Matrix.Translation(lv - lv0) * ev
		
		evp = evt.project(lv)
		
		tm = Matrix.Translation((evp - evt) * self.percentage / 100).inverted()

		line.location = tm * line.location

		return {'FINISHED'}

# This allows you to right click on a button and link to the manual
def register():
	bpy.utils.register_class(OBJECT_OT_move_line_to_empty)


def unregister():
	bpy.utils.unregister_class(OBJECT_OT_move_line_to_empty)

	
if __name__ == "__main__":
	register()
