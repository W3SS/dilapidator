import dilap.core.base as db
import dilap.construct as dlc
#import dilap.destruct as dld

import bpy,sys
from bpy_extras.io_utils import unpack_list
from bpy_extras.io_utils import unpack_face_list

#########################################################################
### blender interface
#########################################################################

bl_info = {
    'name':'dilapidator',
    'description':'dilapidator procedural mesh generator',
    'category':'Object',
    'author':'Curtis Ogle',
    'version':(1,0),
}
'''#
    "blender": (2, 6, 3),
    "api": 31236,
    "location": "File > Import-Export > Grit",
    "warning": "",
    "category": "Import-Export"
'''#

class dilap_panel(bpy.types.Panel):
    bl_label = "dilap Generator Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "scene"

    def draw(self,context):
        box = self.layout
        col = box.column(align=True)
        col.operator('object.dilaprun',icon="SCRIPT")
        col.operator('object.dilappurge',icon="SCRIPT")

def register():
    print('register dilapidator')
    bpy.utils.register_module(__name__)

def unregister():
    print('unregister dilapidator')
    bpy.utils.unregister_module(__name__)

class dilap_run(bpy.types.Operator):
    '''dilap run'''
    # blender will use this as a tooltip for menu items and buttons.

    # unique identifier for buttons and menu items to reference.
    bl_idname = 'object.dilaprun'
    bl_label = 'dilap run'          # display name in the interface.
    bl_options = {'REGISTER','UNDO'} # enable undo for the operator.
    
    # moved assignment from execute() to the body of the class...
    years = bpy.props.IntProperty(name = 'years',default = 10,min = 1,max = 100)
    #dcontext = bpy.props.StringProperty(name = 'context',default = 'lot')
    dcontext = bpy.props.StringProperty(name = 'context',default = 'continent')

    # execute() is called by blender when running the operator.
    def execute(self,context):

        #dilaps = [dld.dilapidors['ivy']()]
        #dcx = dlc.contextualizer[self.dcontext](sys.modules[__name__],dilaps)
        #dlc.realize(dcx,self.years)
        dlc.teststage(io = sys.modules[__name__])

        return {'FINISHED'}

class dilap_purge(bpy.types.Operator):
    '''dilap purge'''
    # blender will use this as a tooltip for menu items and buttons.

    # unique identifier for buttons and menu items to reference.
    bl_idname = 'object.dilappurge'
    bl_label = 'dilap purge'          # display name in the interface.
    bl_options = {'REGISTER','UNDO'} # enable undo for the operator.
    
    # execute() is called by blender when running the operator.
    def execute(self,context):
        global dmodels_bobjs

        #unselect everything
        # <insert code here, this can vary depending on your situation>
        # bpy.ops.object.select_all()
               
        candidate_list = [o.name for o in bpy.data.objects 
                if o.type == "MESH" and o in dmodels_bobjs]
        for object_name in candidate_list:
            bpy.data.objects[object_name].select = True
        # remove all selected.
        bpy.ops.object.delete()
        # remove the meshes, they have no users anymore.
        for item in bpy.data.meshes:
            try:bpy.data.meshes.remove(item) 
            except:print('mesh still in use...')
        return {'FINISHED'}

#########################################################################

#########################################################################
### functions for creating blender materials
#########################################################################

# create material from texture image
def material_image(name,texture):
    mat = bpy.data.materials.new(name)
    imgpath = db.resource_path(texture)
    tex = bpy.data.textures.new(name,type = 'IMAGE')
    tex.image = bpy.data.images.load(imgpath)
    tex.use_alpha = True
    #mat.use_shadeless = True
    mtex = mat.texture_slots.add()
    mtex.texture = tex
    mtex.texture_coords = 'UV'
    mtex.use_map_color_diffuse = True
    return mat

