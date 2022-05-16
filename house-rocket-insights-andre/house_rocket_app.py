import pandas as pd
import streamlit as st
import plotly.express as px


# FUNCTIONS
@st.cache(allow_output_mutation=True)
def get_data(path):
    """
    :param path: file directory location
    :return: Pandas dataframe
    """
    data = pd.read_csv(path)

    return data


@st.cache(allow_output_mutation=True)
def transform_data(data):
    """
    :param data: raw dataframe
    :return: dataframe with data manipulated
    """
    # Selecting the indexes of non duplicates
    indexes = data['id'].drop_duplicates().index

    # Creating a new dataframe with distinct property id's
    data = data.iloc[indexes, :].reset_index(drop=True)

    # Converting data do datetime
    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')

    # Converting bathrooms to interger bacause it doesn't make sense having 1.5 bathrooms.
    # If there's any float, it will be converted to the closest interger
    data['bathrooms'] = round(data['bathrooms'], 0).astype('int64')

    # The same goes to floors
    data['floors'] = round(data['floors'], 0).astype('int64')

    # Changing waterfront variable input from 0/1 to 'No'/'Yes'
    data['waterfront'] = data['waterfront'].apply(lambda x: 'no' if x == 0 else 'yes')

    # Group dataframe by zipcode and take median price
    data_zipcode = data[['price', 'zipcode']].groupby('zipcode').median().sort_values(by='price',
                                                                                      ascending=False).reset_index()
    # Rename price column
    data_zipcode.rename(columns={'price': 'median_price_zipcode'}, inplace=True)

    # Merge with zipcode median price
    data = data.merge(right=data_zipcode, how='left', on='zipcode')

    # Create price index column
    data['price_index'] = data['price'] / data['median_price_zipcode']

    # Flag if the property should be purchased (index < 1 should be purchased)
    data['buy'] = data['price_index'].apply(lambda x: "buy" if x < 1 else "don't buy")

    # Extracting month name
    data['month_name'] = data['date'].dt.month_name()
    #
    # Classifying season purchased
    data['season_purchased'] = data['month_name'].apply(
        lambda x: 'winter' if x == 'December' or x == 'January' or x == 'February' else
        'spring' if x == 'March' or x == 'April' or x == 'May' else
        'summer' if x == 'June' or x == 'July' or x == 'August' else
        'autumn')

    # Group data by zipcode and season and take the count of properties
    zipcode_season_data = data[['zipcode', 'season_purchased', 'id']].groupby(['zipcode', 'season_purchased']).count().reset_index()

    # Extract the season with the greatest amount of properties
    zipcode_season_data = zipcode_season_data[zipcode_season_data['id'] == zipcode_season_data.groupby('zipcode')['id'].transform('max')].reset_index()

    # Input the season with more purchases within main dataframe. This season is the one recommended for purchasing
    data = data.merge(right=zipcode_season_data, how='left', on='zipcode')

    # Renaming and dropping dataframe columns to help further manipulation
    data.drop(columns=['index', 'id_y'])
    data.rename(columns={'id_x': 'id', 'season_purchased_x': 'season_purchased', 'season_purchased_y': 'sell_when'}, inplace=True)

    # Group data by zipcode and season to take median price, in order to determine median price by season
    data_zipcode_season = data[['price', 'zipcode', 'season_purchased']].copy().groupby(['zipcode', 'season_purchased']).median().reset_index()
    #
    # Rename price column
    data_zipcode_season.rename(columns={'price': 'median_price_zip_season'}, inplace=True)

    # Merging results
    data = pd.merge(left=data, right=data_zipcode_season, on=['zipcode', 'season_purchased'], how='left')

    # Dropping and renaming columns once again
    data.drop(columns=['index', 'id_y'], inplace=True)

    for item in range(len(data)):
        if data.loc[item, 'price'] <= data.loc[item, 'median_price_zipcode'] and data.loc[item, 'median_price_zip_season']:
            data.loc[item, 'proposed_price'] = data.loc[item, 'price'] * 1.3

        elif data.loc[item, 'price'] > (data.loc[item, 'median_price_zipcode'] and data.loc[item, 'median_price_zip_season']):
            data.loc[item, 'proposed_price'] = data.loc[item, 'price'] * 1.1

        else:
            data.loc[item, 'proposed_price'] = data.loc[item, 'price'] * 1.2

    data = data[['buy', 'id', 'price', 'proposed_price', 'sell_when', 'price_index', 'bedrooms', 'bathrooms',
                 'sqft_living', 'sqft_lot', 'floors', 'waterfront', 'condition', 'sqft_above', 'sqft_basement',
                 'yr_built', 'yr_renovated', 'date', 'zipcode', 'lat', 'long']]

    return data


