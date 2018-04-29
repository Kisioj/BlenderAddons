import bpy
import re

bl_info = {
    "name": "Fix materials",
    "description": "Removing .001, .002 etc. suffix from materials",
    "author": "Krzysztof Jura <kisioj@gmail.com>",
    "version": (1, 1),
    "category": "Material",
}

SUFFIX = r'\.\d{3}$'


def fix_material_names():
    MATERIAL_NAME_2_GLOBAL_MATERIAL = {
        material.name: material
        for material in bpy.data.materials
    }

    for obj in bpy.data.objects:
        MATERIAL_NAME_2_LOCAL_INDEX = {
            material_slot.material.name: index
            for index, material_slot in enumerate(obj.material_slots)
        }

        material_slots_to_remove = []

        bpy.ops.object.mode_set(mode='EDIT')
        for index, material_slot in enumerate(obj.material_slots):
            material = material_slot.material
            if not re.search(SUFFIX, material.name):
                continue

            name_without_suffix = ''.join(re.split(SUFFIX, material.name))

            global_material = MATERIAL_NAME_2_GLOBAL_MATERIAL.get(name_without_suffix)
            if global_material is None:
                material.name = name_without_suffix
                continue

            local_index = MATERIAL_NAME_2_LOCAL_INDEX.get(name_without_suffix)
            if local_index is None:
                obj.material_slots[index] = global_material
                continue

            bpy.ops.mesh.select_all(action='DESELECT')
            obj.active_material_index = index
            bpy.ops.object.material_slot_select()
            obj.active_material_index = local_index
            bpy.ops.object.material_slot_assign()

            material_slots_to_remove.append(index)

        bpy.ops.object.mode_set(mode='OBJECT')
        for index in material_slots_to_remove:
            obj.active_material_index = index
            bpy.ops.object.material_slot_remove()


class SimpleOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"

    def execute(self, context):
        fix_material_names()
        return {'FINISHED'}


class UpdateMaterialNamesPanel(bpy.types.Panel):
    bl_label = "Materials Addon"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Tools"

    def draw(self, context):
        self.layout.operator("object.simple_operator", text="Fix material names")


def register():
    bpy.utils.register_class(SimpleOperator)
    bpy.utils.register_class(UpdateMaterialNamesPanel)


def unregister():
    bpy.utils.unregister_class(SimpleOperator)
    bpy.utils.unregister_class(UpdateMaterialNamesPanel)


if __name__ == '__main__':
    register()
