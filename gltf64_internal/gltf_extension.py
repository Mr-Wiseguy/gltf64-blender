import bpy
import math
from .f3d.f3d_material import all_combiner_uses
from pprint import pprint

material_extension_name = "N64_materials_gltf64"
texture_extension_name = "N64_texture_inputs"
image_extension_name = "N64_image_format"

def make_render_mode(zmode: str, cvg_dst: str, flags: list, blender: list):
	return {
		"zmode" : zmode,
		"cvgDst": cvg_dst,
		"flags": flags,
		"blender": blender
	}

predefinedRenderModes = {
	'G_RM_OPA_SURF'        : make_render_mode("OPA",   "CLAMP", [                                                                                  "FORCE_BL"], ["IN",  "IN",    "MEM", "MEM"]),
	
	'G_RM_ZB_OPA_SURF'     : make_render_mode("OPA",   "FULL",  [         "Z_CMP", "Z_UPD",                                       "ALPHA_CVG_SEL"            ], ["IN",  "IN",    "MEM", "MEM"]),
	'G_RM_ZB_OPA_DECAL'    : make_render_mode("DEC",   "FULL",  [         "Z_CMP",                                                "ALPHA_CVG_SEL"            ], ["IN",  "IN",    "MEM", "MEM"]),
	'G_RM_ZB_XLU_SURF'     : make_render_mode("XLU",   "FULL",  [         "Z_CMP",          "IM_RD",                                               "FORCE_BL"], ["IN",  "IN",    "MEM", "1MA"]),
	'G_RM_ZB_XLU_DECAL'    : make_render_mode("DEC",   "FULL",  [         "Z_CMP",          "IM_RD",                                               "FORCE_BL"], ["IN",  "IN",    "MEM", "1MA"]),
	
	'G_RM_AA_ZB_OPA_SURF'  : make_render_mode("OPA",   "CLAMP", ["AA_EN", "Z_CMP", "Z_UPD", "IM_RD",                              "ALPHA_CVG_SEL"            ], ["IN",  "IN",    "MEM", "MEM"]),
	'G_RM_AA_ZB_OPA_DECAL' : make_render_mode("DEC",   "WRAP",  ["AA_EN", "Z_CMP",          "IM_RD",                              "ALPHA_CVG_SEL"            ], ["IN",  "IN",    "MEM", "MEM"]),
	'G_RM_AA_ZB_OPA_INTER' : make_render_mode("INTER", "CLAMP", ["AA_EN", "Z_CMP", "Z_UPD", "IM_RD",                              "ALPHA_CVG_SEL"            ], ["IN",  "IN",    "MEM", "MEM"]),
	'G_RM_AA_ZB_TEX_EDGE'  : make_render_mode("OPA",   "CLAMP", ["AA_EN", "Z_CMP", "Z_UPD", "IM_RD",               "CVG_X_ALPHA", "ALPHA_CVG_SEL"            ], ["IN",  "IN",    "MEM", "MEM"]),
	'G_RM_AA_ZB_XLU_SURF'  : make_render_mode("XLU",   "WRAP",  ["AA_EN", "Z_CMP",          "IM_RD", "CLR_ON_CVG",                                 "FORCE_BL"], ["IN",  "IN",    "MEM", "1MA"]),
	'G_RM_AA_ZB_XLU_DECAL' : make_render_mode("DEC",   "WRAP",  ["AA_EN", "Z_CMP",          "IM_RD", "CLR_ON_CVG",                                 "FORCE_BL"], ["IN",  "IN",    "MEM", "1MA"]),
	'G_RM_AA_ZB_XLU_INTER' : make_render_mode("INTER", "WRAP",  ["AA_EN", "Z_CMP",          "IM_RD", "CLR_ON_CVG",                                 "FORCE_BL"], ["IN",  "IN",    "MEM", "1MA"]),

	'G_RM_ZB_CLD_SURF'     : make_render_mode("XLU",   "SAVE",  [         "Z_CMP",          "IM_RD",                                               "FORCE_BL"], ["IN",  "IN",    "MEM", "1MA"]),

	'G_RM_FOG_SHADE_A'     : make_render_mode("",      "",      [                                                                                            ], ["FOG", "SHADE", "IN",  "1MA"]),
	'G_RM_FOG_PRIM_A'      : make_render_mode("",      "",      [                                                                                            ], ["FOG", "FOG",   "IN",  "1MA"]),
	'G_RM_PASS'            : make_render_mode("",      "",      [                                                                                            ], ["IN",  "0",     "IN",  "1"  ]),
	'G_RM_ADD'             : make_render_mode("",      "SAVE",  [                           "IM_RD",                                               "FORCE_BL"], ["IN",  "FOG",   "MEM", "1"  ]),
	'G_RM_NOOP'            : make_render_mode("",      "",      [                                                                                            ], ["IN",  "IN",    "IN",  "1MA"]),
}

