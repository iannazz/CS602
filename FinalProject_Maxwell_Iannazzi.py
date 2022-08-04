"""
Name: Maxwell Iannazzi
Due 8/4/2022
Final Project
California Wildfires Dataset

"""

import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px


FILENAME = "California_Fire_Incidents.csv"

df = pd.read_csv(FILENAME)
df = pd.DataFrame(df)
#Function that contains two parameters. Will be called twice. Once called to show how many fires have occurred larger than Waltham. Waltham is 8960 acres in size.
#Second time as a user input interacting with Streamlit number input.

st.title("California Wildfires")
def filteracres(df, acreage):
    return(len(df[df['AcresBurned']>=acreage]))

st.write("California experienced ",filteracres(df, 8960), "wildfires between 2013-2019 that were larger than the size of Waltham.")
st.header("Interactive Structure Info")
acreage_search = st.number_input('Pick a number', 0, 410203)
st.write("Number Input:",acreage_search)

st.write("There have been ", filteracres(df, acreage_search), "wildfires of at least", acreage_search, "acres burned in California between 2013-2019.")

#function that has default value incorporated

def filterstructures(df, structures = 1):
    return(len(df[df['StructuresDestroyed']>=structures]))

tendestroyed = 10
st.write("There have been ", filterstructures(df, tendestroyed), "wildfires that destroyed at least ten structures.")
st.write("There have been ", filterstructures(df), "wildfires that destroyed 1 or more structures.")

#Sorting data by one or more columns. Sorting data by structures destroyed.
st.header("The below data shows the top 20 wildfires in California between 2013-2019 in terms of structures destroyed.")

df = df.sort_values('StructuresDestroyed', ascending=False)
st.write(df[['AcresBurned','StructuresDestroyed']].head(20))


#Filtering by one condition
st.header("The top 10 fires of Los Angeles County from 2013-2019")
def county_filter(county, df):
    df = df.sort_values('AcresBurned', ascending=False)
    result = df[df['Counties'] == county].head(10)
    return result[['Counties', 'AcresBurned']]

st.write(county_filter("Los Angeles", df))

#Filtering by two conditions.
st.header("Showing all fires that occurred in Los Angeles in both 2013 and 2019.")


def county_year_filter(county, year, df):
    df = df.sort_values('AcresBurned', ascending=False)
    result = df[(df['Counties'] == county) & (df['ArchiveYear'] == year)]
    result = result.head(10)
    return result[['Counties', 'ArchiveYear', 'AcresBurned']]


first_county_year = st.write(county_year_filter("Los Angeles", 2013, df))

second_county_year = st.write(county_year_filter("Los Angeles", 2019, df))

#Pivot Table
st.header("The Below Pivot Table shows how many structures per year have been destroyed in each California County.")

PivotTable = pd.pivot_table(df, values='StructuresDestroyed', index=['Counties'], columns=['ArchiveYear'], aggfunc=np.sum, fill_value=0)

st.write(PivotTable)

#Dictionary Interaction for Later
def dictionaryinteraction(FILENAME):

    with open(FILENAME, encoding="utf8") as csv_file:
        data = csv.DictReader(csv_file)
        dict = {}
        for row in data:
            UniqueId = row['UniqueId']
            BurnedAcres = row['AcresBurned']
            Year = row['ArchiveYear']
            if Year not in dict.keys():
                dict[Year]= {UniqueId:BurnedAcres}
            else:
                dict[Year].update({UniqueId:BurnedAcres})
    return dict


(dictionaryinteraction("California_Fire_Incidents.csv"))

#Line Chart & Also use of Group-by Function
st.header("Total Acres Burned in California 2013-2019")

def line_chart(df):

    yearlist = []
    acreageburned = []
    acreageburning = []
    burnedbyyear= df.groupby(['ArchiveYear'])
    for group in burnedbyyear.groups:
        yearlist.append(group)
    acreageburns = burnedbyyear['AcresBurned'].agg([np.sum]).values.tolist()
    for x in acreageburns:
        acreageburning.append((str(x)))
    for x in acreageburning:
        x = x.replace("[", "")
        x = x.replace("]", "")
        acreageburned.append(float(x))

    date = yearlist
    plt.plot(date, acreageburned, label="Acres Burned per year")
    plt.xlabel("Year")
    plt.ylabel("Acres Burned")
    plt.legend(loc="best")
    plt.xticks(rotation=45)
    plt.title("Acres Burned Per Year")

st.pyplot(line_chart(df))




#Chart #2. Bar Chart for total acres burned by county. Also use of GroupBy function and a list.
st.header("Total Acres Burned By County")
def BarChart(df):

    countylist = []
    acreageburned = []
    acreageburning = []
    burnedbycounty= df.groupby(['Counties'])
    for group in burnedbycounty.groups:
        countylist.append(group)
    acreageburns = burnedbycounty['AcresBurned'].agg([np.sum]).values.tolist()
    for x in acreageburns:
        acreageburning.append((str(x)))
    for x in acreageburning:
        x = x.replace("[", "")
        x = x.replace("]", "")
        acreageburned.append(float(x))
    plt.bar(countylist[:5], acreageburned[:5])
    plt.title("Acres Burned By County")
    return plt



