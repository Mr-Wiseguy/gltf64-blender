# This is not in the f3d package since copying materials requires copying collision settings from all games as well.

import bpy, math
from bpy.utils import register_class, unregister_class
from .f3d.f3d_material import *
from .utility import *
from bl_operators.presets import AddPresetBase

def convertAllBSDFtoF3D(objs, renameUV):
	# Dict of non-f3d materials : converted f3d materials
	# handles cases where materials are used in multiple objects
	materialDict = {}
	for obj in objs:
		if renameUV:
			for uv_layer in obj.data.uv_layers:
				uv_layer.name = "UVMap"
		for index in range(len(obj.material_slots)):
			material = obj.material_slots[index].material
			if material is not None and not material.is_f3d:
				if material in materialDict:
					print("Existing material")
					obj.material_slots[index].material = materialDict[material]
				else:
					print("New material")
					convertBSDFtoF3D(obj, index, material, materialDict)

def convertBSDFtoF3D(obj, index, material, materialDict):
	if not material.use_nodes:
		newMaterial = createF3DMat(obj, preset = 'Shaded Solid', index = index)
		f3dMat = newMaterial.f3d_mat
		f3dMat.default_light_color = material.diffuse_color
		updateMatWithName(newMaterial, material, materialDict)

	elif "Principled BSDF" in material.node_tree.nodes:
		tex0Node = material.node_tree.nodes['Principled BSDF'].inputs['Base Color']
		tex1Node = material.node_tree.nodes['Principled BSDF'].inputs['Subsurface Color']
		if len(tex0Node.links) == 0:
			newMaterial = createF3DMat(obj, preset = getDefaultMaterialPreset("opaque_shaded_env_color"), index = index)
			f3dMat = newMaterial.f3d_mat
			f3dMat.default_light_color = tex0Node.default_value
			updateMatWithName(newMaterial, material, materialDict)
		else:
			if isinstance(tex0Node.links[0].from_node, bpy.types.ShaderNodeTexImage):
				if 'convert_preset' in material:
					presetName = material['convert_preset']
					if presetName not in [enumValue[0] for enumValue in enumMaterialPresets]:
						raise PluginError('During BSDF to F3D conversion, for material \'' + material.name + '\',' + \
							' enum \'' + presetName + '\' was not found in material preset enum list.')
				else:
					presetName = getDefaultMaterialPreset('opaque_shaded_tex')
				newMaterial = createF3DMat(obj, preset = presetName, index = index)
				f3dMat = newMaterial.f3d_mat
				f3dMat.tex0.tex = tex0Node.links[0].from_node.image
				if len(tex1Node.links) > 0 and \
					isinstance(tex1Node.links[0].from_node, bpy.types.ShaderNodeTexImage):
					f3dMat.tex1.tex = tex1Node.links[0].from_node.image
				updateMatWithName(newMaterial, material, materialDict)		
			else:
				print("Principled BSDF material does not have an Image Node attached to its Base Color.")
	else:
		print("Material is not a Principled BSDF or non-node material.")

def updateMatWithName(f3dMat, oldMat, materialDict):
	f3dMat.name = oldMat.name + "_f3d"
	update_preset_manual(f3dMat, bpy.context)
	materialDict[oldMat] = f3dMat

def updateMatWithNewVersionName(f3dMat, oldMat, materialDict, version):
	name = oldMat.name
	if oldMat.name[-3:-1] == '_v':
		name = oldMat.name[:-3]
	f3dMat.name = name + "_v" + str(version)
	update_preset_manual(f3dMat, bpy.context)
	materialDict[oldMat] = f3dMat

class BSDFConvert(bpy.types.Operator):
	# set bl_ properties
	bl_idname = 'object.convert_bsdf'
	bl_label = "Principled BSDF to F3D Converter"
	bl_options = {'REGISTER', 'UNDO', 'PRESET'}

	# Called on demand (i.e. button press, menu item)
	# Can also be called from operator search menu (Spacebar)
	def execute(self, context):
		try:
			if context.mode != 'OBJECT':
				raise PluginError("Operator can only be used in object mode.")
			
			if context.scene.bsdf_conv_all:
				convertAllBSDFtoF3D([obj for obj in bpy.data.objects if isinstance(obj.data, bpy.types.Mesh)],
					context.scene.rename_uv_maps)
			else:
				if len(context.selected_objects) == 0:
					raise PluginError("Mesh not selected.")
				elif type(context.selected_objects[0].data) is not\
					bpy.types.Mesh:
					raise PluginError("Mesh not selected.")
				
				obj = context.selected_objects[0]
				convertAllBSDFtoF3D([obj], context.scene.rename_uv_maps)
				
		except Exception as e:
			raisePluginError(self, e)
			return {"CANCELLED"}

		self.report({'INFO'}, 'Created F3D material.')
		return {'FINISHED'} # must return a set

class F3DMaterialConverterPanel(bpy.types.Panel):
	bl_label = "F3D Material Converter"
	bl_idname = "MATERIAL_PT_F3D_Material_Converter"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'glTF64'

	@classmethod
	def poll(cls, context):
		return True
		#return hasattr(context, 'object') and context.object is not None and \
		#	isinstance(context.object.data, bpy.types.Mesh)

	def draw(self, context):
		#mesh = context.object.data
		self.layout.operator(BSDFConvert.bl_idname)
		self.layout.prop(context.scene, 'bsdf_conv_all')
		self.layout.prop(context.scene, 'rename_uv_maps')
		self.layout.prop(context.scene, 'update_conv_all')
		self.layout.operator(ReloadDefaultF3DPresets.bl_idname)


bsdf_conv_classes = (
	BSDFConvert,
)

bsdf_conv_panel_classes = (
	F3DMaterialConverterPanel,
)

def bsdf_conv_panel_regsiter():
	for cls in bsdf_conv_panel_classes:
		register_class(cls)

def bsdf_conv_panel_unregsiter():
	for cls in bsdf_conv_panel_classes:
		unregister_class(cls)

def bsdf_conv_register():
	for cls in bsdf_conv_classes:
		register_class(cls)

	# Moved to Level Root
	bpy.types.Scene.bsdf_conv_all = bpy.props.BoolProperty(
		name = 'Convert all objects', default = True)
	bpy.types.Scene.update_conv_all = bpy.props.BoolProperty(
		name = 'Convert all objects', default = True)
	bpy.types.Scene.rename_uv_maps = bpy.props.BoolProperty(
		name = 'Rename UV maps', default = True)

def bsdf_conv_unregister():
	for cls in bsdf_conv_classes:
		unregister_class(cls)

	del bpy.types.Scene.bsdf_conv_all
	del bpy.types.Scene.update_conv_all
	del bpy.types.Scene.rename_uv_maps