# glTF64

This requires Blender 2.82+.

Forked from [Fast64](https://github.com/Fast-64/fast64/).

This is a Blender plugin that can export glTF files with custom extensions that encode N64 rendering data. It supports custom color combiners / geometry modes / etc. It is to be used in conjunction with a converter that can accept the custom extensions and output data for the given N64 game that the model will be used in.

Make sure to save often, as this plugin is prone to crashing when creating materials / undoing material creation. This is a Blender issue.

<https://developer.blender.org/T70574>


### Credits
Thanks to kurethedead and the maintainers of Fast64, from which this addon was forked.

### Installation
Download the repository as a zip file. In Blender, go to Edit -> Preferences -> Add-Ons and click the "Install" button to install the plugin from the zip file. Find the glTF64 addon in the addon list and enable it. If it does not show up, go to Edit -> Preferences -> Save&Load and make sure 'Auto Run Python Scripts' is enabled.

### Tool Locations
The tools can be found in the properties sidebar under the 'glTF64' tab (toggled by pressing N).
The F3D material inspector can be found in the properties editor under the material tab.

### Vertex Colors
To use vertex colors, select a vertex colored texture preset and add two vertex color layers to your mesh named 'Col' and 'Alpha'. The alpha layer will use the greyscale value of the vertex color to determine alpha.