@st.cache(allow_output_mutation=True)
def download_data(data):
    """
    :param data: dataframe that contaisn the data to be downloaded
    :return: download of filtered data in csv format
    """

    return data.to_csv().encode('utf-8')


# Indicates main function of the script
if __name__ == '__main__':

    # EXTRACTION
    df_raw = get_data(r'house-rocket-dash-app/kc_house_data.csv')

    # TRANSFORMING
    df = transform_data(df_raw)

    # LOADING
    # Set app title
    st.title('House Rocket Insights Project')

    # Creating filters
    purchase_filter = st.sidebar.checkbox(label='Display Purchasable Properties', value=False)
    zipcode_filter = st.sidebar.multiselect(label='Select Zipcode', options=df['zipcode'].unique())

    if purchase_filter and zipcode_filter == []:
        # Calling df2 because we will be modifying df1 according to the filter selected
        condition = (df['buy'] == 'buy')
        df1 = df.loc[condition, :].copy().sort_values(by=['waterfront', 'price_index'],
                                                      ascending=[False, True]).reset_index(drop=True)

    elif purchase_filter and zipcode_filter != []:
        condition = (df['buy'] == 'buy') & (df['zipcode'].isin(zipcode_filter))
        df1 = df.loc[condition, :].copy().sort_values(by=['waterfront', 'price_index'],
                                                      ascending=[False, True]).reset_index(drop=True)

    elif not purchase_filter and zipcode_filter != []:
        condition = df['zipcode'].isin(zipcode_filter)
        df1 = df.loc[condition, :].copy().reset_index(drop=True)

    else:
        df1 = df.copy()

    # Calculate profit only when purchasable propertier are selected
    if purchase_filter:
        profit = (round(df1['proposed_price'].sum() - df1['price'].sum(), 3))
        st.subheader('Potential Profit')
        st.metric('Potential Profit', value=profit)

    # Building DataFrame
    st.subheader('Purchase Recommendation')
    st.dataframe(df1)
    st.download_button('Export as csv', data=download_data(df1), file_name='seattle_properties.csv')

    # Plotting map
    st.subheader('Map Visualization')
    df2 = df1[['lat', 'long']].copy()
    df2.rename(columns={'lat': 'lat', 'long': 'lon'}, inplace=True)
    st.map(data=df2, zoom=9, use_container_width=True)

    # Exploratory Data Analysis

    st.subheader('Exploratory Data Analysis')

    st.write('**H1: Properties that have water front feature are 20% more expensive, on average, than those without a view**')

    # Creating dataframe to group data by category
    h1 = df[['price', 'waterfront']].groupby('waterfront').mean().reset_index()
    h1['price'] = round(h1['price'], 2)

    st.write('R: Properties with waterfront view are 212.93% more expensive')

    fig = px.bar(data_frame=h1, y='price', x='waterfront', text='price', labels={'price': 'mean_price'})

    st.plotly_chart(fig, use_container_width=True)

    #####################################################

    st.markdown('**H2: Properties with a construction date less than 1980 are 55% cheaper on average**')
    h2_base = df[['price', 'yr_built']].copy()

    # Create a flag to categorize if the property was built before/after 1980
    h2_base['1980_flag'] = h2_base['yr_built'].apply(lambda x: 'before_1980' if x < 1980 else
                                                               'after_1980' if x >= 1980 else 'NA')

    # Group data and take mean price by category
    h2 = h2_base[['price', '1980_flag']].groupby('1980_flag').mean().reset_index()
    h2['price'] = round(h2['price'], 2)

    st.write('R: Properties built before 1980 have a mean price 14.01% lower if compared with the ones built after')

    fig = px.bar(data_frame=h2, y='price', x='1980_flag', text='price', labels={'price': 'mean_price'})

    st.plotly_chart(fig, use_container_width=True)

    #####################################################

    st.write('**H3: Properties without basements have 40% more lot area than those without basements**')
    # Create a copy of main dataframe with the information needed to answer the hypothesis
    h3_base = df[['sqft_basement', 'sqft_lot']].copy()

    # Create a flag to categorize ifi the property have/don't have basement
    h3_base['basement_flag'] = h3_base['sqft_basement'].apply(lambda x: 'no_basement' if x == 0 else
                                                                        'basement' if x >= 1 else 'NA')

    # Group data and take mean area by category
    h3 = h3_base[['sqft_lot', 'basement_flag']].groupby('basement_flag').mean().reset_index()
    h3['sqft_lot'] = round(h3['sqft_lot'], 2)

    st.write('R: Properties without basement have a lot area 22.78% larger if compared with the ones with')

    fig = px.bar(data_frame=h3, y='sqft_lot', x='basement_flag', text='sqft_lot', labels={'sqft_lot': 'mean_sqft_lot_area'})

    st.plotly_chart(fig, use_container_width=True)

    #####################################################

    st.write('**H4: YoY (Year over Year) property price growth is 10%**')

    # Create a copy of main dataframe with the information needed to answer the hypothesis
    h4_base = df[['date', 'price']].copy()

    # Extract year of when the property got available  for purchase
    h4_base['yr_available'] = pd.DatetimeIndex(h4_base['date']).year

    # Group data and take mean price by year
    h4 = h4_base[['price', 'yr_available']].groupby('yr_available').mean().reset_index()
    h4['price'] = round(h4['price'], 2)

    st.write('R: We have properties available for 2014 and 2015 years, and the YoY price growth was of 0.7%')

    fig = px.bar(data_frame=h4, y='price', x='yr_available', text='price',
                 labels={'price': 'mean_price'})

    st.plotly_chart(fig, use_container_width=True)

    #####################################################

    st.write('**H5: Properties with 3 bathrooms or more have a MoM (Month over Month) growth of 15% in price**')

    # Create a copy of main dataframe with the information needed to answer the hypothesis
    h5_base = df.loc[df['bathrooms'] >= 3, ['price', 'bathrooms', 'date']].copy().reset_index()

    # Extract year and month
    h5_base['month'] = h5_base['date'].apply(lambda x: x.strftime('%m-%Y'))

    # Converts it to date format
    h5_base['month'] = pd.to_datetime(h5_base['month'], format='%m-%Y')

    # Group data and take mean price by month
    h5 = h5_base[['price', 'month']].groupby('month').mean().reset_index().sort_values(by='month')

    # Creates an empty column that will receive the variation over months in percentage
    h5['variation_pct'] = 'NA'

    # Calculates the variation
    for i in range(len(h5)):

        if i == 0:
            h5.loc[i, 'variation_pct'] = 0

        else:
            h5.loc[i, 'variation_pct'] = ((h5.loc[i, 'price'] - h5.loc[i - 1, 'price']) / h5.loc[i, 'price']) * 100

    fig = px.line(h5, x='month', y='variation_pct', title='Mean price MoM of available properties with 3 or more bathrooms for sale on portfolio')

    st.plotly_chart(fig, use_container_width=True)

    #####################################################

    st.write('**H6: Properties with 1 bedroom are 30% cheaper on average compared to properties with 2 or more**')

    # Create a copy of main dataframe with the information needed to answer the hypothesis
    h6_base = df[['price', 'bedrooms']].copy()

    # Creates a classification wether the property have one or more bedrooms
    h6_base['single_bedroom_flag'] = h6_base['bedrooms'].apply(lambda x: 'one_bedroom' if x == 1 else
                                                                         'two_or_more' if x > 1 else 'NA')

    # Dropping NA values
    h6_base = h6_base.loc[h6_base['single_bedroom_flag'] != 'NA', :].reset_index()

    # Group data and take mean price by category
    h6 = h6_base[['price', 'single_bedroom_flag']].groupby('single_bedroom_flag').mean().reset_index()
    h6['price'] = round(h6['price'], 2)

    st.write('R: Properties with one bedroom are 70.81% cheaper if compared with the ones with two or more')

    fig = px.bar(data_frame=h6, y='price', x='single_bedroom_flag', text='price',
                 labels={'price': 'mean_price'})

    st.plotly_chart(fig, use_container_width=True)

    #####################################################

    st.write('**H7: Total properties available for purchase grew 15% YoY**')

    # Create a copy of main dataframe with the information needed to answer the hypothesis
    h7_base = df[['date', 'id']].copy()

    # Extract year of when the property got available
    h7_base['yr_available'] = pd.DatetimeIndex(h7_base['date']).year

    # Group data and take count id by year
    h7 = h7_base[['id', 'yr_available']].groupby('yr_available').count().reset_index()

    st.write('R: The amount of properties available for purchase droped 113.51% YoY according with properties in database')

    fig = px.pie(data_frame=h7, values='id', names='yr_available', title='Amount of properties available by year')

    st.plotly_chart(fig, use_container_width=True)

    #####################################################

    st.write('**H8: The standard deviation of the price of properties that have more than 2 bedrooms is 40% lower than the others**')

    h8_base = df.loc[df['bedrooms'] >= 1, ['bedrooms', 'price']].reset_index()

    # Creates classification of number of bedrooms
    h8_base['bedrooms_flag'] = h8_base['bedrooms'].apply(lambda x: 'one_or_two' if x <= 2 else
                                                                   'more_than_two' if x > 2 else 'NA')

    # Group data and take std deviation of price by category
    h8 = h8_base[['price', 'bedrooms_flag']].groupby('bedrooms_flag').std().reset_index()
    h8['price'] = round(h8['price'], 2)

    st.write('R: The std deviation of properties with more than two bedrooms is 96.01% higher if compared with the ones with two or less')

    fig = px.bar(data_frame=h8, y='price', x='bedrooms_flag', text='price',
                 labels={'price': 'price_std_dev'})

    st.plotly_chart(fig, use_container_width=True)

    #####################################################

    st.write('**H9: Properties that have undergone renovation are 50% in better condition compared to properties that have not been renovated**')

    # Create a copy of main dataframe with the information needed to answer the hypothesis
    h9_base = df[['condition', 'yr_renovated']].copy()

    # Creates classification for properties that got renovated/didn't get and normalize condition to 1 or 0
    h9_base['renovated'] = h9_base['yr_renovated'].apply(lambda x: 'renovated' if x > 0 else 'no_renovated')
    h9_base['condition'] = h9_base['condition'].apply(lambda x: 1 if x == 4 or x == 5 else 0)

    # Group data and take mean for each category
    h9 = h9_base[['renovated', 'condition']].groupby('renovated').mean()

    st.write("R: From the properties that were renovated, 19% is in good condition (condition 4 or 5), while the ones that weren't have 35%  in good conditions")

    st.dataframe(h9)

    #####################################################

    st.write('**H10: Renovated properties from 1980 onwards are 50% in better condition compared to all other properties (renovated or not)**')

    # Create a copy of main dataframe with the information needed to answer the hypothesis
    h10_base = df[['condition', 'yr_renovated']].copy()

    # Creates classification for properties that got renovated/didn't get and normalize condition to 1 or 0
    h10_base['renovated'] = h10_base['yr_renovated'].apply(lambda x: 'renovated' if x >= 1980 else 'no_renovated')
    h10_base['condition'] = h10_base['condition'].apply(lambda x: 1 if x == 3 or x == 4 or x == 5 else 0)

    # Group data and take mean for each category
    h10 = h10_base[['renovated', 'condition']].groupby('renovated').mean()

    st.write("R: Considering 3 as good condition as well (3, 4, 5), "
             "we have nearly 100% of all properties renovated after 1980 in good condition and the same for the ones not renovated")

    st.dataframe(h10)
