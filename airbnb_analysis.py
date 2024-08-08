#Importing Libraries
import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
from PIL import Image
import mysql.connector

#Page Configuration Setup
icon=Image.open(r'airbnb_logo.jpg')
st.set_page_config(
                page_title="Airbnb",
                page_icon=icon,
                layout="wide",
                initial_sidebar_state="expanded")

#Title and Introduction 
st.image("airbnb_logo.jpg", width=350, use_column_width=False)
st.title("Airbnb Data Analysis : User friendly Dashboard")

#Creating option menu in Home page
selected=option_menu(
    "Airbnb Data Visualization | Analyze Data",
    ["Home", "Overview", "Explore Insights"],
    icons=["house", "graph-up-arrow", "bar-chart-line"],
    menu_icon="globe",
    default_index=0,
    orientation="horizontal",
    styles={"nav-link": {"font-size":"20px", "text-align":"left", "margin":"-2px", "--hover-color":"FF5A5F"},
            "nav-link-selected":{"background-color":"FF5A5F"}})

#Home Page
if selected == "Home":
    #Column layout
    col1,col2=st.columns([2,1], gap="medium")
    with col1:
        st.markdown("### :red[Domain]: Travel Industry, Property Management and Tourism")
        st.markdown("### :red[Technologies Used]: Python, Pandas, Plotly, Streamlit")
        st.markdown(""" ### :red[Overview]: ##
                    \n- Processed an airbnb 2019 JSON dataset using Python for structured Dataframe transformation, \n- Applied Pre-processing techniques, including thorough data cleaning for accuracy and reliability, \n- Analyzed airbnb data for Pricing, Availability and Location trends, \n- Developed Interactive Visualizations and Dynamic plots to provide valuable insights for hosts and guests"""
                   )
    with col2:
        st.image("https://media.gq.com/photos/616f02741269f766981e8bd9/4:3/w_844,h_633,c_limit/airbnb-cabins.gif",
        width=600,
        caption="Explore the insights in Airbnb data",
        use_column_width=True)
    st.markdown("---")
    
#SQL connection
mydb=mysql.connector.connect(host="localhost", user="root", password="Abisheg@7103", database="airbnb")
print(mydb)
mycursor=mydb.cursor()

if selected == "Overview":
    col1, col2=st.columns(2)
    df=pd.read_csv("Airbnb_data.csv")
    with col1:
        country_options=['Select All']+sorted(df['Country'].unique())
        property_options=['Select All']+sorted(df['Property_Type'].unique())
        room_options=['Select All']+sorted(df['Room_Type'].unique())
        
        country=st.sidebar.multiselect('Select Country', country_options, default=['Select All'])
        property=st.sidebar.multiselect('Select Property Type', property_options, default=['Select All'])
        room=st.sidebar.multiselect('Select Room Type', room_options, default=['Select All'])
        
        if 'Select All' in country:
            country=sorted(df['Country'].unique())
        if 'Select All' in property:
            property=sorted(df['Property_Type'].unique())
        if 'Select All' in room:
            room=sorted(df['Room_Type'].unique())
        
        price=st.slider('Select Price', df['Price'].min(), df['Price'].max(), (df['Price'].min(), df['Price'].max()))
        query=f"Country in {country} & Room_Type in {room} & Property_Type in {property} & Price >= {price[0]} & Price <= {price[1]}"
    
    col1, col2=st.columns(2, gap='medium')
    col3=st.columns(1)[0]
    col4=st.columns(1)[0]
    
    with col1:
        df1 = df.query(query).groupby(['Property_Type']).size().reset_index(name='Listings').sort_values(by='Listings', ascending=False)[:10]
        fig=px.bar(df1, title='1. Top 10 Properties', x='Listings', y='Property_Type', orientation='h', color='Property_Type', color_continuous_scale=px.colors.sequential.Agsunset)  
        st.plotly_chart(fig, use_container_width=True)      
        
        df2=df.query(query).groupby(['Host_Name']).size().reset_index(name='Listings').sort_values(by='Listings', ascending=False)[:10]
        fig=px.bar(df2, title='3. Top 10 Hosts with highest number of Listings', x='Listings', y='Host_Name', orientation='h', color='Host_Name', color_continuous_scale=px.colors.sequential.Agsunset)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)   

    with col2:
        df1=df.query(query).groupby(['Room_Type']).size().reset_index(name='counts')
        fig=px.pie(df1, title='2. Total Listings in each Room types', names='Room_Type', values='counts', color_discrete_sequence=px.colors.sequential.Rainbow)
        fig.update_traces(textposition='outside', textinfo='value+label')
        st.plotly_chart(fig, use_container_width=True) 

        df2 = df.query(query).groupby(['Room_Type']).agg({'Price': 'mean', 'Name': 'count'}).reset_index()
        df2.columns=['Room_Type', 'Average_Price', 'Accomodation_Count']
        fig=px.bar(df2, x='Room_Type', y='Average_Price', color='Average_Price', title='4. Room type wise accomodation count and Average price', color_continuous_scale=px.colors.sequential.Viridis)
        fig.update_traces(marker_line_width=1, marker_line_color='DarkSlateGrey')
        st.plotly_chart(fig, use_container_width=True) 

    with col3:
        df1=df.query(query).groupby(['Property_Type']).agg({'Price':'mean','Name':'count'}).reset_index()
        df1.columns=['Property_Type', 'Average_Price', 'Accomodation_Count']
        fig=px.bar(df1, x='Property_Type', y=['Accomodation_Count', 'Average_Price'], color='Average_Price', title='5. Property type wise accomodation count and Average price', barmode='group', color_continuous_scale=px.colors.sequential.Agsunset)
        st.plotly_chart(fig, use_container_width=True)

        df3=df.query(query).groupby(['Property_Type', 'Room_Type']).agg({'Availability_365':'mean'}).reset_index()
        df3.columns=['Property_Type', 'Room_Type', 'Average_availability_days']
        fig=px.bar(df3, x='Average_availability_days', y='Property_Type', orientation='h', color='Room_Type', title='6. Average availability days for specific property and country', color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig, use_container_width=True) 

    with col4:
        country_df=df.query(query).groupby(['Country'], as_index=False)['Name'].count().rename(columns={'Name':'Total_Listings'})
        fig=px.choropleth(country_df, locations='Country', locationmode='country names', color="Total_Listings", title="7. Total Listings in each Country", color_continuous_scale=px.colors.sequential.Plasma)
        fig.update_layout(mapbox_style="stamen-terrain")
        st.plotly_chart(fig, use_container_width=True) 