def error_popup_handler(error_msg):
	def handler(self, context):
		self.layout.label(text = error_msg)
	return handler

def removeprefix(input, prefix):
	if input.startswith(prefix):
		return input[len(prefix):]
	return input

def remove_blender_input_prefixes(input):
	tmp = removeprefix(input, "G_BL_CLR_")
	tmp = removeprefix(tmp, "G_BL_A_")
	tmp = removeprefix(tmp, "G_BL_")
	return tmp
	
from io_scene_gltf2.io.com import gltf2_io
from io_scene_gltf2.io.com.gltf2_io_constants import TextureFilter, TextureWrap
from io_scene_gltf2.blender.exp.gltf2_blender_image import ExportImage
from io_scene_gltf2.blender.exp.gltf2_blender_gather_image import __gather_name, __gather_uri, __gather_buffer_view, __make_image
from io_scene_gltf2.blender.exp.gltf2_blender_gather_sampler import __sampler_by_value
from io_scene_gltf2.blender.exp.gltf2_blender_gather_cache import cached
from io_scene_gltf2.io.com.gltf2_io_extensions import Extension

def blender_image_to_gltf2_image(bl_image, f3d_tex, export_settings):
	image_data = ExportImage.from_blender_image(bl_image)
	mime_type = "image/png"
	name = __gather_name(image_data, export_settings)
	buffer_view = __gather_buffer_view(image_data, mime_type, name, export_settings)

	uri = __gather_uri(image_data, mime_type, name, export_settings)
	
	image = __make_image(
		buffer_view,
		None,
		None,
		mime_type,
		name,
		uri,
		export_settings
	)

	if image.extensions is None:
		image.extensions = {}
	
	image.extensions[image_extension_name] = Extension(
		name=image_extension_name,
		extension = { 'format': f3d_tex.tex_format },
		required = False
	)
		
	return image

def sampler_from_f3d(f3d_mat, f3d_tex, export_settings):
	use_nearest = f3d_mat.rdp_settings.g_mdsft_text_filt == 'G_TF_POINT'
	mag_filter = TextureFilter.Nearest if use_nearest else TextureFilter.Linear
	min_filter = TextureFilter.NearestMipmapNearest if use_nearest else TextureFilter.LinearMipmapLinear
	clamp_s = f3d_tex.S.clamp
	clamp_t = f3d_tex.T.clamp
	mirror_s = f3d_tex.S.mirror
	mirror_t = f3d_tex.T.mirror
	wrap_s = TextureWrap.ClampToEdge if clamp_s else (TextureWrap.MirroredRepeat if mirror_s else TextureWrap.Repeat)
	wrap_t = TextureWrap.ClampToEdge if clamp_t else (TextureWrap.MirroredRepeat if mirror_t else TextureWrap.Repeat)
	# TODO mask and shift
	sampler = __sampler_by_value(
		mag_filter,
		min_filter,
		wrap_s,
		wrap_t,
		export_settings
	)

	# if sampler.extensions is None:
	# 	sampler.extensions = {}
	
	# sampler.extensions[sampler_extension_name] = Extension(
	# 	name=sampler_extension_name,
	# 	extension = {},
	# 	required = False
	# )

	return sampler

@cached
def texture_by_value(sampler, image, export_settings):
	return gltf2_io.Texture(
		extensions={},
		extras=None,
		name=None,
		sampler=sampler,
		source=image
	)

import traceback

def append_geometry_mode(mat_value, global_value, mask, mode, do_write):
	if mat_value:
		mode |= mask
	if mat_value != global_value:
		do_write = True
	return mode, do_write
