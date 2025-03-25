# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 10:18:31 2022
last updated 25-03-2024
@author: jana_s
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.ndimage.interpolation import shift

##############################################
### 1. Input data ############################
##############################################

#Input Data
#Adapt the data in this section to project the biogas production pf your system
VF = 0.0055  	                                   #Input: volume of fermenter in m^3   
HRT1 = 25                                          #Input: hydraulic retention time Substrate Mix 1 (should be between 20 and 50 d)
HRT2 = 25                                          #Input: hydraulic retention time Substrate Mix 2 (should be between 20 and 50 d)
HRT3 = 25                                          #Input: hydraulic retention time Substrate Mix 3 (should be between 20 and 50 d)
HRT4 = 25                                          #Input: hydraulic retention time Substrate Mix 4 (should be between 20 and 50 d)
tm = 292                                           #Input: time span for which the biogas production should be projected (d)
tc1 = 167                                          #Input: day of substrate mixture change (d)
tc2 = 192                                          #Input: day of substrate mixture change (d)
tc3 = 242                                          #Input: day of substrate mixture change (d)

BR = 3                                             #Input: organic loading rate (should be between 1.5 and 3.5 kgVS/m^3/d)
Substrates1 = ['S_R_As','L_P_As','GD']             #Input: short names of Substrates to be used in Mix 1
Substrates2 = ['S_R_Ca','G_P_As','GD']             #Input: short names of Substrates to be used in Mix 2
Substrates3 = ['S_R_Ca','G_P_As','GD']             #Input: short names of Substrates to be used in Mix 3
Substrates4 = ['S_R_Ca','G_P_As','GD']             #Input: short names of Substrates to be used in Mix 4
ShareSubstrates1 = [0.25,0.25,0.5]                 #Input: shares of Substrates to be used in Mix 1
ShareSubstrates2 = [0.25,0.25,0.5]                 #Input: shares of Substrates to be used in Mix 2
ShareSubstrates3 = [0.4,0.4,0.2]                   #Input: shares of Substrates to be used in Mix 3
ShareSubstrates4 = [0.5,0.5,0.0]                   #Input: shares of Substrates to be used in Mix 3

#printing a summary of the model input
print("\nThe biogas production is modeled for:\n a fermenter with a volume of "+(f"{(VF)}")+ " m^3,"+\
      "\n a hydraulic retention time of "+(f"{(HRT1)}")+" days,"\
      "\n a time span of "+(f"{(tm)}")+" days, and"\
      "\n a substrate change after "+(f"{(tc1)}")+", "+(f"{(tc2)}")+" and "+(f"{(tc3)}")+" days."\
      "\n The organic loading rate is set to "+(f"{(BR)}")+" kgVS/m^3/d."\
      "\nThe following Substrates are used in Mix 1:")
for i in range(len(Substrates1)):
    print(" "f"{(ShareSubstrates1[i])*100}"+ " % " + Substrates1[i])
print("The following Substrates are used in Mix 2:")
for i in range(len(Substrates2)):
    print(" "f"{(ShareSubstrates2[i])*100}"+ " % " + Substrates2[i])
print("The following Substrates are used in Mix 3:")
for i in range(len(Substrates3)):
    print(" "f"{(ShareSubstrates3[i])*100}"+ " % " + Substrates3[i])
print("The following Substrates are used in Mix 4:")
for i in range(len(Substrates4)):
    print(" "f"{(ShareSubstrates4[i])*100}"+ " % " + Substrates4[i])

#import database with substrate characteristics 
data = pd.read_csv('data/Database_CoAgrowPlus.csv', sep=';')

#################################################
### 2. Input processing #########################
#################################################

#add columns with dry mass to data set
data['DM'] = 1-data["WC"]                                         # creates a column with dry mass content of substrates in %

#creat data frames for shares in substrate mixtures
Share1 = pd.DataFrame(np.zeros([len(data),1]),columns=['Share1']) # creat columns for Shares1 
Share2 = pd.DataFrame(np.zeros([len(data),1]),columns=['Share2']) # creat columns for Shares2 
Share3 = pd.DataFrame(np.zeros([len(data),1]),columns=['Share3']) # creat columns for Shares3 
Share4 = pd.DataFrame(np.zeros([len(data),1]),columns=['Share4']) # creat columns for Shares4 
data=pd.concat([data,Share1,Share2,Share3,Share4],axis=1)

