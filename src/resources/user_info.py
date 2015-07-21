import dilap.core.tools as dpr

import os

obj_world_dir = os.getcwd()
obj_texture_dir = os.getcwd()

osmdata = dpr.resource_path('richmond_virginia.osm')
#osmdata = dpr.resource_path('san-jose_california.osm')
#osmdata = dpr.resource_path('sioux-city_iowa.osm')
#osmdata = dpr.resource_path('new-york_new-york.osm')

info = {
    'exporter':'obj',

    'contentdir':obj_world_dir, 
    'contenttexturedir':obj_texture_dir, 

    'osmdata':osmdata, 
        }

