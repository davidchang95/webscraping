#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  2 23:29:59 2020

@author: davidchang
"""

import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import ast

data = pd.read_csv('fb_jobs_with_years.csv')

#%%

"""
create scatter plot/dot density plot over map

-get all the locations into one list; currently have a list of lists
-in csv is stored as list of list (list of office locations for each job)
-use ast.literal_eval to convert list stored as string in csv to a list object
-manually get lat/long for distinct office locations and store in city_lat_long.csv
-for each distinct location, count total in all_locs[]
"""
#getting the data

all_locs = []
locs = data['location']

for loc in locs:
    all_locs.extend(ast.literal_eval(loc))    

distinct_locs = list(dict.fromkeys(all_locs)) #use this to manually find lat and long

unique_locs = pd.read_csv('/Users/davidchang/Desktop/city_lat_long.csv')
unique_locs['count'] = 0

def count (city):
    return all_locs.count(city)

#for each unique city, get count of it in list of all job city availabities
unique_locs['count'] = unique_locs['City'].apply(count)
#%%
#making the actual map

map = Basemap()
#map.shadedrelief()
map.drawcoastlines(color='gray')
map.drawcountries(color='gray')
map.drawstates(color='gray')
map.scatter(unique_locs['Lon'],unique_locs['Lat'],sizes=unique_locs['count'],color='Red', alpha=0.5)

plt.show()

del locs, distinct_locs

#%%

"""
-create pie chart of distribution of jobs across departments

-get all list of all teams same way as locations (csv stored as list of lists)
-use ast.literal_eval to convert list stored as string in csv to a list object
-only look at teams hiring at least 70 positions otherwise pie chart as too many slices
-got rid of fb reality labs and oculus because overlap with AR/VR

"""

#pulling the data
all_teams = []
teams = data['team']

for team in teams: 
    all_teams.extend(ast.literal_eval(team))
    
unique_teams = list(dict.fromkeys(all_teams))
teams_df = pd.DataFrame(unique_teams, columns=['team'])

teams_df['count'] = 0

def count (team):
    return all_teams.count(team)

teams_df['count'] = teams_df['team'].apply(count)

#clean up
pie_df = teams_df.loc[teams_df['count'] > 70] #convert to dataframe including ones with at least 70
pie_df = pie_df.loc[pie_df['team'] != 'Facebook Reality Labs'] #this is basically ar/vr
pie_df = pie_df.loc[pie_df['team'] != 'Oculus']                #so is this
#If I want to include the misc that are < 70
#dfpie = dfpie.append(pd.DataFrame([['Other',390]],columns=['team','count']))
pie_df = pie_df.sort_values(by=['count'], ascending = False)

#%%
#make the actual chart
fig1, ax1 = plt.subplots()

labels = pie_df['team']
sizes = pie_df['count']
ax1.pie(sizes, labels=labels, autopct='%1.f%%', shadow=True, startangle=75)
ax1.axis('equal')
ax1.set(title = 'Job Distribution')
plt.show()

del team, teams, unique_teams

#%%
"""
Create nested pie chart of each team broken down by experience level

defined 1-3 years exp as entry level
        4-7 years exp as mid level
        >=8 years exp as senior level
        if no explicit years of exp then assume mid level
"""

#getting data
data['level'] = 0

data.loc[data['years_exp']==0,'level'] = 'mid'
data.loc[(data['years_exp']>=1) & (data['years_exp'] <4),'level'] = 'entry'
data.loc[(data['years_exp']>=4) & (data['years_exp'] <8),'level'] = 'mid'
data.loc[(data['years_exp']>=8) & (data['years_exp'] <99),'level'] = 'senior'

#dataframe with each row is list of teams and experience level for each job
team_levels = pd.DataFrame(data[['team','level']])
#break out the list of teams for each job so each team is in its own row and assign level
level_list = pd.DataFrame(columns=['team','level'])
for index, row in team_levels.iterrows():
    temp = pd.DataFrame(ast.literal_eval(row['team']), columns=['team'])
    temp['level'] = row['level']
    level_list = level_list.append(temp)

#get unique teams to get count of each exp level of
unique_teams = list(dict.fromkeys(level_list['team']))

#teams_df dataframe will hold final data of count for each team
#intialized with column of unique teams
teams_df = pd.DataFrame(unique_teams, columns=['team'])

#for each unique team, get sum of entry, mid, and senior jobs from level_list to aggregate levels
agg_levels = []
for team in unique_teams: 
    entry = level_list.loc[level_list['level'] == 'entry','team'].tolist().count(team)
    mid = level_list.loc[level_list['level'] == 'mid','team'].tolist().count(team)
    senior = level_list.loc[level_list['level'] == 'senior','team'].tolist().count(team)
    agg_levels.append([entry,mid,senior])

#first store in each individual column to easily sum up total
pie2_df = pd.DataFrame(agg_levels, columns=['entry','mid','senior']) 
pie2_df['team'] = pd.DataFrame(unique_teams)
#also store entry, mid, senior as a list, easier for the plotting
pie2_df['list'] = agg_levels

#clean up
pie2_df['total'] = pie2_df['entry']+pie2_df['mid']+pie2_df['senior']
#get rid of teams with less than 70 job openings
pie2_df = pie2_df.loc[pie2_df['total'] > 70]
pie2_df = pie2_df.sort_values(by=['total'],ascending = False)
#get rid of these are probably overlap of AR/VR
pie2_df = pie2_df.loc[~pie2_df['team'].isin(['Oculus','Facebook Reality Labs'])]

#%%
#plotting chart
fig, ax = plt.subplots()

vals = np.array(pie2_df['list'].tolist())
cmap = plt.get_cmap("tab20c")
outer_colors = cmap(np.arange(3)*4)
inner_colors = ['Yellow','Orange','Red']

#outer pie
ax.pie(vals.sum(axis=1), radius=1, labels = pie2_df['team'], startangle=70,
       wedgeprops=dict(width=0.2, edgecolor='w'))

#inner pie
wedge, text = ax.pie(vals.flatten(), radius=1-0.2, colors=inner_colors, startangle=70,
       wedgeprops=dict(width=.3, edgecolor='w'))

ax.set(aspect="equal", title='Job Distribution')

#legend
ax.legend([wedge[0], wedge[1],wedge[2]],['Entry level','Mid level','Senior level'], 
          title='Tenure', loc = (-0.3,0.8))

plt.show()

#%%
"""
Bar chart for frequency of each years of experience 

"""

#get data
#remove jobs where years_exp == 0 (did not find "X+ years of experience" stored as 0)
years_list = data.loc[data['years_exp'] != 0,'years_exp'].tolist()
unique_years = pd.DataFrame(list(dict.fromkeys(data['years_exp'])),columns=['years_exp'])

unique_years['count'] = 0

def count (year):
    return years_list.count(year) 

#get count of jobs for each unique years of exp
unique_years['count'] = unique_years['years_exp'].apply(count)
years_df = pd.DataFrame(unique_years)
years_df = years_df.sort_values(by=['years_exp'])

#%%

#plot chart
fig, ax = plt.subplots()

objects = years_df['years_exp']#.tolist()
y_pos = np.arange(len(objects))
performance = years_df['count'].tolist()

plt.bar(y_pos, performance, align='center')
plt.xticks(y_pos, objects)
plt.ylabel('Number of Positions')
plt.xlabel('Years of Experience')
plt.title('Experience Level of Jobs')

for i, v in enumerate(performance):
    plt.text(y_pos[i] - 0.2, v + 4, str(v))

plt.show()


