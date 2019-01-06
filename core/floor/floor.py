import bmesh
from .floor_types import make_floors
from ...utils import (
    get_edit_mesh,
    kwargs_from_props
)


class Floor:

    @classmethod
    def build(cls, context, props):
        """利用floor types & props 生成几何"""
        me = get_edit_mesh()
        bm = bmesh.from_edit_mesh(me)

        if cls.validate(bm):
            if any([f for f in bm.faces if f.select]):
                make_floors(bm, None, **kwargs_from_props(props))
            else:
                edges = [e for e in bm.edges if e.is_boundry]
                make_floors(bm, edges, **kwargs_from_props(props))
            bmesh.update_edit_mesh(me, True)
            return {'FINISHED'}
        return {'CANCELLED'}

    @classmethod
    def validate(cls, bm):
        """???"""
        if len(list({v.co.z for v in bm.verts})) == 1:
            return True
        elif any([f for f in bm.faces if f.select]):
            return True
        return False