#assign shares of substrates according to the input 
for i in range(len(Substrates1)):
    for j in range(len(data)):
        if data["Short"][j]==Substrates1[i]:
            data["Share1"][j]=ShareSubstrates1[i]

for i in range(len(Substrates2)):
    for j in range(len(data)):
        if data["Short"][j]==Substrates2[i]:
            data["Share2"][j]=ShareSubstrates2[i]

for i in range(len(Substrates3)):
    for j in range(len(data)):
        if data["Short"][j]==Substrates3[i]:
            data["Share3"][j]=ShareSubstrates3[i]

for i in range(len(Substrates4)):
    for j in range(len(data)):
        if data["Short"][j]==Substrates4[i]:
            data["Share4"][j]=ShareSubstrates4[i]

# safe substrate charateristics in lists/vectors 
Share1 = data["Share1"]                              #Share of the substrates in Mix1
Share2 = data["Share2"]                              #Share of the substrates in Mix2
Share3 = data["Share3"]                              #Share of the substrates in Mix3
Share4 = data["Share4"]                              #Share of the substrates in Mix4
WC = data["WC"]                                      #Water Content of the substrates (%)
DM = data["DM"]                                      #Dry Mass content of the substrates (%)
VS = data["VS"]                                      #Volatile Solids Content of the substrates (% DM)
P = data["P"]                                        #kinetic Parameter P
Rm = data["Rm"]                                      #kinetic Parameter Rm
l = data["l"]                                        #kinetic Paramter l
C = data["C"]                                        #C Content of the substrates (g/kg)
N = data["N"]                                        #N Content of the substrates (g/kg)
methane = data["methane"]                            #methane Content of produced biogas (%)

#volume feed daily 
Volume_Flow = VF/HRT1                                #(m^3 / d)
Volume_Flow2 = VF/HRT2                               #(m^3 / d)
Volume_Flow3 = VF/HRT3                               #(m^3 / d)
Volume_Flow4 = VF/HRT4                               #(m^3 / d)

#################################################
### 3. Biogas production of mixtures ############
#################################################

#Gompertz-Function for the estimation of biogas production  
def Gompertz_Function(t, P, Rm, l):
        return P * np.exp (-1*np.exp(((Rm*np.e)/P)*(l-t)+1))

#preparing variables for applying the Gompertz function 
ns = len(data)                         #range Share is the number of substrates in the data base
BGP1 = np.zeros([HRT1+1,ns])           #array with zeros width # substrates (ns) and length # time steps (nt)
BGP2 = np.zeros([HRT2+1,ns])           #array with zeros width # substrates (ns) and length # time steps (nt)
BGP3 = np.zeros([HRT3+1,ns])           #array with zeros width # substrates (ns) and length # time steps (nt)
BGP4 = np.zeros([HRT4+1,ns])           #array with zeros width # substrates (ns) and length # time steps (nt)

#Gompertz_funktion for every substrate is calculated for a full HRT
for i in range(ns): 
    BGP1[:,i] = Gompertz_Function(range(HRT1+1), P[i], Rm[i], l[i])
for i in range(ns): 
    BGP2[:,i] = Gompertz_Function(range(HRT2+1), P[i], Rm[i], l[i])
for i in range(ns): 
    BGP3[:,i] = Gompertz_Function(range(HRT3+1), P[i], Rm[i], l[i])
for i in range(ns): 
    BGP4[:,i] = Gompertz_Function(range(HRT4+1), P[i], Rm[i], l[i])

#(cummulative) Biogasproduction of Substrates according to their share in Mix 1
BGP_Share1 = np.zeros([HRT1+1,ns])
for i in range(ns): 
    BGP_Share1[:,i] = BGP1[:,i]*Share1[i]

#(cummulative) Biogasproduction of Substrates according to their Share in Mix 2
BGP_Share2 = np.zeros([HRT2+1,ns])
for i in range(ns): 
    BGP_Share2[:,i] = BGP2[:,i]*Share2[i]
    
#(cummulative) Biogasproduction of Substrates according to their Share in Mix 3
BGP_Share3 = np.zeros([HRT3+1,ns])
for i in range(ns): 
    BGP_Share3[:,i] = BGP3[:,i]*Share3[i]
    
#(cummulative) Biogasproduction of Substrates according to their Share in Mix 4
BGP_Share4 = np.zeros([HRT4+1,ns])
for i in range(ns): 
    BGP_Share4[:,i] = BGP4[:,i]*Share4[i]
    
