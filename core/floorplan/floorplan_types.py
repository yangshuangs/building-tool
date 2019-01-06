import bmesh
import random
from bmesh.types import BMVert
from mathutils import Vector, Matrix
from ...utils import (
    clamp,
    plane,
    circle,
    filter_geom,
    calc_edge_median,   # 计算边的中点
    filter_vertical_edges,
    filter_horizontal_edges
)

# 创建不同形状地板平面图的操作

def fp_rectangular(bm, width, length, **kwargs):
    """
    :param bm: (bmesh.types.BMesh)创建方形的网格
    :param width: (float)
    :param length: (float)
    :param kwargs: 
    :return: 
    """
    plane(bm, width, length)


def fp_circular(bm, radius, segs, cap_tris, **kwargs):
    """
    :param bm: (bmesh.types.BMesh)创建圆形的网格
    :param radius: (float)圆形半径
    :param segs: (int)圆形划分多少部分
    :param cap_tris: (bool)是否用三角形填充圆形
    :param kwargs: 
    :return: 
    """
    circle(bm, radius, segs, cap_tris)


def fp_composite(bm, width, length, tl1, tl2, tl3, tl4, **kwargs):
    """
    由4个矩形构建十字架形状
    :param bm: 
    :param width: (float)内部矩形宽
    :param length: (float)内部矩形长
    :param tl1: (float)底部长
    :param tl2: (float)左侧长
    :param tl3: (float)右侧长
    :param tl4: (float)顶部长
    """
    base = plane(bm, width, length)
    ref = list(bm.faces)[-1].clac_center_median()

    edges = list(bm.edges)
    edges.sort(key=lambda ed: calc_edge_median(ed).x)
    edges.sort(key=lambda ed: calc_edge_median(ed).y)

    # 矩形外部参数
    exts = [tl1, tl2, tl3, tl4]
    for idx, e in enumerate(edges):
        if exts[idx] > 0:
            res = bmesh.ops.extrude_edge_only(bm, edges=[e])
            verts = filter_geom(res['geom'], BMVert)

            v = (calc_edge_median(e) - ref)
            v.normalize()
            bmesh.ops.translate(bm, verts=verts, vec=v * exts[idx])


def fp_hshaped(bm, width, length, tl1, tl2, tl3, tl4, tw1, tw2, tw3, tw4, **kwargs):
    """
    创建 H形面板
    :param bm: 
    :param width: (float)内部矩形宽
    :param length: (float)内部矩形长
    :param tl1: (float)length bottom-left
    :param tl2: (float)length bottom-right
    :param tl3: (float)length top-left
    :param tl4: (float)length top-right
    :param tw1: (float)width bottom-left
    :param tw2: (float)width bottom-right
    :param tw3: (float)width top-left
    :param tw4: (float)width top-right
    """
    base = plane(bm, width, length)
    face = list(bm.faces)[-1]
    # calc_center_median()--返回面的中点, return: vector
    ref = face.calc_center_median()
    n = face.normal

    for e in filter_vertical_edges(bm.edges, n):
        # extrude_edge_only(bm, edges)--将边缘挤压成面, bm--操作的bmesh, edges--构成边的顶点序列
        res = bmesh.ops.extrude_edge_only(bm, edges=[e])
        verts = filter_geom(res['geom'], BMVert)

        v = (calc_edge_median(e) - ref)
        v.normalize()   # unit length vector--单位长度向量
        # translate()--通过偏移量转换顶点
        bmesh.ops.translate(bm, verts=verts, vec=v)

    # 筛选顶部的中间部分边
    op_edges = filter_horizontal_edges(bm.edges, n)
    op_edges.sort(key=lambda ed: calc_edge_median(ed).x)
    op_edges = op_edges[:2] + op_edges[4:]
    op_edges.sort(key=lambda ed: calc_edge_median(ed).y)
    lext = [tl1, tl2, tl3, tl4]
    wext = [tw1, tw2, tw3, tw4]

    for idx, e in enumerate(op_edges):
        if lext[idx] > 0:
            res = bmesh.ops.extrude_edge_only(bm, edges=[e])
            verts = filter_geom(res['geom'], BMVert)

            v = (calc_edge_median(e) - ref)
            v.normalize()

            flt_func = min if v.x > 0 else max
            mv1 = flt_func(list(e.verts), key=lambda v: v.co.x)
            mv2 = flt_func(verts, key=lambda v: v.co.x)

            bmesh.ops.translate(bm, verts=verts, vec=Vector((0, v.y, 0)) * lext[idx])
            bmesh.ops.translate(bm, verts=[mv1, mv2], vec=Vector((-v.x, 0, 0)) * wext[idx])


def fp_random(bm, seed, width, length, **kwargs):
    """
    创建随机形状的建筑地基
    :param bm: 
    :param seed: (int)
    :param width: 
    :param length: 
    """
    random.seed(seed)
    sc_x = Matrix.Scale(width, 4, (1, 0, 0))
    sc_y = Matrix.Scale(length, 4, (0, 1, 0))
    mat = sc_x * sc_y
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1, matrix=mat)
    # random.sample(sequence, k)，从指定序列中随机获取指定长度为k的片段。sample函数不会修改原有序列
    sample = random.sample(list(bm.edges), random.randrange(1, len(bm.edges)))
    ref = list(bm.faces)[-1].calc_center_median()
    for edge in sample:
        # 计算边的中心和长度
        cen = calc_edge_median(edge)
        elen = edge.calc_length()
        # 切割
        # subdivide_edges()-->Return type: dict with string keys:
        # -->geom_inner, geom_split, geom: contains all output geometry
        res = bmesh.ops.subdivide_edges(bm, edges=[edge], cuts=2)
        new_verts = filter_geom(res['geom_inner'], BMVert)
        # link_edges()-->Edges connected to this vertex
        new_edge = list(set(new_verts[0].link_edges) & set(new_verts[1].link_edges))[-1]

        # resize new edge
        axis = Vector((1, 0, 0)) if new_verts[0].co.y == new_verts[1].co.y else Vector((0, 1, 0))
        scale_factor = clamp(random.random() * elen/new_edge.calc_length(), 1, 2.95)
        bmesh.ops.scale(bm, verts=new_verts, vec=axis*scale_factor, space=Matrix.Translation(-cen))

        # offset
        if random.choice([0, 1]):
            max_offset = (elen - new_edge.calc_length()) / 2
            rand_offset = random.random() * max_offset
            bmesh.ops.translate(bm, verts=new_verts, vec=axis*rand_offset)

        # extrude
            res = bmesh.ops.extrude_edge_only(bm, edges=[new_edge])
            bmesh.ops.translate(
                bm,
                verts=filter_geom(res['geom'], BMVert),
                vec=(cen - ref).normalized() * random.randrange(1, int(elen/2))
            )
