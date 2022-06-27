import time
import ee
ee.Initialize()

def dic_conv(o):
    d = ee.Dictionary(o)
    group = ee.Number(d.get('group')).format('%d')
    sum = d.get('sum')
    return ee.Feature(None, {'group': group, 'sum':sum})

def extract_lake(lake):
    def extract(image):
        image_area = ee.Image.pixelArea().addBands(image)
      
        area_sums = ee.List(image_area.reduceRegion(
            reducer=ee.Reducer.sum().group(1),
            geometry=lake.geometry(),
            scale=30,
            maxPixels=1e10
        ).get('groups')).map(dic_conv)
        
        area_sums = ee.FeatureCollection(area_sums)
        
        return ee.Feature(None, {'0':0, '1':0, '2':0, '3':0}) \
                 .set('year', image.get('year')) \
                 .set(ee.Dictionary.fromLists(area_sums.aggregate_array('group'), area_sums.aggregate_array('sum')))
    
    area_ts = jrc_yr.map(extract)
    return area_ts

jrc_yr = ee.ImageCollection("JRC/GSW1_3/YearlyHistory")
lakes = ee.FeatureCollection("users/ee_zhao/Dryland_water/HydroLAKES_v10_voro_buffer_area1")

for i in range(0, 1000, 1):
    
    lake = ee.Feature(lakes.toList(1000).get(i))
    
    output = extract_lake(lake)
    
    outn = ee.String('lakeArea_').cat(ee.Number(lake.get('Hylak_id')).format('%d'))
    
    task = ee.batch.Export.table.toDrive(
                        collection=output,
                        folder='myFolder',
                        description=outn.getInfo(),
                        fileFormat='CSV',
                        selectors=['year','0','1','2','3'])
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