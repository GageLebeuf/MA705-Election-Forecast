# -*- coding: utf-8 -*-
"""
Step 2

Simulate the Election 

"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


polldata = pd.read_csv("05_Input_PollingData.csv",encoding='utf-8-sig', index_col=0)

all_states = set(list(polldata.State)) 
all_states = sorted(all_states)

#Take a sample using the logic most recent highest graded poll
sample = pd.DataFrame()

for _ in all_states:
        #Separate polls for this state into preference levels (higher grades given preference)
        this_state = polldata[polldata.State == _ ]
        this_state1 = this_state[this_state.Grade_Bin == 1].sort_values(by="Date") 
        this_state2 = this_state[this_state.Grade_Bin == 2].sort_values(by="Date")
        this_state3 = this_state[this_state.Grade_Bin == 3].sort_values(by="Date")
        this_stateN = this_state[this_state.Grade_Bin.isnull()].sort_values(by="Date")
        
        if len(this_state1.index > 0):
            s = this_state1.iloc[0]
        elif len(this_state2.index > 0):
            s = this_state2.iloc[0]
        elif len(this_state3.index > 0):
            s = this_state3.iloc[0]
        elif len(this_stateN.index > 0):
            s = this_stateN.iloc[0]
             
        #Append sample for each state onto sample dataset... after loop we will have 51 records
        sample = sample.append(s, ignore_index=True)
        
sample = sample.set_index('State')
        

def simulate_election(polldata, n):
    
    results = pd.DataFrame(index=all_states)
    electoral_college = pd.DataFrame(index=all_states)
    
    for k in range(n):
    
        sim_poll = poll_dist.rvs() 
        sim_result = np.round(sim_poll)*sample.Delegates
        
        trial_str = "Trial" + str(k+1)
        results[trial_str] = sim_poll
        electoral_college[trial_str] = sim_result
    
    return results, electoral_college

#if x is normally distributed with mean m and y= x+ bias then y is normally distributed with mean m+bias and the same std. dev.
poll_dist = stats.norm((sample.p_hat + sample.Bias_Adjustment), sample.sample_sd)

num_sims = 1000

results, electoral_college = simulate_election(polldata, num_sims)
total_electors = electoral_college.sum()

#Formatting versions of the output

ec_names = electoral_college.astype(bool)

for col in ec_names.columns[ec_names.dtypes == 'bool']:
    ec_names[col] = ec_names[col].map({True: 'Biden', False: 'Trump'})

electoral_college["TotalWins_Biden"] =  electoral_college.astype(bool).sum(axis=1)
electoral_college["TotalWins_Trump"] =  num_sims - electoral_college.TotalWins_Biden
electoral_college["p_Biden"] = electoral_college.TotalWins_Biden / num_sims

totals_cols = electoral_college[["TotalWins_Biden", "TotalWins_Trump", "p_Biden"]]

ec_names = ec_names.merge(totals_cols, how="left", right_index=True, left_index=True)

# Indicating Battle Ground States for this Simulation
def indicate_battleground(row):
    if row["TotalWins_Biden"]/num_sims >= .25 and row["TotalWins_Biden"]/num_sims <= .75:
        return 1
    else:
        return 0
    
electoral_college["BattleGround"] = electoral_college.apply(indicate_battleground, axis=1)
ec_names["BattleGround"] = ec_names.apply(indicate_battleground, axis=1)

pd.DataFrame.to_csv(results,"06_Output_SimulatedPolls.csv", encoding='utf-8-sig')
pd.DataFrame.to_csv(electoral_college,"07_Output_ElectoralCollegeSim.csv", encoding='utf-8-sig')
pd.DataFrame.to_csv(ec_names, "08_Output_ElectoralCollegeSim_CandidateNames.csv", encoding='utf-8-sig')

## GRAPH RESULTS ##


bins_list = np.arange(200,400,10)

print("\nMean number of electoral votes received by Joe Biden is", round(np.mean(total_electors), 2))


count_T_win = len(total_electors[total_electors < 269])
count_Tie = len(total_electors[total_electors == 269])
count_B_win = len(total_electors[total_electors >= 270])

n, bins, patches = plt.hist(total_electors, bins_list, edgecolor='black')

for c, p in zip(bins, patches):
    if c > 0 and c < 270:
        plt.setp(p, 'facecolor', 'red')
    else:
        plt.setp(p, 'facecolor', 'blue')

plt.xlabel("# of Delegates for Joe Biden", fontsize=14)
plt.ylabel("Frequency", fontsize=14)
plt.axvline(270,color="orange", linestyle="dashed")
plt.title("Histogram of Simulated Election Results (N=" + str(num_sims) + ")", fontsize=16)
plt.text(350,(.13*num_sims),"Joe Biden wins \n" + str(count_B_win) + " Trials", color="blue")
plt.text(200,(.13*num_sims),"Donald Trump wins \n" + str(count_T_win) + " Trials", color = "red")
plt.text(240,(.18*num_sims), "Electoral Tie \n" + str(count_Tie) + " Trials", color = "purple")

plt.savefig('09_Results_Histogram.png')
plt.show()




