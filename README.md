# lakeEvap


This GitHub repository includes python scripts for calculating lake evaporation volume. 

__GEE_annualWaterArea.py__: Calculate annual water area for each lake using the [GSW yearly history dataset](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_3_YearlyHistory).
<pre>    The annual water area includes 0: no data, 1: not water, 2: seasonal water, 3: permanent water</pre>
__GEE_seasonWaterArea.py__: Calculate monthly weights for each lake using the [GSW monthly recurrence dataset](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_3_MonthlyRecurrence).\
__GEE_TerraClimate.py__: Calculate lake average meteorological forcings from the [TerraClimate dataset](https://developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_TERRACLIMATE).

__evaporationCalc.py__: Calculate lake average evaporation rate using meteorological forcings (e.g., TerraClimate).
<br/><br/>
<br/><br/>
__The generated datasets can be found at the [GEE App](https://zeternity.users.earthengine.app/view/glev
) and [Zenodo](https://doi.org/10.5281/zenodo.4646620)__
<br/><br/>
<br/><br/>
Reference

1. Zhao, G., Li, Y., Zhou, L., Gao, H. (2022) Evaporative water loss of 1.42 million global lakes. Nature Communications. https://doi.org/10.1038/s41467-022-31125-6
2. Zhao, G., and H. Gao (2019), Estimating reservoir evaporation losses for the United States: Fusing remote sensing and modeling approaches, Remote Sensing of Environment, 226, 109-124. https://doi.org/10.1016/j.rse.2019.03.015
3. Zhao, G., and H. Gao (2018), Automatic correction of contaminated images for assessment of reservoir surface area dynamics. Geophysical Research Letters, 45, 6092-6099. https://doi.org/10.1029/2018GL078343
