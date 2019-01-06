import bpy
import bmesh
from .util_mesh import select


def make_object(name, data=None):
    """新建元素"""
    return bpy.data.objects.new(name, data)


def bm_from_obj(obj):
    """由物体数据创建多边形网格"""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    return bm


def bm_to_obj(bm, obj):
    """将多边形网格赋予物体"""
    # to_mesh()-->将此BMesh数据写入现有的Mesh数据块
    bm.to_mesh(obj.data)
    bm.free()


def link_obj(obj):
    """将物体链接到场景"""
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.objects.active = obj
    select(bpy.data.objects, False)
    obj.select = True
    obj.location = bpy.context.scene.cursor_location


def obj_clear_data(obj):
    """从物体上删除网格几何数据"""
    bm = bm_from_obj(obj)
    bmesh.ops.delete(bm, geom=list(bm.verts), context=1)
    bm_to_obj(bm, obj)
