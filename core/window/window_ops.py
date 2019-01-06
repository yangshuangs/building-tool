import bpy
from .window import Window
from .window_props import WindowPrperty


class WindowOperator(bpy.types.Operator):
    """Creates windows on selected mesh faces"""
    # 在选定网格内创建窗户
    bl_idname = "cynthia.add_window"
    bl_label = "Add window"
    bl_options = {'REGISTER', 'UNDO'}

    props = bpy.props.PointerProperty(type=WindowPrperty)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.mode == 'EDIT_MESH'

    def execute(self, context):
        return Window.build(context, self.props)

    def draw(self, context):
        self.props.draw(context, self.layout)
