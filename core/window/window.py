import bmesh
from .window_types import make_window
from ...utils import (get_edit_mesh, kwargs_from_props)


class Window:

    @classmethod
    def build(cls, context, props):
        me = get_edit_mesh()
        bm = bmesh.from_edit_mesh(me)
        faces = [face for face in bm.faces if face.select]  # 找出被选中的面

        if cls.validate(faces):
            make_window(bm, faces, **kwargs_from_props(props))
            bmesh.update_edit_mesh(me, True)
            return {'FINISHED'}
        return {'CANCELLED'}

    @classmethod
    def validate(cls, faces):
        if faces:
            if not any([f.normal.z for f in faces]):
                return True
        return False
