# From: http://www.blender.org/forum/viewtopic.php?t=19102

# Render all cameras or cameras containing text given with command line argument "cameras". 
# Example: 
# Let's say test.blend file contains cameras "east.01", "east.02", "west.01", "west.02" 
# By executing command "blender -b your_file.blend -P render_all_cameras.py" all 4 cameras will be rendered. 
# Command "blender -b your_file.blend -P render_all_cameras.py  cameras=east" will render "east.01" and "east.02" cameras. 
# Command "blender -b your_file.blend -P render_all_cameras.py  cameras=01" will render "east.01" and "west.01.02" cameras. 


import bpy, bgl, blf,sys 
from bpy import data, ops, props, types, context 
print("\nThis Python script will render your scene with all available cameras") 
print("or with camera(s) matching command line argument 'cameras'") 
print("") 
print("Usage:") 
print("Render all cameras:") 
print("blender -b your_file.blend -P render_all_cameras.py\n") 
print("Render only matching cameras:") 
print("blender -b your_file.blend -P render_all_cameras.py  cameras=east\n") 

cameraNames='' 

# Loop all command line arguments and try to find "cameras=east" or similar 
for arg in sys.argv: 
    words=arg.split('=') 
    if ( words[0] == 'cameras'): 
     cameraNames = words[1] 

print('rendering cameras containing [' + cameraNames + ']') 

print('\nPrint Scenes...') 
sceneKey = bpy.data.scenes.keys()[0] 
print('Using Scene['  + sceneKey + ']') 

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
      bpy.data.scenes[sceneKey].render.filepath = '//camera_' + str(c) 

      # Render Scene and store the scene 
      bpy.ops.render.render( write_still=True ) 
      c = c + 1 
print('Done!')