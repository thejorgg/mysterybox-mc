"""Export the Minecraft models and render Blender previews with local vanilla textures.

Run with blender --background --python tools/build_assets.py -- --vanilla-jar PATH
"""
import argparse
import bpy
import json
import math
import random
import sys
import zipfile
from pathlib import Path
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument('--vanilla-jar', type=Path, required=True,
                    help='Installed Minecraft Java 26.3 client jar for Blender preview textures')
parser.add_argument('--preview-samples', type=int, default=32,
                    help='Cycles samples for preview PNGs; does not affect Minecraft assets')
arguments = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
options = parser.parse_args(arguments)
vanilla_jar = options.vanilla_jar

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'resourcepack'
ASSETS = PACK / 'assets/mysterybox'
for folder in ['models/item', 'items', 'textures/block']:
    (ASSETS / folder).mkdir(parents=True, exist_ok=True)
(ROOT / 'previews').mkdir(exist_ok=True)
(ROOT / 'model').mkdir(exist_ok=True)

# Preview PNGs live in the local cache, not the distributed resource pack or .blend.
vanilla_cache = Path.home() / '.cache/mysterybox/vanilla' / vanilla_jar.stem
vanilla_cache.mkdir(parents=True, exist_ok=True)
vanilla_images = {}
with zipfile.ZipFile(vanilla_jar) as jar:
    for name, block in (('spruce', 'spruce_planks'), ('bricks', 'bricks')):
        texture = jar.read(f'assets/minecraft/textures/block/{block}.png')
        cached = vanilla_cache / f'{block}.png'
        if not cached.exists() or cached.read_bytes() != texture:
            cached.write_bytes(texture)
        vanilla_images[name] = bpy.data.images.load(str(cached), check_existing=False)

