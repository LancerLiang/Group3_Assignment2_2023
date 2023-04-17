import pandas as pd
import datetime


dataset_dynamic = pd.read_csv('sph_dynamic.csv')
dataset_static = pd.read_csv('sph_static.csv')


#handling duplicates
dataset_dynamic_g=dataset_dynamic.groupby(['stay_id', 'charttime']).median()
dataset_dynamic_g.reset_index(inplace=True)

#merge based on unique stay_id
dataset=dataset_dynamic_g.merge(dataset_static, how='left', on='stay_id')

dataset_sort=dataset.sort_values(['stay_id','charttime'],ascending=[True,True])

#remove features with a missing rate over 95%
counts=dataset_sort.isna().sum()/len(dataset_sort)
clst=counts.index[counts.values>0.95].tolist()



dataset_sort['Date']= pd.to_datetime(dataset_sort['charttime']).dt.strftime('%y-%m-%d %H:%M:%S')
dataset_sort['icu_in']= pd.to_datetime(dataset_sort['icu_intime']).dt.strftime('%y-%m-%d %H:%M:%S')
dataset_sort['start']= pd.to_datetime(dataset_sort['vent_start'],format='%m/%d/%y %H:%M').dt.strftime('%y-%m-%d %H:%M:%S')
dataset_sort['end']= pd.to_datetime(dataset_sort['vent_end'],format='%m/%d/%y %H:%M').dt.strftime('%y-%m-%d %H:%M:%S')
   

records_count_by_stayid=dataset_sort.groupby(['stay_id']).count()
records_count_by_stayid['records_num']=records_count_by_stayid['charttime']
records_count_by_stayid=records_count_by_stayid[['records_num']]

#dataset_sort=dataset_sort.merge(records_count_by_stayid, how='left', on='stay_id')


dataset_sort=dataset_sort.drop(columns=clst)

dataset_sort.isna().sum()/len(dataset_sort)

dataset_stayid=dataset_static[['stay_id', 'vent_duration']]

#outcome classification
for i in range(len(dataset_stayid)):
    timev=dataset_stayid.loc[i,'vent_duration']
    if timev<6:
        dataset_stayid.loc[i,'outcome_6hours']='<6hrs'
    elif timev<12 and timev>=6:
        dataset_stayid.loc[i,'outcome_6hours']='6-12hrs'
    elif timev<18 and timev>=12:
        dataset_stayid.loc[i,'outcome_6hours']='12-18hrs'
    elif timev<24 and timev>=18:
        dataset_stayid.loc[i,'outcome_6hours']='18-24hrs'
    else:
        dataset_stayid.loc[i,'outcome_6hours']='>24hrs'

for i in range(len(dataset_stayid)):
    timev=dataset_stayid.loc[i,'vent_duration']
    if timev<12:
        dataset_stayid.loc[i,'outcome_12hours']='<12hrs'
    elif timev<24 and timev>=12:
        dataset_stayid.loc[i,'outcome_12hours']='12-24hrs'
    else:
        dataset_stayid.loc[i,'outcome_12hours']='>24hrs'

for i in range(len(dataset_stayid)):
    timev=dataset_stayid.loc[i,'vent_duration']
    if timev<24:
        dataset_stayid.loc[i,'outcome_days']='1days'
    elif timev<48 and timev>=24:
        dataset_stayid.loc[i,'outcome_days']='2days'
    else:
        dataset_stayid.loc[i,'outcome_days']='>2days'
        



dict1={'calcium':'calcium+24',
 'creatinine':'creatinine+24',
 'glucose': 'glucose+24',
 'sodium':'sodium+24',
 'chloride':'chloride+24',
 'hemoglobin':'hemoglobin+24',
 'wbc':'wbc+24',
 'alt':'alt+24',
 'ast':'ast+24',
 'alp':'alp+24',
 'bilirubin_total':'bilirubin_total+24',
 'pt':'pt+24'}

dict2={'calcium':'calcium-24',
 'creatinine':'creatinine-24',
 'glucose': 'glucose-24',
 'sodium':'sodium-24',
 'chloride':'chloride-24',
 'hemoglobin':'hemoglobin-24',
 'wbc':'wbc-24',
 'alt':'alt-24',
 'ast':'ast-24',
 'alp':'alp-24',
 'bilirubin_total':'bilirubin_total-24',
 'pt':'pt-24'}

dict3={'calcium':'calcium-48',
 'creatinine':'creatinine-48',
 'glucose': 'glucose-48',
 'sodium':'sodium-48',
 'chloride':'chloride-48',
 'hemoglobin':'hemoglobin-48',
 'wbc':'wbc-48',
 'alt':'alt-48',
 'ast':'ast-48',
 'alp':'alp-48',
 'bilirubin_total':'bilirubin_total-48',
 'pt':'pt-48'}

dataset_icuin=dataset_sort.copy()
dataset_intubation=dataset_sort.copy()





