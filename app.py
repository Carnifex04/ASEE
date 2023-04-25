import time
from pathlib import Path
from PlotFunctions import *
from BacktestFunctions import *
import holoviews as hv
import streamlit.components.v1 as components
import os
import requests
from alpha_vantage.timeseries import TimeSeries
import csv
import streamlit as st

# AlphaVantage API
AV_API = "AG077SBWLB8YFIIL"
# Display the Project info in the sidebar

st.sidebar.title('Algorithmic Stock Exchange Engine (ASEE)')
st.sidebar.markdown('---------')

# Side bar Navigation menu select

# Getting all the csv file names
data_files = os.listdir('data')
file_names = [os.path.splitext(file)[0] for file in data_files]

options = ['About'] + file_names + ['Other']
nav_select = st.sidebar.selectbox(label='Navigation', options=options)
custom_option = ""
if nav_select == 'Other':
    custom_option = st.sidebar.text_input('Enter custom option')
    add_button = st.sidebar.button('Add')
    if add_button and custom_option != '':
        # update the options list with the new file name
        options.insert(-1, custom_option)

print(nav_select)
# Dropdown selection of trading strategy
Strategy_select = st.sidebar.selectbox(label='Select Trading Strategy',
                                       options=['All Strategies', 'Strategy 1: William%R + SMA&LMA', 'Strategy 2: William%R', 'Strategy 3: VolatilityBreakout'])


# Algo specific Variables
# Define lookback window and percentage:
# lookback = 10
lookback = st.sidebar.slider(
    "Select the lookback days:", min_value=5, max_value=100, value=10)
st.sidebar.write("Lookback days you selected is:", lookback)
# Generate the short and long window simple moving averages (50 and 100 days, respectively)
short_window = 15
long_window = 30

# Set initial capital and initial share size
# initial_capital = float(100000)
initial_capital = float(st.sidebar.number_input(
    "Set the initial capital:", value=100000, min_value=100))
share_size = -500

# Define the list of years displayed in the Entry/Exit Points Charts
years = ['2017', '2018', '2019', '2020', '2021', '2022']
years = st.sidebar.multiselect(
    'Please select the year(s) you would like to view:',
    ['2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011',
        '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022'],
    ['2020', '2021', ])


# Set the percent for algorithm
percent = float(st.sidebar.number_input(
    "Breakout Percent", min_value=1, value=20))
st.sidebar.write("Breakout Percentage you set is:", percent, " %")

st.sidebar.markdown('---------')
if st.sidebar.button("Celebration Time!"):
    st.sidebar.balloons()
    # embed a song
    with st.sidebar:
        components.iframe(
            src="http://sdasofia.org/dataup/MUSIC/Music-classical/secret%20garden/Poeme%204.59.mp3", height=70, width=210)
# reset button status when select other options in dropdown box


if nav_select == 'About':
    intro_markdown = Path("README.md").read_text()
    st.markdown(intro_markdown, unsafe_allow_html=True)

elif nav_select == 'Other':
    st.markdown('RUNNING...')
    print(custom_option)
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={custom_option}&apikey={AV_API}&outputsize=full&datatype=csv'
    response = requests.get(url)

    if response.status_code == 200:
        # get the content of the file
        content = response.content.decode('utf-8')

        # create the file in the data folder with the user-specified name
        file_path = os.path.join('data', custom_option + '.csv')

        # write the content to a CSV file in the data folder
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            reader = csv.reader(content.splitlines())
            next(reader)  # skip the first row
            writer.writerow(['Date', 'Open', 'High', 'Low',
                            'Close', 'Adj Close', 'Volume'])
            for line in reader:
                date, open_price, high, low, close, adjusted_close, volume = line[
                    0], line[1], line[2], line[3], line[4], line[5], line[6]
                writer.writerow([date, open_price, high, low,
                                close, adjusted_close, volume])

