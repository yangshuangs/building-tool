import bmesh
from ...utils import (split, get_edit_mesh)
from ..fill import (fill_bar, fill_louver, fill_glass_panes)


def make_window(bm, faces, **kwargs):
    """创建窗户"""
    for face in faces:
        if face.normal.z:
            continue
        face = make_window_split(bm, face, **kwargs)
        if not face:
            continue
        face = make_window_frame(bm, face, **kwargs)
        make_window_fill(bm, face, **kwargs)


def make_window_split(bm, face, size, off, **kwargs):
    """
    将窗户面进行分割
    :param bm: 
    :param face: 
    :param size: (vector2)新面与旧面的比例
    :param off: (vector3)新面与中心的距离
    """
    return split(bm, face, size.y, size.x, off.x, off.y, off.z)


def make_window_frame(bm, face, ft, fd, **kwargs):
    """
    创建窗户基础形状
    :param fd:(float)Depth of the window frame
    :param ft:(float)thickness of the window frame
    """
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts))
    face = bmesh.ops.extrude_discrete_faces(bm, faces=[face]).get('faces')[-1]
    bmesh.ops.translate(bm, verts=face.verts, vec=face.normal*fd/2)
    if ft:
        bmesh.ops.inset_individual(bm, faces=[face], thickness=ft)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if fd:
        f = bmesh.ops.extrude_discrete_faces(bm, faces=[face]).get('faces')[-1]
        bmesh.ops.translate(bm, verts=f.verts, vec=-f.normal*fd)

        return f
    return face


def make_window_fill(bm, face, fill_type, **kwargs):
    """窗户面填充"""
    if fill_type == 'NONE':
        pass
    elif fill_type == 'GLASS PANES':
        fill_glass_panes(bm, face, **kwargs)
    elif fill_type == 'BAR':
        fill_bar(bm, face, **kwargs)
    elif fill_type == 'LOUVER':
        fill_louver(bm, face, **kwargs)