# create material based on colors
def material_solid(name,diffuse,specular,alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5
    mat.alpha = alpha
    mat.ambient = 1
    return mat

materials = {}
# global list of loaded blender materials
def default_materials():
    global materials
    if not materials.keys():
        materials['generic'] = material_image('generic','orangeboxtex.png')
        materials['grass1'] = material_image('grass1','grass1.dds')
        materials['grass2'] = material_image('grass2','grass2.jpg')
        materials['grass3'] = material_image('grass3','grass3.jpg')
        materials['grass4'] = material_image('grass4','grass4.png')
        materials['brick1'] = material_image('brick1','brick1.jpg')
        materials['brick2'] = material_image('brick2','brick2.jpg')
        materials['concrete1'] = material_image('concrete1','concrete1.png')
        materials['concrete2'] = material_image('concrete2','concrete2.png')
        materials['concrete3'] = material_image('concrete3','concrete3.jpg')
        
    '''#
    for ke in materials.keys():
        if ke.startswith('brick'):
            m = materials[ke]
            t = m.texture_slots[0]
            #m.use_transparency = True
            #t.use_map_alpha = True
            t.scale = (0.5,0.5,1.0)
        if ke.startswith('grass'):
            m = materials[ke]
            t = m.texture_slots[0]
            m.use_transparency = True
            t.use_map_alpha = True
            #t.scale = (0.5,0.5,1.0)
        print('matdir',dir(materials['generic']))
    '''#
    return materials

# must exist for dilap context usage
def write_materials():
    default_materials()
    print('materials generated')

#########################################################################

#########################################################################
### functions to create blender space objects from geometry data
#########################################################################

# put the object into the scene, making it active if make_active
def object_to_scene(obj,make_active = True):
    bpy.context.scene.objects.link(obj)
    if make_active:bpy.context.scene.objects.active = obj
    dmodels_bobjs.append(obj)

# create a blender object from a blender mesh
def object_from_mesh(name,mesh,obj_loc = (0,0,0),mats = None):
    obj = bpy.data.objects.new(name,mesh)
    obj.location = obj_loc
    if not mats is None:
        mats = [materials[mat] for mat in mats]
        [obj.data.materials.append(ma) for ma in mats]
    return obj

# create a blender mesh from model geometry data
def mesh_from_data(name,coords,uvs,faces,face_mats,mats):
    mesh = bpy.data.meshes.new(name)
    if not mats is None:
        [mesh.materials.append(materials[ma]) for ma in mats]
    mesh.vertices.add(len(coords))
    mesh.vertices.foreach_set('co',unpack_list(coords))
    mesh.tessfaces.add(len(faces))
    mesh.tessfaces.foreach_set('vertices_raw',unpack_face_list(faces))
    mesh.tessfaces.foreach_set('material_index',face_mats)
    mesh.tessface_uv_textures.new()
    for fdx in range(len(faces)):
        fa = faces[fdx]
        mesh.tessface_uv_textures[0].data[fdx].uv1 = uvs[fa[0]].to_tuple()
        mesh.tessface_uv_textures[0].data[fdx].uv2 = uvs[fa[1]].to_tuple() 
        mesh.tessface_uv_textures[0].data[fdx].uv3 = uvs[fa[2]].to_tuple() 
    mesh.update()
    return mesh

#########################################################################

#########################################################################
### functions to connect dilap models to blender space
#########################################################################

dmodels_bobjs = []

# build models on some arrangement of models
# return a list of blender space objects generated from models
def build_models(*args,**kwargs):
    default_materials()
    bobjs = []
    for ag in args:
        if not type(ag) is type([]):
            bobjs.append(build_model(ag,**kwargs))
        else:[bobjs.append(build_model(p,**kwargs)) for p in ag]
    #dmodels_bobjs.extend(bobjs)
    return bobjs
    
# build a single model into the blender world
# return the resulting blender space object
def build_model(mod,**kwargs):
    oname = mod.filename.replace('.mesh','.000')
    mname = oname+'.'+'mesh'

    coords = mod.pcoords
    uvs = mod.ucoords
    faces = mod.faces
    face_mats = mod.face_mats
    mats = mod.mats
    oloc = (0,0,0)

    mesh = mesh_from_data(mname,coords,uvs,faces,face_mats,mats)
    obj = object_from_mesh(oname,mesh,oloc,mats)
    object_to_scene(obj)
    return obj

# build a single model into the blender world
# return the resulting blender space object
def build_model2(mod,**kwargs):

    default_materials()

    oname = mod.filename.replace('.mesh','.000')
    mname = oname+'.'+'mesh'

    ps = mod.pset.ps
    us = mod.uset.ps

    mats = ['generic','concrete1','grass2']
    fs_lookup = {}
    for fmx in range(len(mats)):
        fs_lookup[mats[fmx]] = fmx

    for gfx in mod.gfxmeshes:
        faces = [f for f in gfx.faces if not f is None]
        face_mats = [fs_lookup[gfx.fs_mats[f][1]] for f in faces]
        oloc = (0,0,0)

        #mesh = mesh_from_data(mname,ps,us,faces,face_mats,mats)
        #def mesh_from_data(name,ps,us,faces,face_mats,mats):

        mesh = bpy.data.meshes.new(mname)
        if not mats is None:
            [mesh.materials.append(materials[ma]) for ma in mats]
        mesh.vertices.add(len(ps))
        mesh.vertices.foreach_set('co',unpack_list(ps))
        mesh.tessfaces.add(len(faces))
        mesh.tessfaces.foreach_set('vertices_raw',unpack_face_list(faces))
        mesh.tessfaces.foreach_set('material_index',face_mats)
        mesh.tessface_uv_textures.new()
        for fdx in range(len(faces)):
            fa = faces[fdx]
            mesh.tessface_uv_textures[0].data[fdx].uv1 = tuple(us[fa[0]])[:-1]
            mesh.tessface_uv_textures[0].data[fdx].uv2 = tuple(us[fa[1]])[:-1]
            mesh.tessface_uv_textures[0].data[fdx].uv3 = tuple(us[fa[2]])[:-1]
        mesh.update()




    '''#
    faces = mod.gfxmeshes[0].faces
    face_mats = [fs_lookup[mod.gfxmeshes[0].fs_mats[f]] for f in faces]
    #face_mats = [0]*len(faces)
    #mats = ['generic']
    oloc = (0,0,0)

    #mesh = mesh_from_data(mname,ps,us,faces,face_mats,mats)
    #def mesh_from_data(name,ps,us,faces,face_mats,mats):

    mesh = bpy.data.meshes.new(mname)
    if not mats is None:
        [mesh.materials.append(materials[ma]) for ma in mats]
    mesh.vertices.add(len(ps))
    mesh.vertices.foreach_set('co',unpack_list(ps))
    mesh.tessfaces.add(len(faces))
    mesh.tessfaces.foreach_set('vertices_raw',unpack_face_list(faces))
    mesh.tessfaces.foreach_set('material_index',face_mats)
    mesh.tessface_uv_textures.new()
    for fdx in range(len(faces)):
        fa = faces[fdx]
        mesh.tessface_uv_textures[0].data[fdx].uv1 = tuple(us[fa[0]])[:-1]
        mesh.tessface_uv_textures[0].data[fdx].uv2 = tuple(us[fa[1]])[:-1]
        mesh.tessface_uv_textures[0].data[fdx].uv3 = tuple(us[fa[2]])[:-1]
    mesh.update()
    '''#



    obj = object_from_mesh(oname,mesh,oloc,mats)
    object_to_scene(obj)
    return obj

#########################################################################

# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register()










