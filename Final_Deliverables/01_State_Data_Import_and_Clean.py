# -*- coding: utf-8 -*-
"""
Step 1

Import polling data from CSVs for all states and clean into a final file for the simulation

"""

import pandas as pd
import numpy as np
import datetime
import glob


"""
Note that this code is designed to bring in data without headers.
"""

## STATE POLLING DATA ##
# Import all State files and clean the data.

state_dir = "FINAL_State_Files_No_Header_UTF8"

states = glob.glob(state_dir + "/*.txt")

states

pld=pd.DataFrame()

for state in states:
    
    state_name = state.replace(state_dir,"").replace(".txt","").replace("\\","")
    
    with open(state, encoding='utf-8-sig') as f:
        i=0
        for aline in f:
            source, date, sample, biden, trump, other = aline.lstrip("\t").split("\t")
            key = state_name + "-" + str(i)
            sample = sample.split()[0].replace('N/A','0')
            
            pld.loc[key, "Source"] = source.strip()
            pld.loc[key, "State"] = state_name.strip()
            pld.loc[key, "Date"] = datetime.datetime.strptime(date, '%m/%d/%Y').date()
            pld.loc[key, "Sample"] = float(sample.replace(",",""))
            pld.loc[key, "Biden"] = float(biden.strip('%'))/100
            pld.loc[key, "Trump"] = float(trump.strip('%'))/100
            pld.loc[key, "Other"] = float(other.strip('%\n'))/100
            i += 1
    
pld = pld.astype({"Source": 'string',
                  "State": 'string',
                  "Sample": 'float',
                  "Biden": 'float',
                  "Trump": 'float',
                  "Other": 'float'})
pld["Date"] = pd.to_datetime(pld["Date"])

# Allocate "Other" evenly between Biden and Trump
pld["Biden"] = pld.Biden + pld.Other/2
pld["Trump"] = pld.Trump + pld.Other/2
pld.drop(["Other"],axis=1)

# remove rows with 0 sample size (this results in std dev = infinity)
pld = pld[pld.Sample != 0]

# p_hat is an estimate for p, choice of Biden or Trump is arbitrary here.
pld["p_hat"] = pld.Biden

# Calculate sample standard deviation as sqrt( (p(1-p))/n )
pld["sample_sd"] = ((pld.p_hat*(1-pld.p_hat))/pld.Sample)**.5


list_polls=list(set(pld.Source))
list_polls
len(list_polls)


## POLLSTER DATA ##

#Read in Pollster Data with Manually altered names
pollster = pd.read_csv("pollster-stats_namesQA.csv", index_col=0, encoding='utf-8-sig')
#Take Columns needed
pollster = pollster[["Source", "538 Grade", "Mean-Reverted Bias", "Bias"]]
pollster[["Bias_Party", "Bias_Numeric"]] = pollster.Bias.str.split(" +",expand=True)
pollster["Bias_Numeric"] = pollster.Bias_Numeric.str.strip("+")
pollster

pollster = pollster.astype({"Source": 'string',
                  "538 Grade": 'string',
                  "Mean-Reverted Bias": 'string',
                  "Bias": 'string',
                  "Bias_Party": 'string',
                  "Bias_Numeric": 'float'})

pollster["Bias_Numeric"] = pollster.Bias_Numeric/100

# Assign preference groupings for poll grades

def assign_grade_bin(row):
    if row["538 Grade"] == "A" or row["538 Grade"] == "A-" or row["538 Grade"] == "A/B" or row["538 Grade"] == "A+":
        return 1
    elif row["538 Grade"] == "B" or row["538 Grade"] == "B-" or row["538 Grade"] == "B/C" or row["538 Grade"] == "B+":
        return 2
    elif row["538 Grade"] == "C" or row["538 Grade"] == "C-" or row["538 Grade"] == "C/D" or row["538 Grade"] == "C+" or row["538 Grade"]=="D" or row["538 Grade"]=="D+" or row["538 Grade"]=="D-" or row["538 Grade"]=="F":
        return 3
    else:
        return np.nan
    
pollster["Grade_Bin"] = pollster.apply(assign_grade_bin, axis=1)

## ELECTORAL VOTES ##

electors= pd.DataFrame()

with open("Electoral_Votes.txt", encoding='utf-8-sig') as f:
    
       for aline in f:
            state, delegates = aline.split("\t")
            state = state.strip().replace(" ", "_")
            
            electors.loc[state, "Delegates"] = int(delegates.strip("\n"))
    
electors = electors.astype({"Delegates": 'int'
                  })

## MERGE AND FINAL EDITS ##

export1 = pd.merge(pld, electors, how="left", left_on='State', right_index=True)
export_final = pd.merge(export1, pollster, how="left", on="Source")
export_final["Bias_Numeric"] = export_final.Bias_Numeric.fillna(0)
export_final["Bias_Party"] = export_final.Bias_Party.fillna("")
export_final["Date"]=pd.to_datetime(export_final.Date)

#prepare bias adjustment corresponding to party
def assign_bias_adj(row):
    if row["Bias_Party"] == "D":
        return float(0-(row["Bias_Numeric"]))
    elif row["Bias_Party"] == "R":
        return 0+float(row["Bias_Numeric"])
    else:
        return 0
    
export_final["Bias_Adjustment"] = export_final.apply(assign_bias_adj, axis=1)

## WRITE TO CSV ##
#commenting out to not overwrite

#pd.DataFrame.to_csv(export_final,"05_Input_PollingData.csv", encoding='utf-8-sig')




