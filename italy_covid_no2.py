import ee
import folium
import geemap.foliumap as geemap
from google.colab import drive
from google.colab import auth
import time 

date_start="-03-14"
date_end="-03-25"
def upload(image,description,scale,region,folder):
  drive.mount("/content/gdrive",force_remount=True)
  task = ee.batch.Export.image.toDrive(**{"image": image, "description": description, "scale": scale,"region": region, "crs": "EPSG:4326","folder": folder, 'fileFormat': 'GeoTIFF','skipEmptyTiles': True})
  task.start()
  while task.active():
    print('==> Polling for task (id: {}) Current Status: {}.'.format(task.id,task.status().get("state")))
    time.sleep(5)
  print("*** Task {} status is {}.".format(task.id,task.status().get("state")))

def filter_collection(concentration,year,boundaries): 
    start=year+date_start
    end=year+date_end
    filtered=concentration.filterDate(start, end).select("tropospheric_NO2_column_number_density").median().clip(boundaries)
    return filtered

def visualization(image):
  viz = {'min': 0, 'max': 0.0002, 'palette': ["#54bebe", "#76c8c8", "#98d1d1", "#badbdb", "#dedad2", "#e4bcad", "#df979e", "#d7658b", "#c80064"]}
  return image.visualize(**viz)

def print_thumbs(image,region):
   thumbnail=image.getThumbURL({
  'dimensions': 500,
  'region': region,})
   print("* Check out online the thumbnail URL: {}".format(thumbnail))
   

try:
  ee.Initialize()
except Exception as e:
  ee.Authenticate()
  ee.Initialize()

boundaries = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017')
italian_boundaries = boundaries.filter(ee.Filter.eq('country_na', 'Italy'))
no2_concentration=ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_NO2")
no2_concentration_2019=filter_collection(no2_concentration,"2019",italian_boundaries)
no2_concentration_2020=filter_collection(no2_concentration,"2020",italian_boundaries)
no2_concentration_difference=no2_concentration_2019.subtract(no2_concentration_2020)
no2_concentration_2019_viz=visualization(no2_concentration_2019)
no2_concentration_2020_viz=visualization(no2_concentration_2020)
no2_concentration_difference_viz=visualization(no2_concentration_difference)
upload(no2_concentration_2019_viz,"Nitrogen_Dioxide_Concentration_Italy_2019",1000,italian_boundaries.geometry(),"covid19_no2_italy")
upload(no2_concentration_2020_viz,"Nitrogen_Dioxide_Concentration_Italy_2020",1000,italian_boundaries.geometry(),"covid19_no2_italy")
upload(no2_concentration_difference_viz,"Nitrogen_Dioxide_Concentration_Italy_Difference",1000,italian_boundaries.geometry(),"covid19_no2_italy")
print_thumbs(no2_concentration_2019_viz,italian_boundaries.geometry())
print_thumbs(no2_concentration_2020_viz,italian_boundaries.geometry())
print_thumbs(no2_concentration_difference_viz,italian_boundaries.geometry())
Map = geemap.Map(center=[40,12], zoom=5)
Map.addLayer(no2_concentration_difference_viz)
Map.add_marker([46,10],popup='This is where the main difference is spotted.',icon=folium.Icon(color="orange",icon="stats"))
Map