import bpy
import re

bl_info = {
    "name": "Fix materials",
    "description": "Removing .001, .002 etc. suffix from materials",
    "author": "Krzysztof Jura <kisioj@gmail.com>",
    "version": (1, 1),
    "category": "Material",
}


def fix_material_names():
    MATERIAL_NAME_2_GLOBAL_MATERIAL = {
        material.name: material
        for material in bpy.data.materials
    }

    for obj in bpy.data.objects:
        MATERIAL_NAME_2_LOCAL_INDEX = {
            material.name: index
            for index, material in enumerate(obj.material_slots)
        }

        for index, material_slot in enumerate(obj.material_slots):
            material = material_slot.material
            if not re.search(r'\.\d{3}$', material.name):
                continue

            new_name = ''.join(re.split(r'\.\d{3}$', material.name))

            global_material = MATERIAL_NAME_2_GLOBAL_MATERIAL.get(new_name)
            if not global_material:
                material.name = new_name
                continue

            local_index = MATERIAL_NAME_2_LOCAL_INDEX.get(new_name)
            if local_index is None:
                obj.material_slots[index] = global_material
                continue

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            obj.active_material_index = index
            bpy.ops.object.material_slot_select()
            obj.active_material_index = local_index
            bpy.ops.object.material_slot_assign()
            obj.active_material_index = index
            bpy.ops.object.mode_set(mode='OBJECT')
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
