import bmesh
from mathutils import Vector, Matrix
from bmesh.types import BMEdge, BMVert
from ...utils import (
    filter_geom,
    filter_vertical_edges,
    filter_horizontal_edges,
    calc_edge_median,
    calc_face_dimensions
)


def fill_panel(bm, face, panel_x, panel_y, panel_b, panel_t, panel_d, **kwargs):
    """
    平面材质填充
    :param bm: 
    :param face: 
    :param panel_x: (int)number of horizontal panels
    :param panel_y: (int)number of vertical panels
    :param panel_b: (float)border of panels from face edges
    :param panel_t: (float)thickness of panel inset
    :param panel_d: (float)depth of panel
    """
    # 主平面(可添加子平面)
    bmesh.ops.inset_individual(bm, faces=[face], thickness=panel_b)

    # 计算被分割的边
    n = face.normal
    v_edges = filter_vertical_edges(face.edges, n)
    h_edges = list(set(face.edges) - set(v_edges))

    vts = []
    # 对边进行分割
    if panel_x:
        res_one = bmesh.ops.subdivide_edges(bm, edges=v_edges, cuts=panel_x)
        vts = filter_geom(res_one['geom_inner'], BMVert)

    if panel_y:
        res_two = bmesh.ops.subdivide_edges(
            bm,
            edges=h_edges+filter_geom(res_one['geom_inner'], BMEdge) if panel_x else h_edges,
            cuts=panel_y
        )
        vts = filter_geom(res_two['geom_inner'], BMVert)

    # 新增平面
    if vts:
        faces = list(filter(lambda f: len(f.verts) == 4,
                            {f for v in vts for f in v.link_faces if f.normal == n})
                     )
        bmesh.ops.inset_individual(bm, faces=faces, thickness=panel_t / 2)
        bmesh.ops.translate(
            bm,
            verts=list({v for f in faces for v in f.verts}),
            vec=n*panel_d
        )
        # recalc_face_normals()-->计算面的“外部”法线
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))


def fill_glass_panes(bm, face, panel_x, panel_y, panel_t, panel_d, **kwargs):
    """添加玻璃平面"""

    v_edges = filter_vertical_edges(face.edges, face.normal)
    h_edges = filter_horizontal_edges(face.edges, face.normal)

    edges = []
    # 对边进行分割
    if panel_x:
        res_one = bmesh.ops.subdivide_edges(bm, edges=v_edges, cuts=panel_x).get('geom_inner')
        edges.extend(filter_geom(res_one, BMEdge))

    if panel_y:
        res_two = bmesh.ops.subdivide_edges(
            bm,
            edges=h_edges + filter_geom(res_one, BMEdge) if panel_x else h_edges,
            cuts=panel_y
        ).get('geom_inner')
        edges.extend(filter_geom(res_two, BMEdge))

    if edges:
        panel_faces = list({f for ed in edges for f in ed.link_faces})
        bmesh.ops.inset_individual(bm, faces=panel_faces, thickness=panel_t)

        for f in panel_faces:
            bmesh.ops.translate(bm, verts=f.verts, vec=-f.normal*panel_d)


def fill_bar(bm, face, bar_x, bar_y, bar_t, bar_d, **kwargs):
    """栏杆类型填充"""
    # 计算面的中心，长和宽
    width, height = calc_face_dimensions(face)
    fc = face.calc_center_median()

    # 新建内部框架
    # --水平方向
    offset = height / (bar_x + 1)
    for i in range(bar_x):
        # 复制
        ret = bmesh.ops.duplicate(bm, geom=[face])
        verts = filter_geom(ret['geom'], BMVert)

        # 缩放 变换
        fs = bar_t / height
        bmesh.ops.scale(bm, verts=verts, vec=(1, 1, fs), space=Matrix.Translation(-fc))
        bmesh.ops.translate(
            bm,
            verts=verts,
            vec=Vector((face.normal*bar_d/2))+Vector((0, 0, -height/2+(i+1)*offset))
        )

        # 挤压
        ext = bmesh.ops.extrude_edge_only(bm, edges=filter_horizontal_edges(
            filter_geom(ret['geom'], BMEdge), face.normal))
        bmesh.ops.translate(bm, verts=filter_geom(ext['geom'], BMVert), vec=-face.normal*bar_d/2)

    # --垂直方向
    eps = 0.015
    offset = width / (bar_y + 1)
    for i in range(bar_y):
        # 复制
        ret = bmesh.ops.duplicate(bm, geom=[face])
        verts = filter_geom(ret['geom'], BMVert)
        # Scale and Translate
        fs = bar_t / width
        bmesh.ops.scale(bm, verts=verts, vec=(fs, fs, 1), space=Matrix.Translation(-fc))
        perp = face.normal.cross(Vector((0, 0, 1)))  # 垂直线
        bmesh.ops.translate(
            bm,
            verts=verts,
            vec=Vector((face.normal*((bar_d/2)-eps)))+perp*(-width/2+((i+1)*offset))
        )
        ext = bmesh.ops.extrude_edge_only(
            bm,
            edges=filter_vertical_edges(
                filter_geom(ret['geom'], BMEdge), face.normal)
        )
        bmesh.ops.translate(
            bm,
            verts=filter_geom(ext['geom'], BMVert),
            vec=-face.normal * ((bar_d / 2) - eps)
        )


def fill_louver(bm, face, louver_m, louver_count, louver_d, louver_b, **kwargs):
    """
    百叶窗
    :param bm: 
    :param face: 
    :param louver_m: (float)margin
    :param louver_count: (int)number
    :param louver_d: (float)depth
    :param louver_b: (float)border
    """
    normal = face.normal
    # inset margin
    if louver_m:
        bmesh.ops.inset_individual(bm, faces=[face], thickness=louver_m)
    # 切割垂直方向边
    count = (2 * louver_count) - 1
    count = count if count % 2 == 0 else count + 1

    res = bmesh.ops.subdivide_edges(
        bm,
        edges=filter_vertical_edges(face.edges, face.normal),
        cuts=count
    )

    # 需要添加百叶窗的面
    faces = list({f for e in filter_geom(res['geom_inner'], BMEdge) for f in e.link_faces})
    faces.sort(key=lambda f: f.calc_center_median().z)
    louver_faces = faces[1::2]

    # 边距缩放
    for face in louver_faces:
        bmesh.ops.scale(
            bm,
            vec=(1, 1, 1+louver_b),
            verts=face.verts,
            space=Matrix.Translation(-face.calc_center_median())
        )
    # 挤压百叶窗面
    res = bmesh.ops.extrude_discrete_faces(bm, faces=louver_faces)
    bmesh.ops.translate(
        bm,
        vec=normal * louver_d,
        verts=list({v for face in res['face'] for v in face.verts})
    )
    # 百叶窗倾斜
    for face in res['faces']:
        top_edge = max(
            filter_horizontal_edges(face.edges, face.normal),
            key=lambda e: calc_edge_median(e).z
        )
        bmesh.ops.translate(bm, vec=-face.normal*louver_d, verts=top_edge.verts)

    # clearup
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)
