# -*- coding: utf-8 -*-
"""
Step 4

Create the Election Map

"""

import pandas as pd
import numpy as np
# import os as os # running on windows so  back slash

#######
# # set up your working directory # windows uses \\   mac uses // 
# cwd='C:\\Users\\Terrywin10\\Documents\\data science project 1'  

# state_poll_folder=os.path.join(cwd, "All_State_Files_with header_no_space_UTF-8 encoded") ##edit this for statepoll txt files
# state_poll_file=os.path.join(state_poll_folder,'*.txt')
#######

import geopandas
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


##set up the state geopands working directory and PollingDataExport.csv location##
# state_geo_folder=os.path.join(cwd, "geo")
# state_geo_file=os.path.join(state_geo_folder,'states.shp')
# polling_file=os.path.join(cwd, "PollingDataExport.csv")
polling=pd.read_csv("07_Output_ElectoralCollegeSim.csv", index_col=0)
states = geopandas.read_file('states.shp')
#convert to Mercator projection
states = states.to_crs("EPSG:3395")


##group p_hat.mean() by State
state_winning_perc=polling.p_Biden
##Notice the state names have spaces, replaced by _
states["STATE_NAME"]=states["STATE_NAME"].str.replace(" ","_")
##merge p_hat.mean() to geo
states=states.merge(state_winning_perc,left_on='STATE_NAME',right_index= True)


continental = states[states.STATE_ABBR.isin(['AK', 'HI']) == False]


fig, ax = plt.subplots(figsize=(14, 14))

continental.plot(ax=ax, column='p_Biden',cmap='RdBu',vmin=0.1,vmax=0.9)

for state in continental.index:
    ax.annotate(text=continental.STATE_ABBR[state], xy = (continental.geometry[state].centroid.x,
                                                         continental.geometry[state].centroid.y),
                ha = 'center', fontsize=8)
plt.axis('off')

ax_AK = inset_axes(ax, width="25%", height="25%", loc="lower left", borderpad=0)
alaska = states[states['STATE_NAME'] == 'Alaska']

alaska.plot(ax=ax_AK,column='p_Biden',cmap='RdBu',vmin=0.1,vmax=0.9)
ax_AK.annotate(text="AK", xy = (alaska.geometry.centroid.x, 
                                alaska.geometry.centroid.y), ha = 'center', fontsize=8)
ax_AK.set_xticks([])
ax_AK.set_yticks([])
ax_AK.axis('off')

ax_HI = inset_axes(ax, bbox_to_anchor=(.2, 0, 1, 1),
                   bbox_transform=ax.transAxes, width="15%", height="15%", loc="lower left", borderpad=0)
hawaii = states[states['STATE_NAME'] == 'Hawaii']

hawaii.plot(ax=ax_HI,column='p_Biden',cmap='RdBu',vmin=0.1,vmax=0.9)
ax_HI.annotate(text="HI", xy = (hawaii.geometry.centroid.x, 
                                hawaii.geometry.centroid.y), ha = 'center', fontsize=8)
ax_HI.set_xticks([])
ax_HI.set_yticks([])
ax_HI.axis('off')


import matplotlib.colors as colors
# # create the colorbar
norm = colors.DivergingNorm(vmin=0, vcenter=0.5, vmax=1)
cbar = plt.cm.ScalarMappable(norm=norm, cmap='RdBu')

# add colorbar
from mpl_toolkits.axes_grid1 import make_axes_locatable
divider = make_axes_locatable(ax)
ax_cbar = fig.colorbar(cbar, ax=ax,cax=divider.append_axes("right", size="3%", pad=0.6))
# add label for the colorbar
ax_cbar.set_label('Biden Winning Percentage')


#####################################################
import geopandas
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np
import pandas as pd
from bokeh.io import output_notebook
from bokeh.plotting import figure, ColumnDataSource
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool
from bokeh.palettes import brewer
output_notebook()
import json


from shapely import affinity
from shapely.geometry import mapping, shape


polling=pd.read_csv("07_Output_ElectoralCollegeSim.csv", index_col=0)
states = geopandas.read_file('states.shp')
#convert to Mercator projection
states = states.to_crs("EPSG:3395")


##group p_hat.mean() by State
state_winning_perc=polling.p_Biden
##Notice the state names have spaces, replaced by _
states["STATE_NAME"]=states["STATE_NAME"].str.replace(" ","_")
##merge p_hat.mean() to geo
states=states.merge(state_winning_perc,left_on='STATE_NAME',right_index= True)


continental = states[states.STATE_ABBR.isin(['AK', 'HI']) == False]

##function to shift Hawaii and Alaska
def get_geojson():
    '''-
    Returns
    -------
    str - geojson with Alaska and Hawaii translated to fit in extent of Continental US.
    states geojson available at: 
    http://s3.amazonaws.com/bokeh_data/us_states_simplified_albers.geojson
    '''
    with open('us_states_simplified_albers.geojson') as us_states_file:
        geojson = json.loads(us_states_file.read())
        for f in geojson['features']:
            if f['properties']['NAME'] == 'Alaska':
                geom = affinity.translate(shape(f['geometry']), xoff=1.2e6, yoff=-4.8e6)
                geom = affinity.scale(geom, .4, .4)
                geom = affinity.rotate(geom, 30)
                f['geometry'] = mapping(geom)
            elif f['properties']['NAME'] == 'Hawaii':
                geom = affinity.translate(shape(f['geometry']), xoff=4.6e6, yoff=-1.1e6)
                geom = affinity.rotate(geom, 30)
                f['geometry'] = mapping(geom)

    return json.dumps(geojson), geojson
gj,df =get_geojson()


##read json dumps from previous section
map=geopandas.read_file(gj)
##
map.NAME=map.NAME.str.replace(' ','_')
map=map.merge(state_winning_perc, left_on='NAME',right_index=True)
##t_hat for Trump 
map['t_hat']=1-map['p_Biden']

#convert json dumps to geojson
states_geojson=GeoJSONDataSource(geojson=map.to_json())

##Formatting
color_mapper = LinearColorMapper(palette = brewer['RdBu'][10], low = 1, high = 0)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=10,width = 500, height = 10,
                     border_line_color=None,location = (350,0), orientation = 'horizontal',title="Biden                      vs.                       Trump",title_text_font_size = "26px")
hover = HoverTool(tooltips = [ ('State','@NAME'),('Biden%', '@p_Biden'),
                               ('Trump%','@t_hat')])
p = figure(title="2020 Presidential Election", tools=[hover],plot_width=1250, plot_height=600, x_range=(-3e6, 3e6), y_range=(-2e6, 1.5e6))
p.grid.grid_line_alpha = 0
p.axis.visible = False
p.patches("xs","ys",source=states_geojson,
          fill_color = {'field' :'p_Biden', 'transform' : color_mapper},line_color='black',line_alpha= 0.4, alpha=1)
p.add_layout(color_bar, 'below')
##########################

show(p)