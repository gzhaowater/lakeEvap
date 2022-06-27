import time
import ee
ee.Initialize()

def extract_meteo(lake):
    def extract(image):
        img_lk = image.reduceRegion(ee.Reducer.mean(), lake.geometry(), 4200)
        return ee.Feature(None, img_lk).set('month', image.date().format('yyyy-MM-dd'))
    forc_ts = teclim.map(extract)
    
    return forc_ts

teclim = ee.ImageCollection("IDAHO_EPSCOR/TERRACLIMATE") \
                .select(['srad','tmmn','tmmx','vpd', 'vs']) \
                .filterDate('1984-1-1','2022-1-1')

lakes = ee.FeatureCollection("users/ee_zhao/Dryland_water/HydroLAKES_v10_voro_buffer_area1")

## run the first 1000 lakes from HydroLAKES dataset
for i in range(0, 1000, 1):
    
    lake = ee.Feature(lakes.toList(1000).get(i))
    
    output = extract_meteo(lake)
    
    outn = ee.String('TerraClimate_').cat(ee.Number(lake.get('Hylak_id')).format('%d'))
    
    task = ee.batch.Export.table.toDrive(
                        collection=output,
                        folder='myFolder',
                        description=outn.getInfo(),
                        fileFormat='CSV',
                        selectors=['month','srad','tmmn','tmmx','vpd', 'vs'])
    task.start()
    print('Submitted ' + str(i))
    
    tasks = ee.data.getTaskList()
    runningTasks = str(tasks).count('RUNNING') + str(tasks).count('READY') 
    
    ## Keep 3 jobs running simultaneously
    while runningTasks >= 3:
        print('Running: ' + str(runningTasks))
        
        time.sleep(60)
        tasks = ee.data.getTaskList()
        runningTasks = str(tasks).count('RUNNING') + str(tasks).count('READY')