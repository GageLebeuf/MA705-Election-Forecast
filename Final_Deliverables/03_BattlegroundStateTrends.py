# -*- coding: utf-8 -*-
"""
Step 3

Create Visualizations for the Battleground States as indicated by the simulations

"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
#from scipy import stats
#from datetime import datetime
#from matplotlib.dates import DateFormatter
#import seaborn as sns

## import data and remove any polls before August 2020
polldataraw = pd.read_csv("05_Input_PollingData.csv",encoding='utf-8-sig', index_col=0)
date_range = pd.date_range('8/1/2020', '11/3/2020', freq='D')

#limit to polls since Sept 2020 
polldataraw['date'] = pd.to_datetime(polldataraw['Date'])
polldata_recent = polldataraw[~(polldataraw['Date'] < '2020-09-01')]

#calculate Biden's lead column
polldata_recent['Biden_lead'] = polldata_recent['Biden'] - polldata_recent['Trump'] 
yrange = np.array(polldata_recent['Biden_lead'])

#average results for states on single date, and remove duplicate rows
polldata = polldata_recent[['Date','State','Biden_lead']].copy()
polldata.groupby(['Date','State']).mean()
polldata.drop_duplicates(keep=False,inplace=True)

#Retrieve results for States indicated as BattleGround by our simulation
sim_results= pd.read_csv("07_Output_ElectoralCollegeSim.csv",encoding='utf-8-sig', index_col=0)
bg= sim_results[sim_results.BattleGround==1]
bgs= bg.index.to_list()

## segment out the battleground state polls into their own data frames

for i in bgs:
    locals()[str(i)+"_polldata"] = polldata[polldata['State']== str(i)]
    locals()[str(i)+"_polldata"].plot('Date','Biden_lead',ylim=(-0.2,0.2))
    plt.gca().invert_xaxis()
    plt.xticks(rotation=45)
    plt.title("Recent " + str(i) +" Polls")
    plt.axhline(linewidth=2, color='r')
    