if selected=="Explore Insights":
    st.markdown('### Explore more about the Airbnb data')
    df=pd.read_csv(r"Airbnb_data.csv")
    
    Country_options=['Select All']+sorted(df['Country'].unique())
    prop_options=['Select All']+sorted(df['Property_Type'].unique())
    room_options=['Select All']+sorted(df['Room_Type'].unique())

    Country=st.sidebar.multiselect('Select Country', Country_options, default=['Select All'])
    prop=st.sidebar.multiselect('Select Property Type', prop_options, default=['Select All'])
    room=st.sidebar.multiselect('Select Room Type', room_options, default=['Select All'])

    if 'Select All' in Country:
        Country=sorted(df['Country'].unique())
    if 'Select All' in prop:
        prop=sorted(df['Property_Type'].unique())
    if 'Select All' in room:
        room=sorted(df['Room_Type'].unique())

    price=st.slider('Select Price', df['Price'].min(), df['Price'].max(), (df['Price'].min(), df['Price'].max()))
    
    query=f"Country in {Country} & Room_Type in {room} & Property_Type in {prop} & Price >= {price[0]} & Price <= {price[1]}"

    col1, col2=st.columns(2)
    with col1:
        st.markdown("### Price analysis")
        price_df=df.query(query).groupby('Room_Type',as_index=False)['Price'].mean().sort_values(by='Price')
        price_df['Price']=price_df['Price'].round(2)
        fig=px.bar(price_df, x='Room_Type', y='Price', color='Price', title='Average Price in each type')
        st.plotly_chart(fig, use_container_width=True)

        Country_df=df.query(query).groupby('Country',as_index=False)['Price'].mean()
        Country_df['Price']=Country_df['Price'].round(2)
        fig=px.scatter_geo(Country_df, locations='Country', color='Price', hover_data=['Price'], locationmode='country names', size='Price', title='Average Price in each country', color_continuous_scale='agsunset')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#   ")
        st.markdown("#   ")

    with col2:
        st.markdown("### Availability Analysis")
        filtered_df=df.query(query)
        filtered_df=filtered_df.rename(columns={"Availability_365":"Availability"})
        fig=px.box(filtered_df, x='Room_Type', y='Availability', color='Room_Type', title='Availability by Room type')
        st.plotly_chart(fig, use_container_width=True)

        Country_df=df.query(query).groupby('Country',as_index=False)['Availability_365'].mean()
        Country_df=Country_df.rename(columns={"Availability_365":"Availability"})
        Country_df['Availability']=Country_df['Availability'].astype(int)
        fig=px.scatter_geo(Country_df, locations='Country', color='Availability', hover_data=['Availability'], locationmode='country names', size='Availability', title='Average Availabilty in each country', color_continuous_scale='agsunset')
        st.plotly_chart(fig, use_container_width=True)
