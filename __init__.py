import bpy
from .core import register_core, unregister_core

bl_info = {
    "name": "Test Build Tools",
    "author": "PxGeng",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "View3D > Toolshelf > Test Build Tools",
    "description": "Building Test Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Cynthia"
}


class MeshGenerationPanel(bpy.types.Panel):
    """建筑操作以及属性设置的UI面板"""
    bl_idname = "VIEW3D_PT_cynthia"
    bl_label = "Mesh Generation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Test Tools"

    def draw(self, context):
        layout = self.layout
        active = context.object

        col = layout.column(align=True)
        col.operator("cynthia.add_floorplan")
        col.operator("cynthia.add_floors")

        row = col.row(align=True)
        row.operator("cynthia.add_window")
        row.operator("cynthia.add_door")

        row = col.row(align=True)
        row.operator("cynthia.add_railing")
        row.operator("cynthia.add_balcony")

        col.operator("cynthia.add_stairs")
        col.operator("cynthia.add_roof")


def register():
    bpy.utils.register_class(MeshGenerationPanel)
    register_core()


def unregister():
    bpy.utils.unregister_class(MeshGenerationPanel)
    unregister_core()

if __name__ == "__main__":
    import os
    os.system("clear")
    try:
        unregister()
    except Exception as e:
        pass
    finally:
        register()
