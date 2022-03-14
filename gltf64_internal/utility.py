import bpy, traceback

class PluginError(Exception):
	pass

def getRGBA16Tuple(color):
	return ((int(round(color[0] * 0x1F)) & 0x1F) << 11) | \
		((int(round(color[1] * 0x1F)) & 0x1F) << 6) | \
		((int(round(color[2] * 0x1F)) & 0x1F) << 1) | \
		(1 if color[3] > 0.5 else 0)

def raisePluginError(operator, exception):
	if bpy.context.scene.fullTraceback:
		operator.report({'ERROR'}, traceback.format_exc())
	else:
		operator.report({'ERROR'}, str(exception))

def prop_split(layout, data, field, name):
	split = layout.split(factor = 0.5)
	split.label(text = name)
	split.prop(data, field, text = '')

