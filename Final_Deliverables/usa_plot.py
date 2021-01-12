"""
Geopandas map of US States for use in group project 1.  Adds inset axes for 
Alaska and Hawaii in lower left.
"""

import geopandas
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

states = geopandas.read_file('usaplot/states.shp')

#convert to Mercator projection
states = states.to_crs("EPSG:3395")

continental = states[states.STATE_ABBR.isin(['AK', 'HI']) == False]

fig, ax = plt.subplots(figsize=(14, 14))
continental.plot(ax=ax, cmap='Blues')
for state in continental.index:
    ax.annotate(text=continental.STATE_ABBR[state], xy = (continental.geometry[state].centroid.x,
                                                         continental.geometry[state].centroid.y),
                ha = 'center', fontsize=10)
plt.axis('off')

ax_AK = inset_axes(ax, width="25%", height="25%", loc="lower left", borderpad=0)
alaska = states[states['STATE_NAME'] == 'Alaska']
alaska.plot(ax=ax_AK, color="lightblue")
ax_AK.annotate(text="AK", xy = (alaska.geometry.centroid.x, 
                                alaska.geometry.centroid.y), ha = 'center', fontsize=10)
ax_AK.set_xticks([])
ax_AK.set_yticks([])
ax_AK.axis('off')

ax_HI = inset_axes(ax, bbox_to_anchor=(.2, 0, 1, 1),
                   bbox_transform=ax.transAxes, width="15%", height="15%", loc="lower left", borderpad=0)
hawaii = states[states['STATE_NAME'] == 'Hawaii']
hawaii.plot(ax=ax_HI, color="mediumblue")
ax_HI.annotate(text="HI", xy = (hawaii.geometry.centroid.x, 
                                hawaii.geometry.centroid.y), ha = 'center', fontsize=10)
ax_HI.set_xticks([])
ax_HI.set_yticks([])
ax_HI.axis('off')

#fig.savefig('usa.png', dpi=128)