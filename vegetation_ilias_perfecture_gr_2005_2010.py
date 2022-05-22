import ee
from google.colab import drive
import time 
import ipygee as ui
import numpy as np 
import pandas as pd 
import proplot as plot 
import matplotlib.pyplot as plt
from sklearn import datasets, linear_model
import matplotlib.dates as mdates
date_start="2005-01-01"
date_end="2010-12-31"
coordinates=ee.Geometry.Point([21.6, 37.75])
modis_collection=ee.ImageCollection("MODIS/006/MOD13Q1")
try:
  ee.Initialize()
except Exception as e:
  ee.Authenticate()
  ee.Initialize()
time_series = (modis_collection
               .filterDate(date_start,date_end)
               .select("NDVI")
               .map(lambda image: image.multiply(0.0001).copyProperties(image,['system:time_start']))
)

chart_ts = ui.chart.Image.series(**{
    'imageCollection': time_series, 
    'region': coordinates,
    'reducer': ee.Reducer.mean(),
    'scale': 10
})
chart_ts_monthly = chart_ts.dataframe.groupby(pd.Grouper(freq="M")).mean()
time = chart_ts_monthly.index
_, ndvi = plot.subplots(suptitle="Ilias' Perfecture (GR) Vegetation",figsize=(7, 3), tight=True)
ndvi.plot(time,chart_ts_monthly,label="NDVI",
        color='forest green', marker='o')
ndvi.set_xlabel("Time")
ndvi.set_ylabel("NDVI")
ndvi.set_yticks(np.arange(0.2, 0.8, 0.1))
ndvi.format(style='seaborn',title="NDVI Statistics for period 2005-2010")
plt.legend()
plt.tight_layout()
plot.show()