def write_geometry_mode(extension_data, mat_settings, global_settings):
	do_write = False
	mode = 0x0

	mode, do_write = append_geometry_mode(mat_settings.g_zbuffer, global_settings.g_zbuffer, 0x00000001, mode, do_write)
	mode, do_write = append_geometry_mode(mat_settings.g_shade, global_settings.g_shade, 0x00000004, mode, do_write)
	mode, do_write = append_geometry_mode(mat_settings.g_shade_smooth, global_settings.g_shade_smooth, 0x00200000, mode, do_write)
	mode, do_write = append_geometry_mode(mat_settings.g_cull_front, global_settings.g_cull_front, 0x00000200, mode, do_write)
	mode, do_write = append_geometry_mode(mat_settings.g_cull_back, global_settings.g_cull_back, 0x00000400, mode, do_write)
	mode, do_write = append_geometry_mode(mat_settings.g_fog, global_settings.g_fog, 0x00010000, mode, do_write)
	mode, do_write = append_geometry_mode(mat_settings.g_lighting, global_settings.g_lighting, 0x00020000, mode, do_write)
	mode, do_write = append_geometry_mode(mat_settings.g_tex_gen, global_settings.g_tex_gen, 0x00040000, mode, do_write)
	mode, do_write = append_geometry_mode(mat_settings.g_tex_gen_linear, global_settings.g_tex_gen_linear, 0x00080000, mode, do_write)

	if do_write:
		extension_data['geometryMode'] = mode
def write_othermodeh(extension_data, mat_settings, global_settings):
	mode = []

	if mat_settings.g_mdsft_cycletype == 'G_CYC_2CYCLE':
		mode.append('two_cycle')

	if mat_settings.g_mdsft_text_filt == 'G_TF_POINT':
		mode.append('point_filter')

	if len(mode) > 0:
		extension_data['othermodeH'] = mode

def swap_textures_cycle_2(input):
	if input == 'TEXEL0':
		return 'TEXEL1'
	elif input == 'TEXEL1':
		return 'TEXEL0'
	elif input == 'TEXEL0_ALPHA':
		return 'TEXEL1_ALPHA'
	elif input == 'TEXEL1_ALPHA':
		return 'TEXEL0_ALPHA'
	return input