#total Biogasproduction (cummulative) of the substrate Mix 1 and Mix 2 
BGP_perkgVS_Mix1 = sum(np.transpose(BGP_Share1))
BGP_perkgVS_Mix2 = sum(np.transpose(BGP_Share2))
BGP_perkgVS_Mix3 = sum(np.transpose(BGP_Share3))
BGP_perkgVS_Mix4 = sum(np.transpose(BGP_Share4))

#################################################
### 4. Mix 1...4 check, characteristics, BGP ####
#################################################

### Mix 1 #######################################

#Input Check Mix 1 - printing a check-up report
print("\nMix 1")
print("")
if sum(Share1) == 1:
    print ("\N{check mark} Input 1 is correct.")
elif sum(Share1) < 1:
    print ("\u2718 Input 1 is too low.")
elif sum(Share1) > 1:
    print("\u2718 Input 1 is too high.")

#check input for Loading Rate per Unit Volume (BR)  
if BR > 3.5:
    print("\u2718 The Loading Rate per Unit Volume is too high. A longer Hydraulic Retention Time is needed.")
elif BR < 1.5:
    print("\u2718 The Loading Rate per Unit Volume is very low. Consider shorter Hydraulic Retention Time.")
else: 
    print("\N{check mark} The Loading Rate per Unit Volume of " + (f"{(BR):.2f}") + " lies in the optimum range.")
    
#check input for Carbon to Nitrogen Ratio
CN_Mix1 = sum(C*Share1)/sum(N*Share1)

if CN_Mix1 < 10:
    print("\u2718 C/N - Ratio " + "(" + (f"{(CN_Mix1):.2f}") + ") is too low")
elif CN_Mix1 > 35: 
    print("\u2718 C/N - Ratio " + "(" + (f"{(CN_Mix1):.2f}") + ") is too high")
else:
    print("\N{check mark} C/N - Ratio " + "(" + (f"{(CN_Mix1):.2f}") + ") is in the optimum range")
    
#Water, Dry Mass and Volatile Solids Content of the Substrate Mix (based on FM)
#Methane content of biogas produced from Substrate Mix1
WC_Mix1 = sum(Share1*WC)                             #(% FM)
DM_Mix1 = sum(Share1*DM)                             #(% FM)
VS_Mix1 = sum(Share1*DM*VS)                          #(% FM)
VS_DM_Mix1 = sum(Share1*VS)                          #(% DM)
methane_Mix1 = sum(Share1*methane)                   #(%)

#amount of fresh substrate to be fed to the reator per day
Feed_Mix1 = VF*BR/VS_Mix1                            #(kg FM/d)
if Feed_Mix1 < 0.1:
    print ("The amount of substrate to be fed daily is " + (f"{(Feed_Mix1*1000):.2f}") + " g FM.")
else:    
    print ("The amount of substrate to be fed daily is " + (f"{(Feed_Mix1):.2f}") + " kg FM.")
       
#Need for additional water
#Water content for wet fermentation needs to be 0.88 or higher
add_water_perday = Volume_Flow*1000 - (Feed_Mix1)      #(L/d)
add_water = (Volume_Flow*1000 - (Feed_Mix1))/Feed_Mix1 #(L/kg FM/d)
if Feed_Mix1 < 0.1:
    print("You have to add " + (f"{(add_water_perday)*1000:.2f}") + " mL water to substrate mix initially.")
elif add_water <= 0 :
    print("No additional water is needed!")
else:
    print ("You have to add " + (f"{(add_water):.2f}") + " kg water per kg substrate mix initially.")

#Volatile Solids Content in the mashed substrate mix    
VS_Mashed_Mix1 = Feed_Mix1*VS_Mix1/(Volume_Flow*1000) #(%)
WC_Mashed_Mix1 = (add_water_perday+(Feed_Mix1*WC_Mix1))/(add_water_perday+Feed_Mix1) #(%)

#check watercontent 
if WC_Mashed_Mix1 < 0.88:
    print("\u2718 Water content of the mashed substrate is too low. You have to decrease the loading rate per unit volume")
else:
    print("\N{check mark} Water content of the mashed substrate of " + (f"{(WC_Mashed_Mix1*100):.2f}") + " % lies in the optimum range.")

#Water Recovery
#Pressing down to 50% water content
water_recovery_perday = add_water_perday - (Feed_Mix1*DM_Mix1) 
water_recovery = add_water - ((0.5 - WC_Mix1) / (1 - 0.5))
if Feed_Mix1 < 0.1:
    print((f"{(water_recovery_perday*1000):.2f}") + " mL water can be recovered per day.")
