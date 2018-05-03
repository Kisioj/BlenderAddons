import bpy
import re

bl_info = {
    "name": "Fix & sort materials",
    "description": "Removing .001, .002 etc. suffix from materials and sorting them by name",
    "author": "Krzysztof Jura <kisioj@gmail.com>",
    "version": (1, 2),
    "category": "Material",
}

SUFFIX = r'\.\d{3}$'


def bubble_sort(obj, key=lambda material: material.name.lower(), desc=False):
    def should_move_material_down(material_index):
        key1 = key(obj.material_slots[material_index].material)
        key2 = key(obj.material_slots[material_index + 1].material)
        if desc:
            return key1 < key2
        return key1 > key2

    def move_material_down(material_index):
        obj.active_material_index = material_index
        bpy.ops.object.material_slot_move(direction='DOWN')

    materials_count = len(obj.material_slots)
    sorted_count = 0
    while materials_count > sorted_count:
        for index in range(materials_count - 1):
            if should_move_material_down(index):
                move_material_down(index)
        sorted_count += 1


def sort_materials():
    def materials_key(material):
        if material.name.startswith('P:'):
            return chr(255) + material.name.lower()
        return material.name.lower()

    for obj in bpy.data.objects:
        bubble_sort(obj, key=materials_key)


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


class FixMaterialNamesOperator(bpy.types.Operator):
    bl_idname = "objects.fix_material_names"
    bl_label = "Fix Material Names Operator"

    def execute(self, context):
        fix_material_names()
        return {'FINISHED'}


class SortMaterialsOperator(bpy.types.Operator):
    bl_idname = "objects.sort_materials"
    bl_label = "Sort Materials Operator"

    def execute(self, context):
        sort_materials()
        return {'FINISHED'}


class UpdateMaterialNamesPanel(bpy.types.Panel):
    bl_label = "Materials Addon"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Tools"

    def draw(self, context):
        self.layout.operator("objects.fix_material_names", text="Fix material names")
        self.layout.operator("objects.sort_materials", text="Sort materials")


def register():
    bpy.utils.register_class(FixMaterialNamesOperator)
    bpy.utils.register_class(SortMaterialsOperator)
    bpy.utils.register_class(UpdateMaterialNamesPanel)


def unregister():
    bpy.utils.unregister_class(FixMaterialNamesOperator)
    bpy.utils.unregister_class(SortMaterialsOperator)
    bpy.utils.unregister_class(UpdateMaterialNamesPanel)


if __name__ == '__main__':
    register()
