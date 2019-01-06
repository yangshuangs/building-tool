from .fill import register_fill, unregister_fill
from .window import register_window, unregister_window
from .balcony import register_balcony, unregister_balcony
from .door import register_door, unregister_door
from .rails import register_rail, unregister_rail
from .roof import register_roof, unregister_roof
from .stairs import register_stairs, unregister_stairs
from .floor import register_floor, unregister_floor
from .floorplan import register_floorplan, unregister_floorplan
from .generic import register_generic, unregister_generic


register_funcs = [
    register_generic,
    register_fill,
    register_window,
    register_stairs,
    register_roof,
    register_rail,
    register_door,
    register_balcony,
    register_floor,
    register_floorplan,

]

unregister_funcs = [
    unregister_generic,
    unregister_fill,
    unregister_window,
    unregister_stairs,
    unregister_roof,
    unregister_rail,
    unregister_door,
    unregister_balcony,
    unregister_floor,
    unregister_floorplan,
]


def register_core():
    for func in register_funcs:
        func()


def unregister_core():
    for func in unregister_funcs:
        func()
