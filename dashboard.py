import streamlit as st
import plotly.express as px  # Using plotly to generate charts
from matplotlib import pyplot as py
import pandas as pd          # Using pandas for data handling
import os                    # Using os for file navigation
import warnings              # Using to avoid warnings

warnings.filterwarnings('ignore')

# Function to display values with text inside the box
def DisplayInsideBox(value, label, selected_color):
    # Display the selected color and value with text inside the box
    st.markdown(f"""
        <div style='
            background-color: {selected_color};
            padding: 2px;
            text-align: center;
            border-radius: 10px;
            margin-top: 20px;
            margin-left: 50px;
            margin-bottom: 30px;
            margin-right: 50px
            '>
            <h1 style='color: white; font-size: 50px;'>{value}</h1>
            <h3 style='color: black; font-size: 25px; font-weight: bold;'>{label}</h3>
        </div>
    """, unsafe_allow_html=True)

def format_large_number(number):
    if number >= 1000000:
        # Convert to 'M' format
        formatted_number = f'{number/1000000:.1f}M'
    elif number >= 1000:
        # Convert to 'k' format
        formatted_number = f'{number/1000:.1f}K'
    else:
        formatted_number = str(number)

    return formatted_number


st.set_page_config(page_title="Superstore!!!", page_icon="🛍️", layout="wide")

# Aligning the Title at the center
st.markdown('<style>div.block-container{padding:1rem;}</style>', unsafe_allow_html=True)
st.title("🛍️ SuperStore Trend and Analysis")

df = pd.read_csv("Superstore.csv", encoding="ISO-8859-1")

col1, col2, col3 = st.columns((3))

with col1:
    TotalSales = int(df["Sales"].sum())
    TotalSales = format_large_number(TotalSales)
    DisplayInsideBox('$'+TotalSales, "Total Sales", "#3498db")

with col2:
    TotalProfit = int(df["Profit"].sum())
    TotalProfit = format_large_number(TotalProfit)
    DisplayInsideBox('$'+TotalProfit, "Total Profit", "#2ecc71")

with col3:
    TotalQuantity = int(df["Quantity"].count())
    DisplayInsideBox(TotalQuantity, "Quantity Sold", "#f39c12")

# Creating two columns for start and end date
col1, col2 = st.columns((2))

df["Order Date"] = pd.to_datetime(df["Order Date"])

# Getting the min and max date
# Selecting the Minimum Date from "Order Date" Column
StartDate = pd.to_datetime(df["Order Date"]).min()
# Selecting the Maximum Date from "Order Date" Column
EndDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", StartDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", EndDate))

st.write(TotalSales)

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= EndDate)].copy()

# Creating a Side Bar to filter out the data as per user requirement
st.sidebar.header("Choose your filter: ")

# Filter on the basis of "Region"
region = st.sidebar.multiselect("Pick your region: ", df["Region"].unique())
if not region:
    # if user doesn't select any region, dataframe remains the same
    df2 = df.copy()
else:
    # else filter out dataframe containing region selected by user
    df2 = df[(df["Region"].isin(region))]

# Filter on the basis of "State" - Using Updated DataFrame "df2"
state = st.sidebar.multiselect("Pick your state: ", df2["State"].unique())
if not state:
    # if user doesn't select any state, dataframe remains the same
    df3 = df2.copy()
else:
    # else filter out dataframe containing state selected by user
    df3 = df2[(df2["State"].isin(state))]

# Filter on the basis of "City" - Using Updated DataFrame "df3"
city = st.sidebar.multiselect("Pick your city: ", df3["City"].unique())

# Filter the data based on Region, State, and City
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not state:
    filtered_df = df[df["City"].isin(city)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(
        region) & df3["State"].isin(state) & df3["City"].isin(city)]

# Select the dataframe after grouping the rows on thebasis of column "Category" and for each category, calculating the Total Sales for each category
category_df = filtered_df.groupby(
    by=["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Category Wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text=[
                 '${:,.2f}'.format(x) for x in category_df["Sales"]], template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Region Wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text=filtered_df["Region"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns((2))

with cl1:
    with st.expander("🔽 Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv",
                           mime="text/csv", help="Click here to download data as a CSV file")

with cl2:
    with st.expander("🔽 Region_ViewData"):
        region = filtered_df.groupby(by="Region", as_index=False)[
            "Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv",
                           mime="text/csv", help="Click here to download data as a CSV file")

filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader(":bar_chart: Time Series Analysis")

LineChart = pd.DataFrame(filtered_df.groupby(
    filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(LineChart, x="month_year", y="Sales", labels={
               "Sales": "Amount"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("🔽 TimeSeriesAnalysis_ViewData"):
    st.write(LineChart.style.background_gradient(cmap="Blues"))
    csv = LineChart.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data", data=csv, file_name="TimeSeriesAnalysis.csv",
                       mime="text/csv", help="Click here to download data as a CSV file")

col1, col2 = st.columns((2))

with col1:
    st.subheader("📈 Profit Trends vs. Discounts")
    # Scatter plot for Quantity vs. Sales using Plotly Express
    fig3 = px.scatter(filtered_df, x='Discount', y='Profit',labels={'Quantity': 'Quantity Sold', 'Sales': 'Sales ($)'})

    st.plotly_chart(fig3, use_container_width=True, height=200)

with col2:
    st.subheader("📉 Sales Trends vs. Discounts")
    # Create an area chart for 'Discount' and 'Profit'
    fig4 = px.area(filtered_df, x='Discount', y='Sales', labels={'Discount': 'Discount', 'Profit': 'Profit'})
    st.plotly_chart(fig4, use_container_width=True, height=200)

# Display the result
st.header("🚩 Top 5 Best-Selling Products")

# Group by Product ID and sum the Sales and Quantity for each product
product_sales = df.groupby(['Product ID', 'Product Name', 'Category'])[['Sales', 'Quantity']].sum()

# Sort the DataFrame based on total Sales in descending order
sorted_products = product_sales.sort_values(by='Sales', ascending=False)

# Select the top 5 best-selling products
top_5_products = sorted_products.head(5)

st.write(top_5_products.style.background_gradient(cmap="Oranges"))