else:
    print((f"{(water_recovery):.2f}") + " kg water can be recovered per kg FM used.")

#Additional water need
if add_water > water_recovery:
    add_water_need = (add_water - water_recovery) * Feed_Mix1
    if Feed_Mix1 < 0.1:
        print("Each day, an amount of " + (f"{(add_water_need*1000):.2f}") + " g water must be supplied externally.")
    else:
        print("Each day, an amount of " + (f"{(add_water_need):.2f}") + " kg water must be supplied externally.")
else:
    add_water_need = 0
    
#daily Biogas production over HRT per kgVS   
BGP_daily_perkgVS_Mix1 = np.diff(BGP_perkgVS_Mix1)   #L / (kgVS * d)

#Biogas production with regards to Substrate Input
#Total daily production in L / d
BGP_daily_Mix1 = Feed_Mix1 * VS_Mix1 * BGP_daily_perkgVS_Mix1
BGP_Mix1 = Feed_Mix1 * VS_Mix1 * BGP_perkgVS_Mix1

#Methane production with regards to Substrate Input
MP_daily_Mix1 = BGP_daily_Mix1 * methane_Mix1
MP_Mix1 = BGP_Mix1 * methane_Mix1

#Production related to the feed of the individual days (i.e. total production from the used substrat mixture)
BGP_daily_fullduration_Mix1 = np.append(BGP_daily_Mix1,[0]*(tm-HRT1))

#creating array with production of single feeds of each day 
BGP_dailyfeed_Mix1 = np.zeros([tm,tm])

for i in range(tc1):
    BGP_dailyfeed_Mix1[:,i] = shift(BGP_daily_fullduration_Mix1,i, cval=0)

#sum of the biogas production at every day 
BGP_sum_Mix1 = sum(np.transpose(BGP_dailyfeed_Mix1))
print("The expected biogas production is "+ (f"{(BGP_sum_Mix1[tc1-1]):.2f}") + " L per day")

################ Substrate Change ##############################
# Substrate change at a specific time point tc1

### Mix 2 #######################################

#Input Check Mix 2  - printing a check-up report
print("\nMix 2")
print("")
if sum(Share2) == 1:
    print ("\N{check mark} Input 2 is correct.")
elif sum(Share2) < 1:
    print ("\u2718 Input 2 is too low.")
elif sum(Share2) > 1:
    print("\u2718 Input 2 is too high.")
    
#Check Loading Rate per Unit Volume [BR]  
if BR > 3.5:
    print("\u2718 The Loading Rate per Unit Volume is too high. A longer Hydraulic Retention Time is needed.")
elif BR < 1.5:
    print("\u2718 The Loading Rate per Unit Volume is very low. Consider shorter Hydraulic Retention Time.")
else: 
    print("\N{check mark} The Loading Rate per Unit Volume of " + (f"{(BR):.2f}") + " lies in the optimum range.")

#Carbon to Nitrogen Ratio
CN_Mix2 = sum(C*Share2)/sum(N*Share2)

if CN_Mix2 < 10:
    print("\u2718 C/N - Ratio " + "(" + (f"{(CN_Mix2):.2f}") + ") is too low")
elif CN_Mix2 > 40: 
    print("\u2718 C/N - Ratio " + "(" + (f"{(CN_Mix2):.2f}") + ") is too high")
else:
    print("\N{check mark} C/N - Ratio " + "(" + (f"{(CN_Mix2):.2f}") + ") is in the optimum range")    
 
#Water, Dry Mass and Volatile Solids Content of the Substrate Mix (based on FM)
#Methane content of biogas produced from Substrate Mix1
WC_Mix2 = sum(Share2*WC)                             #(%)
DM_Mix2 = sum(Share2*DM)                             #(%)
VS_Mix2 = sum(Share2*DM*VS)                          #(%)
methane_Mix2 = sum(Share2*methane)                   #(%)

#amount of fresh substrate to be fed to the reator per day
Feed_Mix2 = VF*BR/VS_Mix2                            #(kg FM/d)
if Feed_Mix2 < 0.1:
    print ("The amount of substrate to be fed daily is " + (f"{(Feed_Mix2*1000):.2f}") + " g FM.")
else:    
    print ("The amount of substrate to be fed daily is " + (f"{(Feed_Mix2):.2f}") + " kg FM.")