"""preprocessing1: based on icu_in time"""
"""1923 unique stay_id"""
for i in range(len(dataset_icuin)):
    dataset_icuin.loc[i,'time_to_icuin']=(datetime.datetime.strptime(dataset_icuin.loc[i,'Date'], '%y-%m-%d %H:%M:%S')-datetime.datetime.strptime(dataset_icuin.loc[i,'icu_in'], '%y-%m-%d %H:%M:%S')).total_seconds()/3600


for i in range(len(dataset_icuin)):
    timei=dataset_icuin.loc[i,'time_to_icuin']
    if timei<24 and timei>=0:
        dataset_icuin.loc[i,'timeframe']=24
    elif timei<0 and timei>=-24:
       dataset_icuin.loc[i,'timeframe']=-24
    elif timei<-24 and timei>=-48:
       dataset_icuin.loc[i,'timeframe']=-48
    else:
       dataset_icuin.loc[i,'timeframe']=1000


dataset_icuin=dataset_icuin[dataset_icuin['timeframe']!=1000]
dataset_icuin=dataset_icuin.groupby(['stay_id', 'timeframe']).mean()
dataset_icuin.reset_index(inplace=True)
dataset_icuin=dataset_icuin.drop(columns=['time_to_icuin','vent_duration'])
dataset_icuinplus24=dataset_icuin[dataset_icuin['timeframe']==24].drop(columns=['timeframe'])
dataset_icuinminus24=dataset_icuin[dataset_icuin['timeframe']==-24].drop(columns=['timeframe'])
dataset_icuinminus48=dataset_icuin[dataset_icuin['timeframe']==-48].drop(columns=['timeframe'])

dataset_icuinplus24.rename(columns=dict1,inplace=True)
dataset_icuinminus24.rename(columns=dict2,inplace=True)
dataset_icuinminus48.rename(columns=dict3,inplace=True)

dataset_icuin_final=dataset_stayid.copy()

dataset_icuin_final=dataset_icuin_final.merge(dataset_icuinminus48, how='left', on='stay_id')
dataset_icuin_final=dataset_icuin_final.merge(dataset_icuinminus24, how='left', on='stay_id')
dataset_icuin_final=dataset_icuin_final.merge(dataset_icuinplus24, how='left', on='stay_id')
dataset_icuin_final=dataset_icuin_final.merge(records_count_by_stayid, how='left', on='stay_id')

dataset_icuin=dataset_icuin.merge(dataset_stayid, how='left', on='stay_id')
dataset_icuin=dataset_icuin.merge(records_count_by_stayid, how='left', on='stay_id')

with pd.ExcelWriter('dataset_icuin.xlsx') as writer:  
    dataset_icuin_final.to_excel(writer, sheet_name='icu_in')
    dataset_icuin.to_excel(writer, sheet_name='icu_in_with_timeframe')
    
"""preprocessing2: based on intubation start time"""

for i in range(len(dataset_intubation)):
    dataset_intubation.loc[i,'time_to_intubation']=(datetime.datetime.strptime(dataset_intubation.loc[i,'Date'], '%y-%m-%d %H:%M:%S')-datetime.datetime.strptime(dataset_intubation.loc[i,'start'], '%y-%m-%d %H:%M:%S')).total_seconds()/3600

for i in range(len(dataset_intubation)):
    timei=dataset_intubation.loc[i,'time_to_intubation']
    if timei<0 and timei>=-24:
       dataset_intubation.loc[i,'timeframe']=-24
    elif timei<-24 and timei>=-48:
       dataset_intubation.loc[i,'timeframe']=-48
    else:
       dataset_intubation.loc[i,'timeframe']=1000 
dataset_intubation=dataset_intubation[dataset_intubation['timeframe']!=1000]
dataset_intubation=dataset_intubation.groupby(['stay_id', 'timeframe']).mean()

dataset_intubation.reset_index(inplace=True)
dataset_intubation=dataset_intubation.drop(columns=['time_to_intubation','vent_duration'])
dataset_intubationminus24=dataset_intubation[dataset_intubation['timeframe']==-24].drop(columns=['timeframe'])
dataset_intubationminus48=dataset_intubation[dataset_intubation['timeframe']==-48].drop(columns=['timeframe'])


dataset_intubationminus24.rename(columns=dict2,inplace=True)
dataset_intubationminus48.rename(columns=dict3,inplace=True)

dataset_intubation_final=dataset_stayid.copy()

dataset_intubation_final=dataset_intubation_final.merge(dataset_intubationminus48, how='left', on='stay_id')
dataset_intubation_final=dataset_intubation_final.merge(dataset_intubationminus24, how='left', on='stay_id')
dataset_intubation_final=dataset_intubation_final.merge(records_count_by_stayid, how='left', on='stay_id')

dataset_intubation=dataset_intubation.merge(dataset_stayid, how='left', on='stay_id')
dataset_intubation=dataset_intubation.merge(records_count_by_stayid, how='left', on='stay_id')
with pd.ExcelWriter('dataset_intubation.xlsx') as writer:  
    dataset_intubation_final.to_excel(writer, sheet_name='intubation')
    dataset_intubation.to_excel(writer, sheet_name='intubation_with_timeframe')

