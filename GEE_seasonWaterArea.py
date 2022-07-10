## This script generates monthly weights for the lakes in the HydroLAKES dataset
## by: Gang Zhao
## 02/01/2020

import time
import ee
ee.Initialize()

def extract_area(lake):
    def extract(image):
        month_dict = image.select('monthly_recurrence') \
                                .addBands(image.select('has_observations').multiply(ee.Image.pixelArea())) \
                                .reduceRegion(ee.Reducer.sum(), lake.geometry(), 30, None, None, True, 1e10)
        return ee.Feature(None, month_dict).set('month', image.get('month'))
        
    output = jrc_mrc.map(extract)
    return ee.Feature(None, {'Hylak_id': lake.get('Hylak_id'),
                             'month': output.aggregate_array('month'),
                             'monthly_recur': output.aggregate_array('monthly_recurrence'),
                             'has_obs': output.aggregate_array('has_observations')})

jrc_mrc = ee.ImageCollection("JRC/GSW1_3/MonthlyRecurrence")

lakes = ee.FeatureCollection("users/ee_zhao/HydroLAKES_v10_voro_buffer_area1")

## group the lakes by groups, each group has 100 lakes
group = ee.Number(100)
n_grp = lakes.size().divide(group).ceil().toInt()

## run the first 1000 groups from HydroLAKES dataset
for i in range(0, 1000, 1):
    i_ee = ee.Number(i)
    
    lakes_grp = ee.FeatureCollection(lakes.toList(group, group.multiply(i_ee)))
    
    output_grp = lakes_grp.map(extract_area)
    
    outn = ee.String('seasonArea_').cat(i_ee.format('%s'))
    
    task = ee.batch.Export.table.toDrive(
                        collection=output_grp,
                        folder='myFolder',
                        description=outn.getInfo(),
                        fileFormat='CSV',
                        selectors=['Hylak_id','month','monthly_recur','has_obs'])
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