#Need for additional water
#Water content for wet fermentation needs to be 0.88 or higher
add_water_perday = Volume_Flow2*1000 - (Feed_Mix2) #(L/d)
add_water = (Volume_Flow2*1000 - (Feed_Mix2))/Feed_Mix2 #(L/kg FM/d)
if Feed_Mix2 < 0.1:
    print("You have to add " + (f"{(add_water_perday)*1000:.2f}") + " mL water to substrate mix initially.")
elif add_water <= 0 :
    print("No additional water is needed!")
else:
    print ("You have to add " + (f"{(add_water):.2f}") + " kg water per kg substrate mix initially.")

#Volatile Solids Content in the mashed substrate mix    
VS_Mashed_Mix2 = Feed_Mix2*VS_Mix2/(Volume_Flow2*1000) #(%)
WC_Mashed_Mix2 = (add_water_perday+(Feed_Mix2*WC_Mix2))/(add_water_perday+Feed_Mix2) #(%)

#check watercontent 
if WC_Mashed_Mix2 < 0.88:
    print("\u2718 Water content of the mashed substrate is too low. You have to decrease the loading rate per unit volume")
else:
    print("\N{check mark} Water content of the mashed substrate of " + (f"{(WC_Mashed_Mix2*100):.2f}") + " % lies in the optimum range.")

#Water Recovery
#Pressing down to 50% water content
water_recovery_perday = add_water_perday - (Feed_Mix2*DM_Mix2) 
water_recovery = add_water - (0.5-WC_Mix2)
if Feed_Mix2 < 0.1:
    print((f"{(water_recovery_perday*1000):.2f}") + " mL water can be recovered per day.")
else:
    print((f"{(water_recovery):.2f}") + " kg water can be recovered per kg FM used.")
      
#Additional water need
if add_water > water_recovery:
    add_water_need = (add_water - water_recovery) * Feed_Mix2
    if Feed_Mix2 < 0.1:
        print("Each day, an amount of " + (f"{(add_water_need*1000):.2f}") + " g water must be supplied externally.")
    else:
        print("Each day, an amount of " + (f"{(add_water_need):.2f}") + " kg water must be supplied externally.")
else:
    add_water_need = 0
    
#daily Biogas production over HRT per kgVS   
BGP_daily_perkgVS_Mix2 = np.diff(BGP_perkgVS_Mix2)   #L / (kgVS * d)

#Biogas production with regards to Substrate Input
#Total daily production in L / d
BGP_daily_Mix2 = Feed_Mix2 * BGP_daily_perkgVS_Mix2 * VS_Mix2
BGP_Mix2 = Feed_Mix2 * VS_Mix2 * BGP_perkgVS_Mix2

#Methane production with regards to Substrate Input
MP_daily_Mix2 = BGP_daily_Mix2 * methane_Mix2
MP_Mix1_Mix2 = BGP_Mix2 * methane_Mix2

#Production related to the feed of the individual days (i.e. total production from the used substrat mixture)
BGP_daily_fullduration_Mix2 = np.insert(BGP_daily_Mix2,0,[0]*tc1) 
BGP_daily_fullduration_Mix2 = np.append(BGP_daily_fullduration_Mix2,[0]*(tm-tc1-HRT2))

#creating array with production of single feeds of each day 
BGP_dailyfeed_Mix2 = np.zeros([tm,tm])

for i in range(tc2-tc1):
    BGP_dailyfeed_Mix2[:,tc1+i] = shift(BGP_daily_fullduration_Mix2,i, cval=0)
    
#sum of the biogas production at every day 
BGP_sum_Mix2 = sum(np.transpose(BGP_dailyfeed_Mix2))
print("The expected biogas production is "+ (f"{(BGP_sum_Mix2[tc2-1]):.2f}") + " L per day")
print("")

################ Substrate Change ##############################
# Substrate change at a specific time point tc2

### Mix 3 #######################################

#Input Mix 3 - printing a check-up report
print("\nMix 3")
print("")
if sum(Share3) == 1:
    print ("\N{check mark} Input 3 is correct.")
elif sum(Share3) < 1:
    print ("\u2718 Input 3 is too low.")
elif sum(Share3) > 1:
    print("\u2718 Input 3 is too high.")
    
#Check Loading Rate per Unit Volume [BR]  
if BR > 3.5:
    print("\u2718 The Loading Rate per Unit Volume is too high. A longer Hydraulic Retention Time is needed.")
elif BR < 1.5:
    print("\u2718 The Loading Rate per Unit Volume is very low. Consider shorter Hydraulic Retention Time.")
