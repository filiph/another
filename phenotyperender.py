# Renders the phenotype given

# Rendering script from: http://www.blender.org/forum/viewtopic.php?t=19102

import bpy, bgl, blf,sys 
from bpy import data, ops, props, types, context

sys.path.append("/Users/filiph/dev/blender")

from phenotype import *

# print("\nThis Python script will render your scene with all available cameras") 
# print("or with camera(s) matching command line argument 'cameras'") 
# print("") 
# print("Usage:") 
# print("Render all cameras:") 
# print("blender -b your_file.blend -P render_all_cameras.py\n") 
# print("Render only matching cameras:") 
# print("blender -b your_file.blend -P render_all_cameras.py  cameras=east\n") 

cameraNames='' 

# Loop all command line arguments and try to find "cameras=east" or similar 
for arg in sys.argv: 
    words=arg.split('=') 
    if ( words[0] == 'cameras'): 
     cameraNames = words[1] 

dna = ""
for arg in sys.argv:
    words = arg.split('=')
    if (words[0] == "dna"):
        dna = words[1]

ph = Phenotype(0)
if dna == "":
    ph.randomize()
else:
    ph.set_from_dna(dna)

print('Rendering phenotype with dna ' + ph.get_binary_string())

print('\nPrint Scenes...') 
sceneKey = bpy.data.scenes.keys()[0] 
print('Using Scene['  + sceneKey + ']') 

print("Modifying scene according to DNA")

if not ph.show_trees.get_bool():
    bpy.data.objects["Tree"].hide_render = True

bpy.data.objects["plane"].particle_systems["ParticleSystem"].seed = ph.trees_seed.get_int()

bpy.data.objects["Lamp"].delta_rotation_euler = (0, ph.sun_position.get_relative_value() * 0.5, 0)

# Loop all objects and try to find Cameras 
print('Looping Cameras') 
c=0 
for obj in bpy.data.objects: 
    # Find cameras that match cameraNames 
    if ( obj.type =='CAMERA') and ( cameraNames == '' or obj.name.find(cameraNames) != -1) : 
      print("Rendering scene["+sceneKey+"] with Camera["+obj.name+"]") 

      # Set Scenes camera and output filename 
      bpy.data.scenes[sceneKey].camera = obj 
      #bpy.data.scenes[sceneKey].render.file_format = 'JPEG' 
      bpy.data.scenes[sceneKey].render.filepath = '//generation' + str(ph.generation) + "/" + ph.get_binary_string()# + "_camera_" + str(c)

      # Render Scene and store the scene 
      bpy.ops.render.render( write_still=True ) 
      c = c + 1 
print('Done!')