class glTF2ExportUserExtension:

	def __init__(self):
		# We need to wait until we create the gltf2UserExtension to import the gltf2 modules
		# Otherwise, it may fail because the gltf2 may not be loaded yet
		self.Extension = Extension
		self.blender_images = {}
		self.samplers = set()
		self.textures = set()
	
	def gather_image_hook(self, gltf2_image, blender_shader_sockets, export_settings):
		print("image hook")
		print(gltf2_image)
	
	# Converts an f3d material/texture into a gltf2_texture and stores any relevant created data in this object
	def f3d_texture_to_gltf2_texture(self, f3d_mat, f3d_texture, export_settings):
		cur_bl_image = f3d_texture.tex
		cur_image = blender_image_to_gltf2_image(cur_bl_image, f3d_texture, export_settings)
		cur_sampler = sampler_from_f3d(f3d_mat, f3d_texture, export_settings)
		cur_texture = texture_by_value(cur_sampler, cur_image, export_settings)
		self.blender_images[cur_bl_image.name] = cur_image
		self.samplers.add(cur_sampler)
		self.textures.add(cur_texture)

		return cur_texture

	def gather_material_pbr_metallic_roughness_hook(self, gltf2_material, blender_material, orm_texture, export_settings):
		if blender_material.is_f3d:
			if gltf2_material.extensions is None:
				gltf2_material.extensions = {}
			f3d_mat = blender_material.f3d_mat
			useDict = all_combiner_uses(f3d_mat)
		
			gltf2_material.metallic_factor = 0.0
			gltf2_material.roughness_factor = 0.5

			extension_data = {}

			# Check if the f3d material has textures and if so add them to the gltf2 material 
			if useDict['Texture 0'] and f3d_mat.tex0.tex_set and f3d_mat.tex0.tex is not None:
				print('tex0')
				cur_texture = self.f3d_texture_to_gltf2_texture(f3d_mat, f3d_mat.tex0, export_settings)

				gltf2_material.base_color_texture = gltf2_io.TextureInfo(
					extensions = {}, # Texture transform here
					extras = None,
					index = cur_texture,
					tex_coord = None
				)
				extension_data['tex0'] = {
					'index': cur_texture
				}
			if useDict['Texture 1'] and f3d_mat.tex1.tex_set and f3d_mat.tex1.tex is not None:
				print('tex1')
				cur_texture = self.f3d_texture_to_gltf2_texture(f3d_mat, f3d_mat.tex1, export_settings)
				extension_data['tex1'] = {
					'index': cur_texture
				}

			gltf2_material.extensions[texture_extension_name] = self.Extension(
				name=texture_extension_name,
				extension = extension_data,
				required = False
			)
			
	def gather_texture_info_hook(self, gltf2_texture_info, blender_shader_sockets, export_settings):
		print('texture info hook')
	
	def gather_gltf_hook(self, gltf2_plan, export_settings):
		# gltf2_plan.images.extend(list(self.blender_images.values()))
		# gltf2_plan.samplers.extend(list(self.samplers))
		# gltf2_plan.textures.extend(list(self.textures))
		pass

	def gather_material_hook(self, gltf2_material, blender_material, export_settings):
		try:
			if blender_material.is_f3d:
				if gltf2_material.extensions is None:
					gltf2_material.extensions = {}
				f3d_mat = blender_material.f3d_mat
				useDict = all_combiner_uses(f3d_mat)
				extension_data = {}

				# Color/Alpha combiners
				if f3d_mat.set_combiner:
					if f3d_mat.rdp_settings.g_mdsft_cycletype == 'G_CYC_1CYCLE':
						extension_data["combiner"] = [
							f3d_mat.combiner1.A,
							f3d_mat.combiner1.B,
							f3d_mat.combiner1.C,
							f3d_mat.combiner1.D,
							f3d_mat.combiner1.A_alpha,
							f3d_mat.combiner1.B_alpha,
							f3d_mat.combiner1.C_alpha,
							f3d_mat.combiner1.D_alpha,
							f3d_mat.combiner1.A,
							f3d_mat.combiner1.B,
							f3d_mat.combiner1.C,
							f3d_mat.combiner1.D,
							f3d_mat.combiner1.A_alpha,
							f3d_mat.combiner1.B_alpha,
							f3d_mat.combiner1.C_alpha,
							f3d_mat.combiner1.D_alpha
						]
					elif f3d_mat.rdp_settings.g_mdsft_cycletype == 'G_CYC_2CYCLE':
						extension_data["combiner"] = [
							swap_textures_cycle_2(f3d_mat.combiner1.A),
							swap_textures_cycle_2(f3d_mat.combiner1.B),
							swap_textures_cycle_2(f3d_mat.combiner1.C),
							swap_textures_cycle_2(f3d_mat.combiner1.D),
							swap_textures_cycle_2(f3d_mat.combiner1.A_alpha),
							swap_textures_cycle_2(f3d_mat.combiner1.B_alpha),
							swap_textures_cycle_2(f3d_mat.combiner1.C_alpha),
							swap_textures_cycle_2(f3d_mat.combiner1.D_alpha),
							swap_textures_cycle_2(f3d_mat.combiner2.A),
							swap_textures_cycle_2(f3d_mat.combiner2.B),
							swap_textures_cycle_2(f3d_mat.combiner2.C),
							swap_textures_cycle_2(f3d_mat.combiner2.D),
							swap_textures_cycle_2(f3d_mat.combiner2.A_alpha),
							swap_textures_cycle_2(f3d_mat.combiner2.B_alpha),
							swap_textures_cycle_2(f3d_mat.combiner2.C_alpha),
							swap_textures_cycle_2(f3d_mat.combiner2.D_alpha)
						]
				
				def to_srgb_component(c):
					if c < 0.0031308:
						srgb = 0.0 if c < 0.0 else c * 12.92
					else:
						srgb = 1.055 * math.pow(c, 1.0 / 2.4) - 0.055

					return srgb

				def to_srgb(linear):
					return [to_srgb_component(linear[0]), to_srgb_component(linear[1]), to_srgb_component(linear[2]), linear[3]]


				# Color registers
				if useDict['Environment'] and f3d_mat.set_env:
					extension_data["envColor"] = list(f3d_mat.env_color)
				if useDict['Primitive'] and f3d_mat.set_prim:
					extension_data["primColor"] = list(f3d_mat.prim_color)
				write_geometry_mode(extension_data, f3d_mat.rdp_settings, bpy.context.scene.world.rdp_defaults)
				write_othermodeh(extension_data, f3d_mat.rdp_settings, bpy.context.scene.world.rdp_defaults)
				
				extension_data["drawLayer"] = f3d_mat.draw_layer.gltf64

				# Render mode
				if f3d_mat.rdp_settings.set_rendermode:
					rendermode_data = {}
					# Advanced rendermode
					if f3d_mat.rdp_settings.rendermode_advanced_enabled:
						zmode = removeprefix(f3d_mat.rdp_settings.zmode, 'ZMODE_')
						cvg_dst = removeprefix(f3d_mat.rdp_settings.cvg_dst, 'CVG_DST_')
						flags = []
						if f3d_mat.rdp_settings.aa_en:
							flags.append('AA_EN')
						if f3d_mat.rdp_settings.z_cmp:
							flags.append('Z_CMP')
						if f3d_mat.rdp_settings.z_upd:
							flags.append('Z_UPD')
						if f3d_mat.rdp_settings.im_rd:
							flags.append('IM_RD')
						if f3d_mat.rdp_settings.clr_on_cvg:
							flags.append('CLR_ON_CVG')
						if f3d_mat.rdp_settings.cvg_x_alpha:
							flags.append('CVG_X_ALPHA')
						if f3d_mat.rdp_settings.alpha_cvg_sel:
							flags.append('ALPHA_CVG_SEL')
						if f3d_mat.rdp_settings.force_bl:
							flags.append('FORCE_BL')

						blender = [
							remove_blender_input_prefixes(f3d_mat.rdp_settings.blend_p1),
							remove_blender_input_prefixes(f3d_mat.rdp_settings.blend_a1),
							remove_blender_input_prefixes(f3d_mat.rdp_settings.blend_m1),
							remove_blender_input_prefixes(f3d_mat.rdp_settings.blend_b1),
							remove_blender_input_prefixes(f3d_mat.rdp_settings.blend_p2),
							remove_blender_input_prefixes(f3d_mat.rdp_settings.blend_a2),
							remove_blender_input_prefixes(f3d_mat.rdp_settings.blend_m2),
							remove_blender_input_prefixes(f3d_mat.rdp_settings.blend_b2),
						]
					# Preset rendermode
					else:
						rm_str_cycle1 = f3d_mat.rdp_settings.rendermode_preset_cycle_1
						rm_cycle1 = predefinedRenderModes[rm_str_cycle1]

						if f3d_mat.rdp_settings.g_mdsft_cycletype == 'G_CYC_2CYCLE':
							rm_str_cycle2 = f3d_mat.rdp_settings.rendermode_preset_cycle_2
							if rm_str_cycle2[-1] == '2':
								rm_str_cycle2 = rm_str_cycle2[:-1]
							rm_cycle2 = predefinedRenderModes[rm_str_cycle2]
						else:
							rm_cycle2 = rm_cycle1

						cvg_dst1 = rm_cycle1['cvgDst']
						cvg_dst2 = rm_cycle2['cvgDst']

						if cvg_dst1 == '':
							cvg_dst1 = cvg_dst2
						if cvg_dst2 == '':
							cvg_dst2 = cvg_dst1

						if cvg_dst1 != cvg_dst2:
							err_str = 'Cycle 1 and 2 render modes cannot have different cvg_dst values! In material: ' + blender_material.name
							bpy.context.window_manager.popup_menu(error_popup_handler(err_str), title="Error", icon='ERROR')
							raise Exception(err_str)
						cvg_dst = cvg_dst1 if not cvg_dst1 == '' else 'CLAMP'

						zmode1 = rm_cycle1['zmode']
						zmode2 = rm_cycle2['zmode']

						if zmode1 == '':
							zmode1 = zmode2
						if zmode2 == '':
							zmode2 = zmode1

						if zmode1 != zmode2:
							err_str = 'Cycle 1 and 2 render modes cannot have different Z modes! In material: ' + blender_material.name
							bpy.context.window_manager.popup_menu(error_popup_handler(err_str), title="Error", icon='ERROR')
							raise Exception(err_str)
						zmode = zmode1 if not zmode1 == '' else 'OPA'

						flags = list(set(rm_cycle1['flags']) | set(rm_cycle2['flags']))
						blender = rm_cycle1['blender'] + rm_cycle2['blender']

					rendermode_data['zmode'] = zmode
					rendermode_data['cvgDst'] = cvg_dst
					rendermode_data['flags'] = flags
					rendermode_data['blender'] = blender

					extension_data['renderMode'] = rendermode_data

				gltf2_material.extensions[material_extension_name] = self.Extension(
					name=material_extension_name,
					extension = extension_data,
					required = False
				)
		except:
			traceback.print_exc()
			raise
