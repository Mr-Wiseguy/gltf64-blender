import sys
import tempfile
import copy
import shutil
import bpy
import traceback
import os
from pathlib import Path
from .gltf64_internal import *

import cProfile
import pstats

# info about add on
bl_info = {
	"name": "glTF64",
	"author": "Wiseguy",
	"location": "3DView",
	"description": "Plugin for exporting glTF files with extension data needed for N64 model conversion.",
	"category": "Import-Export",
	"blender": (2, 90, 0),
	}
	
class F3D_GlobalSettingsPanel(bpy.types.Panel):
	bl_idname = "F3D_PT_global_settings"
	bl_label = "F3D Global Settings"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'glTF64'

	@classmethod
	def poll(cls, context):
		return True

	# called every frame
	def draw(self, context):
		col = self.layout.column()
		col.prop(context.scene, 'saveTextures')
		col.prop(context.scene, 'f3d_simple', text = "Simple Material UI")
		col.prop(context.scene, 'generateF3DNodeGraph', text = "Generate F3D Node Graph For Materials")
		col.prop(context.scene, 'ignoreTextureRestrictions')
		if context.scene.ignoreTextureRestrictions:
			col.box().label(text = "Width/height must be < 1024. Must be RGBA32. Must be png format.")

class glTF64_GlobalSettingsPanel(bpy.types.Panel):
	bl_idname = "GLTF64_PT_global_settings"
	bl_label = "glTF64 Global Settings"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'glTF64'

	@classmethod
	def poll(cls, context):
		return True

	# called every frame
	def draw(self, context):
		col = self.layout.column()
		col.prop(context.scene, 'exportHiddenGeometry')
		col.prop(context.scene, 'fullTraceback')
		col.prop(context.scene, 'gltf64ExportPath')
		col.prop(context.scene, 'gltf64TextureExportPath')

classes = (
	F3D_GlobalSettingsPanel,
	glTF64_GlobalSettingsPanel
)

def gltf64_register():
	gltf64_bone_register()
	gltf64_ops_register()

def gltf64_unregister():
	gltf64_bone_unregister()
	gltf64_ops_unregister()

# called on add-on enabling
# register operators and panels here
# append menu layout drawing function to an existing window
def register():
	mat_register()
	bsdf_conv_register()
	gltf64_register()

	bsdf_conv_panel_regsiter()

	for cls in classes:
		register_class(cls)
	

	# ROM
	bpy.types.Scene.ignoreTextureRestrictions = bpy.props.BoolProperty(
		name = 'Ignore Texture Restrictions (Breaks CI Textures)')
	bpy.types.Scene.fullTraceback = \
		bpy.props.BoolProperty(name = 'Show Full Error Traceback', default = False)
	bpy.types.Scene.saveTextures = bpy.props.BoolProperty(
		name = 'Save Textures As PNGs (Breaks CI Textures)')
	bpy.types.Scene.generateF3DNodeGraph = bpy.props.BoolProperty(name = "Generate F3D Node Graph", default = True)
	bpy.types.Scene.exportHiddenGeometry = bpy.props.BoolProperty(name = "Export Hidden Geometry", default = True)
	bpy.types.Scene.gltf64ExportPath = bpy.props.StringProperty(
		name ='Export Directory', subtype = 'FILE_PATH')
	bpy.types.Scene.gltf64TextureExportPath = bpy.props.StringProperty(
		name ='Texture Export Directory', subtype = 'FILE_PATH')
	

# called on add-on disabling
def unregister():
	gltf64_unregister()
	mat_unregister()
	bsdf_conv_unregister()
	bsdf_conv_panel_unregsiter()

	del bpy.types.Scene.fullTraceback
	del bpy.types.Scene.ignoreTextureRestrictions
	del bpy.types.Scene.saveTextures
	del bpy.types.Scene.generateF3DNodeGraph
	del bpy.types.Scene.exportHiddenGeometry
	del bpy.types.Scene.gltf64ExportPath
	del bpy.types.Scene.gltf64TextureExportPath

	for cls in classes:
		unregister_class(cls)