else: 
    print("\N{check mark} The Loading Rate per Unit Volume of " + (f"{(BR):.2f}") + " lies in the optimum range.")

#Carbon to Nitrogen Ratio
CN_Mix3 = sum(C*Share3)/sum(N*Share3)

if CN_Mix3 < 10:
    print("\u2718 C/N - Ratio " + "(" + (f"{(CN_Mix3):.2f}") + ") is too low")
elif CN_Mix3 > 40: 
    print("\u2718 C/N - Ratio " + "(" + (f"{(CN_Mix3):.2f}") + ") is too high")
else:
    print("\N{check mark} C/N - Ratio " + "(" + (f"{(CN_Mix3):.2f}") + ") is in the optimum range")    
 
#Water, Dry Mass and Volatile Solids Content of the Substrate Mix (based on FM)
#Methane content of biogas produced from Substrate Mix1
WC_Mix3 = sum(Share3*WC)                             #(%)
DM_Mix3 = sum(Share3*DM)                             #(%)
VS_Mix3 = sum(Share3*DM*VS)                          #(%)
methane_Mix3 = sum(Share3*methane)                   #(%)

#amount of fresh substrate to be fed to the reator per day
Feed_Mix3 = VF*BR/VS_Mix3                            #(kg FM/d)
if Feed_Mix3 < 0.1:
    print ("The amount of substrate to be fed daily is " + (f"{(Feed_Mix3*1000):.2f}") + " g FM.")
else:    
    print ("The amount of substrate to be fed daily is " + (f"{(Feed_Mix3):.2f}") + " kg FM.")

#Need for additional water
#Water content for wet fermentation needs to be 0.88 or higher
add_water_perday = Volume_Flow3*1000 - (Feed_Mix3) #(L/d)
add_water = (Volume_Flow3*1000 - (Feed_Mix3))/Feed_Mix3 #(L/kg FM/d)
if Feed_Mix3 < 0.1:
    print("You have to add " + (f"{(add_water_perday)*1000:.2f}") + " mL water to substrate mix initially.")
elif add_water <= 0 :
    print("No additional water is needed!")
else:
    print ("You have to add " + (f"{(add_water):.2f}") + " kg water per kg substrate mix initially.")

#Volatile Solids Content in the mashed substrate mix    
VS_Mashed_Mix3 = Feed_Mix3*VS_Mix3/(Volume_Flow3*1000) #(%)
WC_Mashed_Mix3 = (add_water_perday+(Feed_Mix3*WC_Mix3))/(add_water_perday+Feed_Mix3) #(%)

#check watercontent 
if WC_Mashed_Mix3 < 0.88:
    print("\u2718 Water content of the mashed substrate is too low. You have to decrease the loading rate per unit volume")
else:
    print("\N{check mark} Water content of the mashed substrate of " + (f"{(WC_Mashed_Mix3*100):.2f}") + " % lies in the optimum range.")

#Water Recovery
#Pressing down to 50% water content
water_recovery_perday = add_water_perday - (Feed_Mix3*DM_Mix3) 
water_recovery = add_water - (0.5-WC_Mix3)
if Feed_Mix3 < 0.1:
    print((f"{(water_recovery_perday*1000):.2f}") + " mL water can be recovered per day.")
else:
    print((f"{(water_recovery):.2f}") + " kg water can be recovered per kg FM used.")
      
#Additional water need
if add_water > water_recovery:
    add_water_need = (add_water - water_recovery) * Feed_Mix3
    if Feed_Mix3 < 0.1:
        print("Each day, an amount of " + (f"{(add_water_need*1000):.2f}") + " g water must be supplied externally.")
    else:
        print("Each day, an amount of " + (f"{(add_water_need):.2f}") + " kg water must be supplied externally.")
else:
    add_water_need = 0
    
#daily Biogas production over HRT per kgVS   
BGP_daily_perkgVS_Mix3 = np.diff(BGP_perkgVS_Mix3)   #L / (kgVS * d)

#Biogas production with regards to Substrate Input
#Total daily production in L / d
BGP_daily_Mix3 = Feed_Mix3 * BGP_daily_perkgVS_Mix3 * VS_Mix3
BGP_Mix3 = Feed_Mix3 * VS_Mix3 * BGP_perkgVS_Mix3

#Methane production with regards to Substrate Input
MP_daily_Mix3 = BGP_daily_Mix3 * methane_Mix3
MP_Mix1_Mix3 = BGP_Mix3 * methane_Mix3

