import ee
import folium
import geemap.foliumap as geemap
from google.colab import drive
from google.colab import auth
import time 

date_start="2020-01-01"
date_end="2021-01-01"
def upload(image,description,scale,region,folder):
  drive.mount("/content/gdrive",force_remount=True)
  task = ee.batch.Export.image.toDrive(**{"image": image, "description": description, "scale": scale,"region": region, "crs": "EPSG:4326","folder": folder, 'fileFormat': 'GeoTIFF','skipEmptyTiles': True})
  task.start()
  while task.active():
    print('==> Polling for task (id: {}) Current Status: {}.'.format(task.id,task.status().get("state")))
    time.sleep(5)
  print("*** Task {} status is {}.".format(task.id,task.status().get("state")))

def filter_collection(concentration,metric_type,boundaries): 
    filtered=concentration.filterDate(date_start, date_end).select(metric_type).max().multiply(0.0001).clip(boundaries)
    return filtered

def visualization(image):
  viz = {'min': 0, 'max': 1, 'palette': ["#593a0e","#72601b","#818c3c","#25591f","#19270d"]}
  return image.visualize(**viz)

def print_thumbs(image,region,name):
   thumbnail=image.getThumbURL({
  'dimensions': 500,
  'region': region,})
   print("* Check out online the {} thumbnail URL: {}".format(name,thumbnail))
   

try:
  ee.Initialize()
except Exception as e:
  ee.Authenticate()
  ee.Initialize()

boundaries = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017')
maltese_boundaries = boundaries.filter(ee.Filter.eq('country_na', 'Malta'))
modis_collection=ee.ImageCollection("MODIS/006/MOD13Q1")
evi=filter_collection(modis_collection,"EVI",maltese_boundaries)
ndvi=filter_collection(modis_collection,"NDVI",maltese_boundaries)
evi_viz=visualization(evi)
ndvi_viz=visualization(ndvi)
upload(evi_viz,"EVI_MALTA_2020",50,maltese_boundaries.geometry(),"vegetation_malta")
upload(ndvi_viz,"NDVI_MALTA_2020",50,maltese_boundaries.geometry(),"vegetation_malta")
print_thumbs(evi_viz,maltese_boundaries.geometry(),"EVI")
print_thumbs(ndvi_viz,maltese_boundaries.geometry(),"NDVI")
Map = geemap.Map(center=[35.95,14.4], zoom=11)
Map.addLayer(evi_viz)
Map.add_marker([36.06,14.25],popup='Enhanced Vegetation Index , Malta',icon=folium.Icon(color="green",icon="leaf"))
Map