else:
    print(nav_select)
    st.markdown(f'# {nav_select}')

    # Import current market data
    current_df = pd.read_csv(f'data/{nav_select}.csv',
                             index_col="Date",
                             parse_dates=True,
                             infer_datetime_format=True
                             )

    # Create Dataframes for plotting
    current_processed_df = process_df(
        current_df, lookback, short_window, long_window)

    if Strategy_select == 'Strategy 1: William%R + SMA&LMA':
        # Strategy 1
        st.markdown('### Entry/Exit Points')
        current_strategy_1 = Algo.ma_cross(
            short_window, current_processed_df, percent)
        current_plot_s1 = plot_strategy_1(
            current_strategy_1, nav_select, years)
        st.write(hv.render(current_plot_s1, backend='bokeh'))
        st.markdown(
            '### Strategy Backtest Result: Portfolio Cumulative Returns')
        current_return_s1 = calculate_s1_returns(
            current_strategy_1, initial_capital, share_size)
        current_returnplot_s1 = display_returns(
            current_return_s1, 'William%R + SMA&LMA', nav_select, years)
        st.write(hv.render(current_returnplot_s1, backend='bokeh'))
        # st.markdown('Place holder text for explanation of visual')
    elif Strategy_select == 'Strategy 2: William%R':
        # Strategy 2
        st.markdown('### Entry/Exit Points')
        current_strategy_2 = Algo.williams_r(current_processed_df, percent)
        current_plot_s2 = plot_strategy_2(
            current_strategy_2, nav_select, years)
        st.write(hv.render(current_plot_s2, backend='bokeh'))
        st.markdown(
            '### Strategy Backtest Result: Portfolio Cumulative Returns')
        current_return_s2 = calculate_s2_returns(
            current_strategy_2, initial_capital, share_size)
        current_returnplot_s2 = display_returns(
            current_return_s2, 'William%R', nav_select, years)
        st.write(hv.render(current_returnplot_s2, backend='bokeh'))
        # st.markdown('Place holder text for explanation of visual')
    elif Strategy_select == 'Strategy 3: VolatilityBreakout':
        # Strategy 3
        st.markdown('### Entry/Exit Points')
        current_strategy_3 = Algo.vol_breakout(current_processed_df, percent)
        current_plot_s3 = plot_strategy_3(
            current_strategy_3, nav_select, years)
        st.write(hv.render(current_plot_s3, backend='bokeh'))
        st.markdown(
            '### Strategy Backtest Result: Portfolio Cumulative Returns')
        current_return_s3 = calculate_s3_returns(
            current_strategy_3, initial_capital, share_size)
        current_returnplot_s3 = display_returns(
            current_return_s3, 'VolatilityBreakout', nav_select, years)
        st.write(hv.render(current_returnplot_s3, backend='bokeh'))
        # st.markdown('Place holder text for explanation of visual')
    elif Strategy_select == 'All Strategies':
        st.markdown('### Entry/Exit Points')
        # Strategy 1
        current_strategy_1 = Algo.ma_cross(
            short_window, current_processed_df, percent)
        current_plot_s1 = plot_strategy_1(
            current_strategy_1, nav_select, years)
        st.write(hv.render(current_plot_s1, backend='bokeh'))
        # Strategy 2
        current_strategy_2 = Algo.williams_r(current_processed_df, percent)
        current_plot_s2 = plot_strategy_2(
            current_strategy_2, nav_select, years)
        st.write(hv.render(current_plot_s2, backend='bokeh'))
        # Strategy 3
        current_strategy_3 = Algo.vol_breakout(current_processed_df, percent)
        current_plot_s3 = plot_strategy_3(
            current_strategy_3, nav_select, years)
        st.write(hv.render(current_plot_s3, backend='bokeh'))

        st.markdown(
            '### Strategy Backtest Result: Portfolio Cumulative Returns')
        current_return_s1 = calculate_s1_returns(
            current_strategy_1, initial_capital, share_size)
        current_returnplot_s1 = display_returns(
            current_return_s1, 'William%R', nav_select, years)
        st.write(hv.render(current_returnplot_s1, backend='bokeh'))
        current_return_s2 = calculate_s2_returns(
            current_strategy_2, initial_capital, share_size)
        current_returnplot_s2 = display_returns(
            current_return_s2, 'William%R + SMA&LMA', nav_select, years)
        st.write(hv.render(current_returnplot_s2, backend='bokeh'))
        current_return_s3 = calculate_s3_returns(
            current_strategy_3, initial_capital, share_size)
        current_returnplot_s3 = display_returns(
            current_return_s3, 'VolatilityBreakout', nav_select, years)
        st.write(hv.render(current_returnplot_s3, backend='bokeh'))

st.sidebar.markdown('---------')
st.sidebar.markdown('## Project Members:')
st.sidebar.markdown(
    '- [Avantika Modi](https://www.linkedin.com/in/avantikamodi/)')
st.sidebar.markdown(
    '- [Hriday Gupta](https://www.linkedin.com/in/hridaygupta/)')
st.sidebar.markdown('---------')
