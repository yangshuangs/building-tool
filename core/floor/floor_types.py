import bmesh
import itertools as it
from bmesh.types import (
    BMVert, BMFace, BMEdge
)
from ...utils import (
    select, filter_geom
)


def make_floors(bm, edges, floor_count, floor_height,
                slab_thickness, slab_outset, **kwargs):
    """
    生成类似建筑楼层的挤压模型
    :param floor_count: (int)楼层数
    :param floor_height: (float)楼层高度
    :param slab_thickness: (float)楼板厚度
    :param slab_outset: (float)楼板外延部分长度
    :param kwargs: 
    """
    del_faces = []
    if not edges:
        # --检测选中的面的边缘
        del_faces = [f for f in bm.faces if f.select]
        all_edges = list({e for f in del_faces for e in f.edges})
        edges = [e for e in all_edges
                 if len(list({f for f in e.link_faces if f in del_faces})) == 1]

    # --extrude floor
    slab_faces = []

    # cycle()-->把传入的一个序列无限重复下去
    offsets = it.cycle([slab_thickness, floor_height])

    # islice(iterable, start, stop[, step])-->返回序列seq的从start开始到stop结束的步长为step的元素的迭代器
    # ???
    for offset in it.islice(offsets, 0, floor_count*2):
        if offset == 0 and offset == slab_thickness:
            continue
        ext = bmesh.ops.extrude_edge_only(bm, edges=edges)
        # ???translate
        bmesh.ops.translate(bm, vec=(0, 0, offset), verts=filter_geom(ext['geom'], BMVert))
        edges = filter_geom(ext['geom'], BMEdge)
        if offset == slab_thickness:
            slab_faces.extend(filter_geom(ext['geom'], BMFace))
    # --将面嵌入区域
    bmesh.ops.inset_region(bm, faces=slab_faces, depth=-slab_outset)
    # --上下文创建，从顶点创建新面，从边网生成东西，制作线边等
    bmesh.ops.contextual_create(bm, geom=edges)
    # --计算指定输入面的“外部”法线
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    if del_faces:
        bmesh.ops.delete(bm, geom=del_faces, context=5)     # ???context
        select(list(bm.edges), False)
