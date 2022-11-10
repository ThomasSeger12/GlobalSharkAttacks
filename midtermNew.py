# Hello prof!

"""
Thomas Seger
MA346 - Midterm Project
Global Shark Attacks
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import re

df_shark = pd.read_csv('global-shark-attack.csv', index_col=0, lineterminator="\n", delimiter=";")
pd.set_option('display.max_columns', None)

# delete unnecessary columns
df_shark = df_shark.drop(
    ['Name', 'Investigator or Source', 'pdf', 'href formula', 'href', 'Case Number.1', 'Case Number.2',
     'original order\r'], axis=1)
df_shark = df_shark[~df_shark['Date'].isna()]

# Year of Attack
df_shark = df_shark[~df_shark['Year'].isna()]
byYear = df_shark.groupby('Year')['Date'].count().reset_index()
sns.lineplot(data=byYear, x='Year', y='Date').set(title='Shark Attack by Year - All Time', ylabel='Count')
plt.show()
# zoomed in
sns.lineplot(data=byYear.loc[122:, :], x='Year', y='Date').set(title='Shark Attack by Year - 1900 to 2022', ylabel='Count')
print(byYear.loc[122:, :])
plt.show()

# Provoked vs unprovoked over time
yearType = df_shark.groupby(['Year', 'Type'])['Date'].count().reset_index()
yearType = yearType.loc[yearType['Type'].isin(['Provoked', 'Unprovoked'])]
sns.lineplot(data=yearType.loc[272:, :], x='Year', y='Date', hue='Type').set(title='Attack Type by Year', ylabel='Count')
plt.show()

# we now know that unprovoked attacks are significantly higher than provoked ones, so what makes up an unprovoked attack?
# what activities are associated most with unprovoked attacks?
df_shark.loc[(df_shark['Activity'] == 'Wading') |
             (df_shark['Activity'] == 'Bathing') |
             (df_shark['Activity'] == 'Snorkeling') |
             (df_shark['Activity'] == 'Standing') |
             (df_shark['Activity'] == 'Treading water')] = 'Swimming'
df_shark.loc[(df_shark['Activity'] == 'Spearfishing')] = 'Fishing'
df_shark.loc[(df_shark['Activity'] == 'Body boarding') | (df_shark['Activity'] == 'Body surfing') |
             (df_shark['Activity'] == 'Boogie boarding')] = 'Surfing'

byActivity = df_shark['Activity'].value_counts().reset_index().rename(columns={'index': 'Activity', 'Activity': 'Count'})
sns.barplot(data=byActivity.loc[:5], x='Activity', y='Count').set(title='Activities Associated with All Attacks')
plt.show()

unprovokedActivity = df_shark.loc[df_shark['Type'].isin(['Unprovoked'])]
unprovokedActivity = unprovokedActivity['Activity'].value_counts().reset_index().rename(
    columns={'index': 'Activity', 'Activity': 'Count'})
sns.barplot(data=unprovokedActivity.loc[:5], x='Activity', y='Count').set(
    title='Activities Associated with Unprovoked Attacks')
plt.show()

provokedActivity = df_shark.loc[df_shark['Type'].isin(['Provoked'])]
provokedActivity = provokedActivity['Activity'].value_counts().reset_index().rename(
    columns={'index': 'Activity', 'Activity': 'Count'})
sns.barplot(data=provokedActivity.loc[:5], x='Activity', y='Count').set(
    title='Activities Associated with Provoked Attacks')
plt.show()

# Count of attacks over time based on region/country
countryTime = df_shark.groupby(['Year', 'Country'])['Date'].count().reset_index()
# I'm not sure why fishing, swimming, and surfing are in this column, but we want to avoid that
mask = countryTime.Year.isin(['Fishing', 'Swimming', 'Surfing'])
countryTime = countryTime[~mask]

countries = ['USA', 'AUSTRALIA', 'SOUTH AFRICA', 'NEW ZEALAND']
mask = countryTime.Country.isin(countries)
countryTime = countryTime[mask]

sns.lineplot(data=countryTime.loc[222:, :], x='Year', y='Date').set(title='Attacks by Country', ylabel='Count')
plt.show()

# Iterate through list of countries
for i in countries:
    countryTime = df_shark.groupby(['Year', 'Country'])['Date'].count().reset_index()
    mask = countryTime.Year.isin(['Fishing', 'Swimming', 'Surfing'])
    countryTime = countryTime[~mask]

    countryTime = countryTime[countryTime['Country'] == i]
    sns.lineplot(data=countryTime.loc[222:, :], x='Year', y='Date', hue='Country').set(title=f'Attacks in {i}', ylabel='Count')
    plt.show()

countries = ['USA']
mask = countryTime.Country.isin(countries)
countryTime = countryTime[~mask]

sns.lineplot(data=countryTime.loc[222:, :], x='Year', y='Date').set(title='Attacks by Country', ylabel='Count')
plt.show()

# Fatal/non-fatal clean
df_shark['Fatal (Y/N)'] = df_shark['Fatal (Y/N)'].fillna('UNKNOWN')
df_shark['Fatal (Y/N)'] = df_shark['Fatal (Y/N)'].str.strip()
df_shark.loc[df_shark['Fatal (Y/N)'] == 'N', 'Fatal (Y/N)'] = 'NO'
df_shark.loc[df_shark['Fatal (Y/N)'].str.contains('Y|y'), 'Fatal (Y/N)'] = 'YES'
df_shark.loc[~df_shark['Fatal (Y/N)'].str.contains('YES|NO'), 'Fatal (Y/N)'] = 'UNKNOWN'

byFatal = df_shark['Fatal (Y/N)'].value_counts().reset_index().rename(columns={'Fatal (Y/N)': 'Count',
                                                                               'index': 'Fatal?'})
# overall numbers
sns.barplot(data=byFatal, x='Fatal?', y='Count')
plt.show()

# count of attacks over time based on fatal or not
fatalTime = df_shark.groupby(['Year', 'Fatal (Y/N)'])['Date'].count().reset_index()
# I'm not sure why fishing, swimming, and surfing are in this column, but we want to avoid that
mask = fatalTime.Year.isin(['Fishing', 'Swimming', 'Surfing'])
fatalTime = fatalTime[~mask]
sns.lineplot(data=fatalTime.loc[222:, :], x='Year', y='Date', hue='Fatal (Y/N)').set(title='Counts of Fatal and Non-Fatal Attacks', ylabel='Count')
plt.show()

# to show if sharks are getting more aggressive (seeing humans as prey), only fatal
fatalTime = fatalTime[fatalTime['Fatal (Y/N)'] == 'YES']
sns.lineplot(data=fatalTime.loc[222:, :], x='Year', y='Date', hue='Fatal (Y/N)').set(title='Counts of Fatal Attacks', ylabel='Count')
plt.show()

# Species
df_shark.rename(columns={'Species ': 'Species'}, inplace=True)
df_shark['Species'] = df_shark['Species'].fillna('Unknown Shark')
df_shark['New Species'] = None

shark_pattern = r'.* (shark|Shark)'
for row in range(len(df_shark)):
    try:
        shark_species = re.search(shark_pattern, df_shark.iat[row, df_shark.columns.get_loc('Species')]).group()
        df_shark.iat[row, df_shark.columns.get_loc('New Species')] = shark_species
    except:
        df_shark.iat[row, df_shark.columns.get_loc('New Species')] = 'Shark involvement not confirmed'

bySpecies = df_shark['New Species'].value_counts().reset_index().rename(columns={'New Species': 'Count',
                                                                                 'index': 'Species'})
# first 11 could actually mean something -- rest are iffy
plt.pie(data=bySpecies.iloc[2:11, :], x='Count', labels='Species', autopct='%.0f%%')
plt.show()


# unused graphs
# Sex
df_shark = df_shark.rename(columns={'Sex ': 'Sex'})
df_shark['Sex'] = df_shark['Sex'].fillna('Unknown')
df_shark.loc[df_shark['Sex'].str.contains('M|M '), 'Sex'] = 'Male'
df_shark.loc[df_shark['Sex'].str.contains('F'), 'Sex'] = 'Female'
df_shark.loc[~df_shark['Sex'].str.contains('Male|Female'), 'Sex'] = 'Unknown'

bySex = df_shark['Sex'].value_counts().reset_index().rename(columns={'index': 'Gender', 'Sex': 'Count'})

sns.barplot(data=bySex, x="Gender", y='Count')
plt.show()

'''
# Couldn't work it out
# Reported Time
# df_shark['Time'] = df_shark['Time'].str.replace('[0-9]{2}')

time_pattern = r'[0-9]{2}h[0-9]{2}'
morning = r'[0]{1}[5-9]{1}h[0-9]{2}'  # 5:00am-9:59am
midday = r'[1]{1}[0-9]{1}h[0-9]{2}'  # 10:00am-7:59pm
evening = r'[2]{1}[0-4]{1}h[0-9]{2}'  # 8:00pm-11:59pm
late_night = r'[0]{1}[0-4]{1}h[0-9]{2}'  # 12:00am-4:59am

for row in range(len(df_shark)):
    try:
        time = re.search(morning, df_shark.iat[row, df_shark.columns.get_loc('Time')]).group()
        if time:
            df_shark.iat[row, df_shark.columns.get_loc('New Time')] = 'Morning 5:00am-9:59am'

        time = re.search(midday, df_shark.iat[row, df_shark.columns.get_loc('Time')]).group()
        if time:
            df_shark.iat[row, df_shark.columns.get_loc('New Time')] = 'Midday 10:00am-7:59pm'

        time = re.search(evening, df_shark.iat[row, df_shark.columns.get_loc('Time')]).group()
        if time:
            df_shark.iat[row, df_shark.columns.get_loc('New Time')] = 'Evening 8:00pm-11:59pm'

        time = re.search(late_night, df_shark.iat[row, df_shark.columns.get_loc('Time')]).group()
        if time:
            df_shark.iat[row, df_shark.columns.get_loc('New Time')] = 'Late Night 12:00am-4:59am'
    except:
        df_shark.iat[row, df_shark.columns.get_loc('New Time')] = df_shark['Time'].iloc[row]

byTime = df_shark['New Time'].value_counts().reset_index().rename(columns={'New Time': 'Count', 'index': 'Time'})
mask = byTime.Time.isin(['Fishing', 'Swimming', 'Surfing'])
byTime = byTime[~mask]
plt.pie(data=byTime.iloc[1:5, :], x='Count', labels='Time', autopct='%.0f%%')
plt.show()
'''