st.pyplot(BarChart(df))



#Map Plot of the Five Biggest Fires
topfive = [(410203, 39.243283, -123.103367),
        (281893, 34.41521, -119.09124),
        (257314, 37.857, -120.086),
        (229651, 40.65428, -122.62357),
        (153336, 39.8134, -121.4347)]

dmap = pd.DataFrame(topfive, columns=["Acres Burned", "lat", "lon"])
st.map(dmap)
st.header("Map of California Wildfires")
view_state = pdk.ViewState(
    latitude=dmap["lat"],
    longitude=dmap["lon"],
    zoom=8,
    pitch=0)

layer1 = pdk.Layer('ScatterplotLayer',
                  data=dmap,
                  get_position='[lon, lat]',
                  get_radius=500,
                  get_color=[0,0,255],   # big red circle
                  pickable=True
                  )

layer2 = pdk.Layer('ScatterplotLayer',
                  data=dmap,
                  get_position='[lon, lat]',
                  get_radius=100,
                  get_color=[255,0,255],   #purple circle
                  pickable=True
                  )
tool_tip = {"html": "Acres Burned Name:<br/> <b>{Acres Burned}</b> ",
            "style": { "backgroundColor": "steelblue",
                        "color": "white"}
          }
map = pdk.Deck(
    map_style='mapbox://styles/mapbox/outdoors-v11',
    initial_view_state=view_state,
    layers=[layer1, layer2],
    tooltip= tool_tip
)

#st.pydeck_chart(map)

#Streamlit functions: sliders and selectbox for searching the data


st.header("Using more interactive tools to learn more about the wildfire data.")


st.write("Please use the slider to see how many fires have occurred within a certain range.")
acresdestroyed = st.slider('Pick a range', 0, 410203)

st.write("Acres Destroyed:", acresdestroyed)
st.write("There have been ", len(df[df['AcresBurned']<=acresdestroyed]), "of", acresdestroyed, "acres burned in California between 2013-2019.")

st.write("Use the Selectbox to pick a year and then display a dictionary of each unique fire. Then hit the arrow to collapse the dictionary.")
burnyear = st.selectbox('Pick a year', ['2013', '2014', '2015', '2016', '2017', '2018', '2019'])
st.write("Year:", burnyear)
if burnyear == '2013':
    st.write(dictionaryinteraction("California_Fire_Incidents.csv")['2013'])
elif burnyear == '2014':
    st.write(dictionaryinteraction("California_Fire_Incidents.csv")['2014'])
elif burnyear == '2015':
    st.write(dictionaryinteraction("California_Fire_Incidents.csv")['2015'])
elif burnyear == '2016':
    st.write(dictionaryinteraction("California_Fire_Incidents.csv")['2016'])
elif burnyear == '2017':
    st.write(dictionaryinteraction("California_Fire_Incidents.csv")['2017'])
elif burnyear == '2018':
    st.write(dictionaryinteraction("California_Fire_Incidents.csv")['2018'])
elif burnyear == '2019':
    st.write(dictionaryinteraction("California_Fire_Incidents.csv")['2019'])

st.write("Click the box to order the list by fires with more than one fatality.")
fatalitiescheck = st.checkbox('Multiple Fatalities?')
st.write("Fatalities?", fatalitiescheck)

if fatalitiescheck:
    df = df.sort_values('Fatalities', ascending=False)
    st.write(df[['AcresBurned','Fatalities']].head(20))
else:
    df = df.sort_values('Fatalities', ascending=True)
    st.write(df[['AcresBurned','Fatalities']].head(20))


# Module from outside of Class: Plotly Heatmaps:
# For Heatmap data, used the five biggest counties in California
st.header("The Five Largest Counties in California")

fivedata=[[31503, 2416, 1289, 11488, 31190,102232,14462],
          [13771, 26315, 2373, 9115, 10156, 2205, 1459],
          [40, 968, 214, 197, 11879, 23466, 0],
          [53919, 630, 1928, 1822, 16576, 15615, 6872],
          [1850, 2191, 35883, 44454, 4065, 1820, 634]
]




fig = px.imshow(fivedata,
                labels=dict(x="Year", y="County", color="Total Fire"),
                x=['2013', '2014', '2015', '2016', '2017', '2018', '2019'],
                y=['Los Angeles', 'San Diego', 'Orange', 'Riverside', 'San Bernardino']
                )
fig.update_xaxes(side="top")
st.write(fig)


"References: outside of class materials I used Plotly Express at the following link:"
"https://plotly.com/python/heatmaps/"