# Custom art is only for the teddy and the two golden question marks. Keep
# the teddy's original pixels by consuming the discarded crate tiles' RNG draws.
rng=random.Random(18)
variation=(-7,-3,0,0,0,3,6)
S = 64
pixels = [0.0] * (S * S * 4)
palette = {
    'iron': (0, (55, 66, 66)), 'glyph': (1, (255, 231, 130)),
    'fur': (2, (151, 100, 60)), 'cream': (3, (225, 189, 131)),
}
former_slots={2:'iron',7:'glyph',8:'fur',9:'cream'}
for former in range(10):
    name=former_slots.get(former)
    if name is None:
        for _ in range(32*32): rng.choice(variation)
        continue
    tile,base=palette[name]
    tx, ty = (tile % 2)*32, (tile // 2)*32
    for y in range(32):
        for x in range(32):
            n = rng.choice(variation)
            if name == 'iron':
                n += 15 if x == 0 or y == 0 else (-15 if x == 31 or y == 31 else 0)
            elif name == 'glyph':
                n = 0
            i = ((S-1-(ty+y))*S + tx+x)*4
            pixels[i:i+4] = [max(0,min(255,c+n))/255 for c in base] + [1]
atlas = bpy.data.images.new('Mysterybox teddy and glyph atlas', S, S, alpha=True)
atlas.pixels.foreach_set(pixels)
atlas.filepath_raw = str(ASSETS/'textures/block/teddy.png')
atlas.file_format='PNG'; atlas.save()
(ASSETS/'textures/block/crate.png').unlink(missing_ok=True)
# Reload encoded sRGB bytes so Blender's preview uses the same texture as Minecraft.
atlas = bpy.data.images.load(atlas.filepath_raw, check_existing=False)

def light_texture(name, color, alpha):
    size=64
    image=bpy.data.images.new(name,size,size,alpha=True)
    p=[]
    for y in range(size):
        height=y/(size-1)
        for x in range(size):
            radius=14+18*height
            distance=abs(x-(size-1)/2)/radius
            edge=max(0,1-distance*distance)**2
            fade=(1-height)**.65
            a=round(alpha*edge*fade*255)/255
            p.extend([*color,a])
    image.pixels.foreach_set(p); image.filepath_raw=str(ASSETS/f'textures/block/{name}.png'); image.file_format='PNG'; image.save()
    return bpy.data.images.load(image.filepath_raw, check_existing=False)

def beam_texture(name, base=False):
    rows=64 if base else 16
    image=bpy.data.images.new(name,16,rows,alpha=True)
    pixels=[]
    for y in range(rows):
        height=y/(rows-1)
        for x in range(16):
            core=max(0,1-abs(x-7.5)/7.5)
            alpha=height*(height+(1-height)*core) if base else 1
            pixels.extend([.3+.65*core,.75+.23*core,1,alpha])
    image.pixels.foreach_set(pixels)
    image.filepath_raw=str(ASSETS/f'textures/block/{name}.png')
    image.file_format='PNG'; image.save()
    return bpy.data.images.load(image.filepath_raw, check_existing=False)

shine_tex=light_texture('shine',(1,.83,.32),.72)
beam_tex=beam_texture('beam')
beam_base_tex=beam_texture('beam_base',base=True)
# Retire the discarded proximity-opacity assets when rebuilding an existing tree.
for name in ('beam_core',*(f'beam_{stage}' for stage in range(8))):
    for directory,suffix in (('textures/block','.png'),('models/item','.json'),('items','.json')):
        (ASSETS/directory/(name+suffix)).unlink(missing_ok=True)

scene=bpy.data.scenes.new('Mystery Box | Minecraft export')
if bpy.context.window is not None:
    bpy.context.window.scene=scene
scene.render.engine='CYCLES'; scene.cycles.samples=max(1,options.preview_samples)
scene.world=bpy.data.worlds.new('Studio dusk'); scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.055,.08,.105,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
scene.view_settings.view_transform='Standard'

materials={}
for name in (*palette, *vanilla_images):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    nodes=mat.node_tree.nodes; p=nodes.get('Principled BSDF'); p.inputs['Roughness'].default_value=.86
    tex=nodes.new('ShaderNodeTexImage'); tex.image=atlas if name in palette else vanilla_images[name]; tex.interpolation='Closest'
    mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
    if name=='glyph':
        mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Emission Color']); p.inputs['Emission Strength'].default_value=.8
    materials[name]=mat
for name,image in [('shine',shine_tex),('beam',beam_tex),('beam_base',beam_base_tex)]:
    mat=bpy.data.materials.new(name); mat.use_nodes=True; nodes=mat.node_tree.nodes; nodes.clear()
    out=nodes.new('ShaderNodeOutputMaterial'); mix=nodes.new('ShaderNodeMixShader'); trans=nodes.new('ShaderNodeBsdfTransparent'); emit=nodes.new('ShaderNodeEmission'); tex=nodes.new('ShaderNodeTexImage'); tex.image=image; tex.interpolation='Closest'
    emit.inputs['Strength'].default_value=1
    links=mat.node_tree.links
    links.new(tex.outputs['Color'],emit.inputs[0]); links.new(tex.outputs['Alpha'],mix.inputs[0]); links.new(trans.outputs[0],mix.inputs[1]); links.new(emit.outputs[0],mix.inputs[2]); links.new(mix.outputs[0],out.inputs[0]); materials[name]=mat

parts={k:[] for k in ['body','lid','shine','beam','beam_base','teddy']}
collections={}
pivots={}
for name in parts:
    col=bpy.data.collections.new(name.upper()); scene.collection.children.link(col); collections[name]=col
    pivot=bpy.data.objects.new(name.upper()+' origin',None); col.objects.link(pivot); pivots[name]=pivot
pivots['lid'].location=(0,-8/16,14/16)

# MC +Y is up and -Z is the front. Blender +Z is up and +Y is front.
def cv(p): return (p[0]/16,-p[2]/16,p[1]/16)
face_indices={'north':(0,1,5,4),'south':(3,7,6,2),'west':(0,4,7,3),'east':(1,2,6,5),'down':(0,3,2,1),'up':(4,5,6,7)}

def _box_element(part,name,a,b,material,faces,rotation):
    x,y,z=a; X,Y,Z=b
    if material in palette:
        tile=palette[material][0]; u=(tile%2)*8; v=(tile//2)*8
        uv={f:[u,v,u+8,v+8] for f in faces}; texture='#atlas'
    elif material in vanilla_images:
        # One model unit = one texel. Long faces are subdivided, never stretched
        # beyond the 16x16 vanilla sprite in Minecraft's stitched texture atlas.
        uv={}
        for f in faces:
            width,height=((X-x,Y-y) if f in ('north','south') else
                          (Z-z,Y-y) if f in ('east','west') else (X-x,Z-z))
            uv[f]=[0,0,round(width,4),round(height,4)]
        texture='#'+material
    else:
        uv={f:[0,0,16,16] for f in faces}; texture='#'+material
    elem={'name':name,'from':[round(v+8,4) for v in a],'to':[round(v+8,4) for v in b],
          'faces':{f:{'uv':uv[f],'texture':texture} for f in faces}}
    if material in ('glyph','shine','beam','beam_base'): elem.update(shade=False,light_emission=15)
    if rotation:
        elem['rotation']={'origin':[v+8 for v in rotation[0]],'axis':rotation[1],'angle':rotation[2],'rescale':False}
    parts[part].append(elem)
    verts=[(x,y,z),(X,y,z),(X,y,Z),(x,y,Z),(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)]
    mesh=bpy.data.meshes.new(name); mesh.from_pydata([cv(v) for v in verts],[],[face_indices[f] for f in faces]); mesh.update()
    obj=bpy.data.objects.new(name,mesh); collections[part].objects.link(obj); obj.parent=pivots[part]; mesh.materials.append(materials[material])
    layer=mesh.uv_layers.new()
    for poly, face in zip(mesh.polygons, faces):
        u0,v0,u1,v1=[c/16 for c in uv[face]]
        for li in poly.loop_indices:
            px,py,pz=verts[mesh.loops[li].vertex_index]
            if face in ('north','south'):
                u=(px-x)/(X-x); v=(py-y)/(Y-y)
                if face=='north': u=1-u
            elif face in ('east','west'):
                u=(pz-z)/(Z-z); v=(py-y)/(Y-y)
                if face=='east': u=1-u
            else:
                u=(px-x)/(X-x); v=(pz-z)/(Z-z)
            layer.data[li].uv=(u0+u*(u1-u0),1-v1+v*(v1-v0))
    if rotation:
        origin=Vector(cv(rotation[0])); axis={'x':0,'y':2,'z':1}[rotation[1]]
        from mathutils import Matrix
        r=Matrix.Rotation(math.radians(rotation[2])*(-1 if rotation[1]=='z' else 1),4,'XYZ'[axis])
        for v in mesh.vertices: v.co=origin+r.to_3x3()@(v.co-origin)
    return obj

def box(part,name,a,b,material,faces=None,rotation=None):
    faces=list(face_indices) if faces is None else faces
    if material not in vanilla_images or rotation:
        return _box_element(part,name,a,b,material,faces,rotation)

    def segments(start, stop):
        while start < stop:
            end=min(start+16,stop)
            yield start,end
            start=end

    # Keep only outside faces; invisible partition walls would darken seams.
    for x,X in segments(a[0],b[0]):
        for y,Y in segments(a[1],b[1]):
            for z,Z in segments(a[2],b[2]):
                visible=[f for f in faces if (
                    f=='north' and z==a[2] or f=='south' and Z==b[2] or
                    f=='west' and x==a[0] or f=='east' and X==b[0] or
                    f=='down' and y==a[1] or f=='up' and Y==b[1])]
                if visible:
                    _box_element(part,name,(x,y,z),(X,Y,Z),material,visible,None)

# Long spruce chest on four plain brick supports spaced across its front.
# The floor is recessed; lid pieces remain local to the rear hinge (0,14,8).
for x in (-18.5,-8.5,3.5,13.5):
    box('body','Brick support',(x,0,-6),(x+5,4,6),'bricks')
box('body','Recessed spruce floor',(-19,4,-7),(19,5,7),'spruce')
for y in (5,8,11):
    for z in (-8,6.5):
        box('body','Long spruce side plank',(-20,y,z),(20,y+3,z+1.5),'spruce')
    for x in (-20,18.5):
        box('body','Spruce end plank',(x,y,-6.5),(x+1.5,y+3,6.5),'spruce')
for z in (-8.5,6.5):
    box('body','Spruce upper rim',(-20,13.5,z),(20,14,z+2),'spruce')
for x in (-20,18):
    box('body','Spruce end rim',(x,13.5,-6.5),(x+2,14,6.5),'spruce')
for z in (-16,-12,-8,-4):
    box('lid','Spruce lid plank',(-20,0,z),(20,2.5,z+4),'spruce')
box('lid','Spruce lid front lip',(-20,-.5,-16.5),(20,1,-16),'spruce')
# Three raised wooden notches echo the reference, without any iron hardware.
for x in (-14,-1,12):
    box('lid','Spruce lid notch',(x,2.5,-15),(x+2,3,-11),'spruce')
# Five-by-seven one-texel marks; the second faces the opposite end of the lid.
glyph=['01110','10001','00001','00010','00100','00000','00100']
for cx,rotated in ((-7,False),(7,True)):
    for row,line in enumerate(glyph[::-1] if rotated else glyph):
        for col,pixel in enumerate(line[::-1] if rotated else line):
            if pixel=='1':
                x=cx+col-2; z=-5-row
                box('lid','Golden question-mark pixel',(x,2.51,z),(x+1,2.64,z+1),'glyph',faces=['up'])
# Broad, low opening glow: 2.5 blocks wide, only 1.125 blocks tall.
for angle in (0,45,-45):
    box('shine','Golden opening cone',(-20,0,0),(20,18,0),'shine',faces=['north','south'],rotation=((0,0,0),'y',angle))
box('shine','Golden opening cone cross',(0,0,-20),(0,18,20),'shine',faces=['west','east'])
pivots['shine'].location=(0,0,9/16)
# Camera-facing double-sided sprites: opaque segmented shaft, transparent foot.
box('beam','Opaque locator sprite',(-6,0,0),(6,16,0),'beam',faces=['north','south'])
pivots['beam'].location=(0,0,49/16); pivots['beam'].scale=(1,1,16)
box('beam_base','Transparent locator base',(-6,0,0),(6,16,0),'beam_base',faces=['north','south'])
pivots['beam_base'].location=(0,0,17/16); pivots['beam_base'].scale=(1,1,2)
collections['beam'].hide_render=True
collections['beam_base'].hide_render=True

# Small cuboid teddy, separate from the crate and revealed on the relocation roll.
box('teddy','Bear torso',(-4,-3,-2.5),(4,4,2.5),'fur')
box('teddy','Bear head',(-4.5,4,-3),(4.5,10,3),'fur')
for x in (-5.5,2.5):
    box('teddy','Square round-corner ear',(x,9,-1.5),(x+3,12,1.5),'fur')
    box('teddy','Ear inner patch',(x+.6,9.6,-1.6),(x+2.4,11.4,-1.5),'cream')
for x in (-6,4):
    box('teddy','Stubby arm',(x,-1,-2),(x+2,4,2),'fur')
for x in (-4.5,1):
    box('teddy','Plush foot',(x,-5,-3.5),(x+3.5,-2,2),'fur')
box('teddy','Belly patch',(-2.6,-2,-2.65),(2.6,2.5,-2.5),'cream')
box('teddy','Muzzle',(-2,4.6,-3.7),(2,7,-3),'cream')
box('teddy','Button nose',(-.75,6,-3.9),(.75,7,-3.7),'iron')
for x in (-2.8,1.6):
    box('teddy','Button eye',(x,7.7,-3.15),(x+1.2,8.9,-3),'iron')
box('teddy','Stitched mouth',(-.2,4.7,-3.8),(.2,5.8,-3.7),'iron')
collections['teddy'].hide_render=True

textures={'atlas':'mysterybox:block/teddy',
          'spruce':'minecraft:block/spruce_planks','bricks':'minecraft:block/bricks',
          **{n:f'mysterybox:block/{n}' for n in ('shine','beam','beam_base')},
          'particle':'minecraft:block/spruce_planks'}
for name,elements in parts.items():
    model={'credit':'Original cuboid geometry; vanilla spruce planks and bricks','ambientocclusion':name in ('body','lid'),'textures':textures,'elements':elements}
    (ASSETS/f'models/item/{name}.json').write_text(json.dumps(model,indent=2)+'\n')
    (ASSETS/f'items/{name}.json').write_text(json.dumps({'model':{'type':'minecraft:model','model':f'mysterybox:item/{name}'}},indent=2)+'\n')
# Export a single closed item for inventory/previews, while keeping animated components separate.
import copy
closed=copy.deepcopy(parts['body'])
for e in copy.deepcopy(parts['lid']):
    for field in ('from','to'):
        e[field][1]+=14; e[field][2]+=8
    closed.append(e)
(ASSETS/'models/item/closed.json').write_text(json.dumps({'ambientocclusion':True,'textures':textures,'elements':closed,'display':{'gui':{'rotation':[25,135,0],'scale':[.38,.38,.38]},'ground':{'scale':[.4,.4,.4]}}},indent=2)+'\n')
(ASSETS/'items/closed.json').write_text(json.dumps({'model':{'type':'minecraft:model','model':'mysterybox:item/closed'}},indent=2)+'\n')
(PACK/'pack.mcmeta').write_text(json.dumps({'pack':{'min_format':[97,1],'max_format':[97,1],'description':'Mystery Box — model assets only · Java 26.3'}},indent=2)+'\n')

lid=pivots['lid']; lid.rotation_euler.x=0; lid.keyframe_insert(data_path='rotation_euler',frame=1)
lid.rotation_euler.x=math.radians(105); lid.keyframe_insert(data_path='rotation_euler',frame=21)
lid.keyframe_insert(data_path='rotation_euler',frame=60)
scene.frame_start=1; scene.frame_end=60; scene.render.fps=20

# Presentation only: excluded from exported Minecraft JSON.
presentation=bpy.data.collections.new('PRESENTATION ONLY'); scene.collection.children.link(presentation)
def stage_object(name,data):
    obj=bpy.data.objects.new(name,data); presentation.objects.link(obj)
    return obj
stage_mesh=bpy.data.meshes.new('Slate stage mesh')
stage_mesh.from_pydata([(-100,-100,-.015),(100,-100,-.015),(100,100,-.015),(-100,100,-.015)],[],[(0,1,2,3)])
ground=stage_object('Slate stage',stage_mesh)
mat=bpy.data.materials.new('Slate stage'); mat.use_nodes=True; mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.028,.043,.052,1); mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85; ground.data.materials.append(mat)
for location,power,size,color in [((1,4,6),650,5,(1,.85,.63)),((-4,1,3),450,4,(.6,.78,1)),((1,-3,4),800,3,(1,.87,.58))]:
    obj=stage_object('Studio light',bpy.data.lights.new('Studio light','AREA'))
    obj.location=location; obj.data.energy=power; obj.data.shape='DISK'; obj.data.size=size; obj.data.color=color; obj.rotation_euler=(Vector((0,0,.6))-obj.location).to_track_quat('-Z','Y').to_euler()
cam=stage_object('Preview camera',bpy.data.cameras.new('Preview camera'))
cam.location=(3.4,4.6,3.3); cam.rotation_euler=(Vector((0,0,1.0))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=4.3; scene.camera=cam
scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.frame_set(1); collections['shine'].hide_render=True
scene.render.filepath=str(ROOT/'previews/closed.png'); bpy.ops.render.render(write_still=True,scene=scene.name)
scene.frame_set(21); collections['shine'].hide_render=False
scene.render.filepath=str(ROOT/'previews/open.png'); bpy.ops.render.render(write_still=True,scene=scene.name)
collections['beam'].hide_render=False
collections['beam_base'].hide_render=False
cam.location=(30,45,38); cam.rotation_euler=(Vector((0,0,15))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=36
scene.render.resolution_x=900; scene.render.resolution_y=1400
scene.render.filepath=str(ROOT/'previews/beam.png'); bpy.ops.render.render(write_still=True,scene=scene.name)
collections['beam'].hide_render=True
collections['beam_base'].hide_render=True
cam.location=(3.4,4.6,3.3); cam.rotation_euler=(Vector((0,0,1.0))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=4.3
scene.render.resolution_x=1400; scene.render.resolution_y=1000
# Save an editable file with the open pose. Vanilla preview PNGs stay external
# in the local cache; only original teddy and lighting textures are packed.
for image in (atlas,shine_tex,beam_tex,beam_base_tex): image.pack()
if bpy.context.screen is not None:
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.data.libraries.write(str(ROOT/'model/mysterybox.blend'),{scene},fake_user=True,compress=True)
# Convert the scene-only library to a normal startup file without the reference scene.
import subprocess
subprocess.run([bpy.app.binary_path,'--background',str(ROOT/'model/mysterybox.blend'),'--python-expr',
    "import bpy; window=bpy.context.window; window and setattr(window,'scene',bpy.data.scenes[0]); bpy.context.preferences.filepaths.save_version=0; bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)"],check=True)
print(json.dumps({'exported':{k:len(v) for k,v in parts.items()},'body_size_blocks':[2.5,.875,1.0625],'lid_open_degrees':105,'beam_section_height_blocks':16}))