#Production related to the feed of the individual days (i.e. total production from the used substrat mixture)
BGP_daily_fullduration_Mix3 = np.insert(BGP_daily_Mix3,0,[0]*tc2) 
BGP_daily_fullduration_Mix3 = np.append(BGP_daily_fullduration_Mix3,[0]*(tm-tc2-HRT3))

#creating array with production of single feeds of each day 
BGP_dailyfeed_Mix3 = np.zeros([tm,tm])

for i in range(tc3-tc2):
    BGP_dailyfeed_Mix3[:,tc2+i] = shift(BGP_daily_fullduration_Mix3,i, cval=0)
    
#sum of the biogas production at every day 
BGP_sum_Mix3 = sum(np.transpose(BGP_dailyfeed_Mix3))
print("The expected biogas production is "+ (f"{(BGP_sum_Mix3[-1]):.2f}") + " L per day")
print("")

################ Substrate Change ##############################
# Substrate change at a specific time point tc3

### Mix 4 #######################################

#Input Mix 4 - printing a check-up report
print("\nMix 4")
print("")
if sum(Share4) == 1:
    print ("\N{check mark} Input 4 is correct.")
elif sum(Share4) < 1:
    print ("\u2718 Input 4 is too low.")
elif sum(Share4) > 1:
    print("\u2718 Input 4 is too high.")
    
#Check Loading Rate per Unit Volume [BR]  
if BR > 3.5:
    print("\u2718 The Loading Rate per Unit Volume is too high. A longer Hydraulic Retention Time is needed.")
elif BR < 1.5:
    print("\u2718 The Loading Rate per Unit Volume is very low. Consider shorter Hydraulic Retention Time.")
else: 
    print("\N{check mark} The Loading Rate per Unit Volume of " + (f"{(BR):.2f}") + " lies in the optimum range.")

#Carbon to Nitrogen Ratio
CN_Mix4 = sum(C*Share4)/sum(N*Share4)

if CN_Mix4 < 10:
    print("\u2718 C/N - Ratio " + "(" + (f"{(CN_Mix4):.2f}") + ") is too low")
elif CN_Mix3 > 40: 
    print("\u2718 C/N - Ratio " + "(" + (f"{(CN_Mix4):.2f}") + ") is too high")
else:
    print("\N{check mark} C/N - Ratio " + "(" + (f"{(CN_Mix4):.2f}") + ") is in the optimum range")    
 
#Water, Dry Mass and Volatile Solids Content of the Substrate Mix (based on FM)
#Methane content of biogas produced from Substrate Mix1
WC_Mix4 = sum(Share4*WC)                             #(%)
DM_Mix4 = sum(Share4*DM)                             #(%)
VS_Mix4 = sum(Share4*DM*VS)                          #(%)
methane_Mix4 = sum(Share4*methane)                   #(%)

#amount of fresh substrate to be fed to the reator per day
Feed_Mix4 = VF*BR/VS_Mix4                            #(kg FM/d)
if Feed_Mix4 < 0.1:
    print ("The amount of substrate to be fed daily is " + (f"{(Feed_Mix4*1000):.2f}") + " g FM.")
else:    
    print ("The amount of substrate to be fed daily is " + (f"{(Feed_Mix4):.2f}") + " kg FM.")

#Need for additional water
#Water content for wet fermentation needs to be 0.88 or higher
add_water_perday = Volume_Flow4*1000 - (Feed_Mix4) #(L/d)
add_water = (Volume_Flow4*1000 - (Feed_Mix4))/Feed_Mix4 #(L/kg FM/d)
if Feed_Mix4 < 0.1:
    print("You have to add " + (f"{(add_water_perday)*1000:.2f}") + " mL water to substrate mix initially.")
elif add_water <= 0 :
    print("No additional water is needed!")
else:
    print ("You have to add " + (f"{(add_water):.2f}") + " kg water per kg substrate mix initially.")

#Volatile Solids Content in the mashed substrate mix    
VS_Mashed_Mix4 = Feed_Mix4*VS_Mix4/(Volume_Flow4*1000) #(%)
WC_Mashed_Mix4 = (add_water_perday+(Feed_Mix4*WC_Mix4))/(add_water_perday+Feed_Mix4) #(%)

#check watercontent 
if WC_Mashed_Mix4 < 0.88:
    print("\u2718 Water content of the mashed substrate is too low. You have to decrease the loading rate per unit volume")
