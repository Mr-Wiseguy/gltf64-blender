import bpy
import pathlib
import os
from bpy.utils import register_class, unregister_class
from .utility import prop_split, PluginError

class glTF64_Export(bpy.types.Operator):
    bl_idname = 'object.gltf64_export'
    bl_label = "Export selected as glTF64"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    def execute(self, context):
        selected = bpy.context.selected_objects
        export_dir = os.path.realpath(bpy.path.abspath(context.scene.gltf64ExportPath))
        if context.scene.gltf64TextureExportPath != None and context.scene.gltf64TextureExportPath != "":
            texture_export_dir = os.path.realpath(bpy.path.abspath(context.scene.gltf64TextureExportPath))
        else:
            texture_export_dir = export_dir
        if len(selected) == 0:
            self.report({'ERROR'}, "No objects selected")
            return {'FINISHED'}
        if export_dir == "":
            self.report({'ERROR'}, "Invalid export folder")
            return {'FINISHED'}
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        # Export each object one-by-one
        for obj in selected:
            obj.select_set(True)
            child_meshes = []
            if obj.type == "ARMATURE":
                for child in obj.children:
                    if child.type == "MESH":
                        child_meshes.append(child)
                        child.select_set(True)
            pathstr = str(pathlib.Path(export_dir).joinpath(pathlib.Path(obj.name + ".gltf")))
            bpy.ops.export_scene.gltf(filepath = pathstr, export_texture_dir=texture_export_dir,
                export_format="GLTF_SEPARATE", use_selection=True, export_apply=True)
            obj.select_set(False)
            for child in child_meshes:
                child.select_set(False)
        # Reselect selected objects
        for obj in selected:
            obj.select_set(True)

        self.report({'INFO'}, "Exporting complete")
        return {'FINISHED'}

class glTF64_OperationsPanel(bpy.types.Panel):
    bl_idname = "GLTF64_PT_operations"
    bl_label = "glTF64 Operations"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "glTF64"

    @classmethod
    def poll(cls, context):
        return True

    # called every frame
    def draw(self, context):
        self.layout.operator(glTF64_Export.bl_idname)

classes = (
    # Operators
    glTF64_Export,
    # UI
    glTF64_OperationsPanel,
)

def gltf64_ops_register():
    for cls in classes:
        register_class(cls)

def gltf64_ops_unregister():
    for cls in classes:
        unregister_class(cls)
