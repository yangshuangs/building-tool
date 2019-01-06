import bpy
import bmesh
import operator
import functools as ft
from mathutils import Matrix, Vector
from bmesh.types import BMVert


# verts-顶点, edges-边, faces-面
# 对网格进行操作

def get_edit_mesh():
    """获取编辑模式下的物体网格数据"""
    return bpy.context.edit_object.data


def make_mesh(name):
    """新建网格"""
    return bpy.data.meshes.new(name)


def select(elements, val=True):
    """选择元素"""
    for element in elements:
        element.select = val


def filter_geom(geom, _type):
    """lambda--匿名函数"""
    return list(filter(lambda x: isinstance(x, _type), geom))


def filter_vertical_edges(edges, normal):
    """
    round()方法--返回浮点数x的四舍五入值
    res--对垂直方向的边进行值精确化，返回为边的数组
    """
    res = []
    rnd = lambda val: round(val, 3)

    for e in edges:
        if normal.x:
            s = set([rnd(v.co.y) for v in e.verts])
        else:
            s = set([rnd(v.co.x) for v in e.verts])

        if len(s) == 1:
            res.append(e)
    return res


def filter_horizontal_edges(edges, normal):
    """处理水平方向的边"""
    res = []
    rnd = lambda val: round(val, 3)

    for e in edges:
        if normal.z:
            s = set([rnd(v.co.y) for v in e.verts])
        else:
            s = set([rnd(v.co.z) for v in e.verts])

        if len(s) == 1:
            res.append(e)
    return res


def calc_edge_median(edge):
    """计算边的中点"""
    # reduce() 可迭代物相加
    return ft.reduce(operator.add, [v.co for v in edge.verts])/len(edge.verts)


def calc_verts_median(verts):
    """计算多点中心"""
    return ft.reduce(operator.add, [v.co for v in verts])/len(verts)


def calc_face_dimensions(face):
    """计算面的长和宽"""
    vertical = filter_vertical_edges(face.edges, face.normal)[-1]
    horizontal = filter_horizontal_edges(face.edges, face.normal)[-1]
    return horizontal.calc_length(), vertical.calc_length()


def face_with_verts(bm, verts, default=None):
    """利用给定的顶点寻找对应的面"""
    for face in bm.faces:
        if len(set(list(face.verts) + verts)) == len(verts):
            return face
    return default


def split_quad(bm, face, vertical=False, cuts=4):
    """将四边形的边细分成均匀的水平/垂直切割"""
    res = None
    if vertical:
        e = filter_horizontal_edges(face.edges, face.normal)
        res = bmesh.ops.subdivide_edges(bm, edges=e, cuts=cuts)
    else:
        e = filter_vertical_edges(face.edges, face.normal)
        res = bmesh.ops.subdivide_edges(bm, edges=e, cuts=cuts)
    return res


def split(bm, face, svertical, shorizontal, offx=0, offy=0, offz=0):
    """将一个四元组分成规则的四个部分（通常是一个只有棱角直边的图形）"""
    scale = 3
    svertical *= scale
    shorizontal *= scale
    do_vertical = svertical < scale
    do_horizontal = shorizontal < scale
    face.select = False
    median = face.calc_center_median()

    if not do_horizontal and not do_vertical:
        return face

    # 水平方向分割 -- 边的顶点具有相同的Z坐标
    if do_horizontal:
        horizontal = list(filter(
            lambda e: len(set([round(v.co.z, 1) for v in e.verts])) == 1, face.edges
        ))
        sp_res = bmesh.ops.subdivide_edges(bm, edges=horizontal, cuts=2)
        verts = filter_geom(sp_res['geom_inner'], BMVert)

        T = Matrix.Translation(-median)
        bmesh.ops.scale(bm, vec=(shorizontal, shorizontal, 1), verts=verts, space=T)

    # 垂直方向分割 -- 边上的顶点具有相同的x/y坐标
    if do_vertical:
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts))
        face = face_with_verts(bm, verts) if do_horizontal else face

        # 判断垂直的边
        other = list(filter(
            lambda e: len(set([round(v.co.z, 1) for v in verts])) == 1,
            face.edges
        ))
        vertical = list(set(face.edges) - set(other))

        # 切分
        sp_res = bmesh.ops.subdivide_edges(bm, edges=vertical, cuts=2)
        verts = filter_geom(sp_res['geom_inner'], BMVert)

        # 计算切分的面
        T = Matrix.Translation(-median)
        bmesh.ops.scale(bm, vec=(1, 1, svertical), verts=verts, space=T)

    if do_horizontal and do_vertical:
        link_edges = [e for v in verts for e in v.link_edges]
        all_verts = list({v for e in link_edges for v in e.verts})
        bmesh.ops.translate(bm, verts=all_verts, vec=(offx, offy, 0))
    elif do_horizontal and not do_vertical:
        bmesh.ops.translate(bm, verts=verts, vec=(offx, offy, 0))

    bmesh.ops.translate(bm, verts=verts, vec=(0, 0, offz))

    face = face_with_verts(bm, verts)
    return face


def edge_split_offset(bm, edges, verts, offset, connect_verts=False):
    """对边进行分割，偏移量由顶点计算得到"""
    new_verts = []
    for idx, e in enumerate(edges):
        vert = verts[idx]
        _, v = bmesh.utils.edge_split(e, vert, offset / e.calc_length())
        new_verts.append(v)

    if connect_verts:
        res = bmesh.ops.connect_verts(bm, verts=new_verts).get('edges')
        return res
    return new_verts
