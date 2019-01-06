import bpy
from mathutils import Vector


def clamp(val, _min, _max):
    """
    重置值(_min至_max)
    :param val: 
    :param _min: 
    :param _max: 
    :return: 
    """
    return max(min(val, _max), _min)


def condition(con, val1, val2):
    return val1 if con else val2


def ifeven(num, val1, val2):
    return condition(num % 2 == 0, val1, val2)


def args_from_props(props, names):
    return tuple(getattr(props, name) for name in names)


def kwargs_from_props(props):
    valid_types = (
        int, float, str, tuple, bool, Vector,
        bpy.types.Material,
        bpy.types.Object
    )

    result = {}
    for p in dir(props):
        if p.startswith('__') or p in ['rna_type', 'bl_rna']:
            continue
        prop = getattr(props, p)

        if isinstance(prop, valid_types):
            result[p] = prop
        elif isinstance(prop, bpy.types.PropertyGroup) and not isinstance(prop,type(props)):
            result.update(kwargs_from_props(prop))
    return result


def assert_test(func):
    """
    捕获func中的异常
    :param func: 
    :return: 
    """
    def wrapper():
        try:
            func()
            print(func.__name__.upper() + " PASSED ..")
        except Exception as e:
            print(func.__name__.upper + " FAILED ..", e)

    return wrapper()


def clean_scene():
    """清除面板"""
    scene = bpy.context.scene
    if scene.ojects:
        active = scene.objects.active   # 当前选择元素
        if active and active.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='SELECT')  # 更改场景中所有可见对象的选择--选择所有元素
        bpy.ops.object.delete(use_global=False)
    return scene