else:
    print("\N{check mark} Water content of the mashed substrate of " + (f"{(WC_Mashed_Mix4*100):.2f}") + " % lies in the optimum range.")

#Water Recovery
#Pressing down to 50% water content
water_recovery_perday = add_water_perday - (Feed_Mix4*DM_Mix4) 
water_recovery = add_water - (0.5-WC_Mix4)
if Feed_Mix4 < 0.1:
    print((f"{(water_recovery_perday*1000):.2f}") + " mL water can be recovered per day.")
else:
    print((f"{(water_recovery):.2f}") + " kg water can be recovered per kg FM used.")
      
#Additional water need
if add_water > water_recovery:
    add_water_need = (add_water - water_recovery) * Feed_Mix4
    if Feed_Mix4 < 0.1:
        print("Each day, an amount of " + (f"{(add_water_need*1000):.2f}") + " g water must be supplied externally.")
    else:
        print("Each day, an amount of " + (f"{(add_water_need):.2f}") + " kg water must be supplied externally.")
else:
    add_water_need = 0
    
#daily Biogas production over HRT per kgVS   
BGP_daily_perkgVS_Mix4 = np.diff(BGP_perkgVS_Mix4)   #L / (kgVS * d)

#Biogas production with regards to Substrate Input
#Total daily production in L / d
BGP_daily_Mix4 = Feed_Mix4 * BGP_daily_perkgVS_Mix4 * VS_Mix4
BGP_Mix4 = Feed_Mix4 * VS_Mix4 * BGP_perkgVS_Mix4

#Methane production with regards to Substrate Input
MP_daily_Mix4 = BGP_daily_Mix4 * methane_Mix4
MP_Mix1_Mix4 = BGP_Mix4 * methane_Mix4

#Production related to the feed of the individual days (i.e. total production from the used substrat mixture)
BGP_daily_fullduration_Mix4 = np.insert(BGP_daily_Mix4,0,[0]*tc3) 
BGP_daily_fullduration_Mix4 = np.append(BGP_daily_fullduration_Mix4,[0]*(tm-tc3-HRT4))

#creating array with production of single feeds of each day 
BGP_dailyfeed_Mix4 = np.zeros([tm,tm])

for i in range(tm-tc3):
    BGP_dailyfeed_Mix4[:,tc3+i] = shift(BGP_daily_fullduration_Mix4,i, cval=0)
    
#sum of the biogas production at every day 
BGP_sum_Mix4 = sum(np.transpose(BGP_dailyfeed_Mix4))
print("The expected biogas production is "+ (f"{(BGP_sum_Mix4[-1]):.2f}") + " L per day")
print("")


#################################################
### 5. Biogas production of reactor #############
#################################################

#sum of all biogas production mixes 
BGP_dailyfeed_Mix_total=BGP_dailyfeed_Mix1+BGP_dailyfeed_Mix2+BGP_dailyfeed_Mix3++BGP_dailyfeed_Mix4

BGP_total=np.zeros([tm,1])
BGP_total=sum(np.transpose(BGP_dailyfeed_Mix_total))

#################################################
### 6. Saving data ##############################
#################################################

#save data 
datapoints = pd.DataFrame({'day':range(tm),'biogasMix1':BGP_sum_Mix1,'biogasMix2':BGP_sum_Mix2,'biogasMix3':BGP_sum_Mix3,'biogasMix4':BGP_sum_Mix4,'biogastotal':BGP_total})
datapoints.to_csv(r'output/outputdata_conti.csv', index=False, header=True, sep=';')

#Plot data
#Mix1, Mix2, Mix3, Mix4, Mix_total
plt.clf()
plt.plot(range(tm), BGP_sum_Mix1, c="black", lw=0.75, label="Mix 1")
plt.plot(range(tm), BGP_sum_Mix2, c="darkblue", lw=0.75, label="Mix 2")
plt.plot(range(tm), BGP_sum_Mix3, c="blue", lw=0.75, label="Mix 3")
plt.plot(range(tm), BGP_sum_Mix4, c="green", lw=0.75, label="Mix 4")
plt.plot(range(tm), BGP_total, 'r--', lw=0.75, label="Sum")
plt.title("daily biogas production")
plt.xlabel("time (d)")
plt.ylabel("biogas production $(L_N/d)$")
plt.legend(loc="upper left")
plt.savefig('output/daily_biogas_production.png', dpi=300, bbox_inches='tight')
plt.close()
