import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page configuration
st.set_page_config(page_title="Jiji Housing Market Analysis", layout="wide")

# Load data


@st.cache_data
def load_data():
    return pd.read_csv('jiji_housing_cleaned.csv')


df = load_data()

# ==========================================
# SIDEBAR FILTERS (DYNAMIC SLICERS)
# ==========================================
st.sidebar.title("🔍 Filter Dashboard")
st.sidebar.markdown(
    "Select filters to update the analysis dynamically. By default, all options are selected.")

# Get unique values for filters
states = sorted(df['Region Parent Name'].dropna().unique().tolist())
furnishings = sorted(df['Furnishing'].dropna().unique().tolist())
bedrooms = sorted(df['Bedrooms'].dropna().unique().tolist())
boosts = sorted(df['Is Boosted'].dropna().unique().tolist())

# Multiselects with default = all options
selected_states = st.sidebar.multiselect(
    "Select State(s):", states, default=states)
selected_furnishings = st.sidebar.multiselect(
    "Select Furnishing Type(s):", furnishings, default=furnishings)
selected_bedrooms = st.sidebar.multiselect(
    "Select Number of Bedrooms:", bedrooms, default=bedrooms)
selected_boosts = st.sidebar.multiselect(
    "Select Listing Type (Boost):", boosts, default=boosts)

# Add a reset button
if st.sidebar.button("🔄 Reset Filters to Default"):
    st.rerun()  # Resets to default values

# Apply filters to create a filtered dataframe
filtered_df = df[
    (df['Region Parent Name'].isin(selected_states)) &
    (df['Furnishing'].isin(selected_furnishings)) &
    (df['Bedrooms'].isin(selected_bedrooms)) &
    (df['Is Boosted'].isin(selected_boosts))
]

# ==========================================
# MAIN DASHBOARD
# ==========================================
st.title("🏠 Nigeria Jiji Housing Marketplace Analysis")
st.markdown(
    "Interactive dashboard exploring real estate trends, pricing, and regional distributions on Jiji.ng.")
st.markdown("---")

# Handle case where filtered_df is empty
if filtered_df.empty:
    st.warning(
        "⚠️ No data matches the selected filters. Please adjust your filters in the sidebar.")
    st.stop()

# ==========================================
# KPI SECTION (TASK 4 REQUIREMENT)
# ==========================================
st.header("📊 Key Performance Indicators (KPIs)")
col1, col2, col3, col4 = st.columns(4)

total_listings = len(filtered_df)
avg_price = filtered_df['Price'].mean()
most_common_region = filtered_df['Region Parent Name'].mode()[0]
furnished_count = len(filtered_df[filtered_df['Furnishing'] == 'Furnished'])
pct_furnished = (furnished_count / total_listings) * 100

col1.metric("Total House Listings", f"{total_listings:,}")
col2.metric("Average House Price", f"₦{avg_price:,.0f}")
col3.metric("Most Frequent Region", most_common_region)
col4.metric("% Furnished Houses", f"{pct_furnished:.1f}%")

st.markdown("---")

# ==========================================
# VISUALIZATIONS (PLOTLY)
# ==========================================
st.header("📈 Data Visualizations")

# --- CHART 1: Full Width ---
st.subheader("1. Number of Listings per State")
state_counts = filtered_df['Region Parent Name'].value_counts().reset_index()
state_counts.columns = ['State', 'Number_of_Listings']
fig1 = px.bar(state_counts, x='State', y='Number_of_Listings',
              color='Number_of_Listings', color_continuous_scale='Blues')
fig1.update_layout(xaxis_tickangle=-45, height=500,
                   margin=dict(l=0, r=0, t=30, b=0))
st.plotly_chart(fig1, use_container_width=True)

# --- CHART 2: Full Width ---
st.subheader("2. Average House Price per State")
state_avg_price = filtered_df.groupby('Region Parent Name')[
    'Price'].mean().reset_index()
state_avg_price.columns = ['State', 'Average_Price']
state_avg_price = state_avg_price.sort_values(
    by='Average_Price', ascending=False)
fig2 = px.bar(state_avg_price, x='State', y='Average_Price',
              color='Average_Price', color_continuous_scale='Reds')
fig2.update_layout(xaxis_tickangle=-45, height=500,
                   margin=dict(l=0, r=0, t=30, b=0))
fig2.update_yaxes(tickformat=',.0f')
st.plotly_chart(fig2, use_container_width=True)


# --- ROW 2 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("3. Distribution of Property Prices")
    fig3 = px.histogram(filtered_df, x='Price', nbins=40,
                        color_discrete_sequence=['#636EFA'])
    fig3.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0))
    fig3.update_xaxes(title_text="Price (₦)", tickformat=',.0f')
    fig3.update_yaxes(title_text="Frequency")
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("4. Price Distribution by Number of Bedrooms")
    fig4 = px.box(filtered_df, x='Bedrooms', y='Price',
                  color='Bedrooms', color_discrete_sequence=px.colors.qualitative.Pastel)
    fig4.update_layout(height=400, showlegend=False,
                       margin=dict(l=0, r=0, t=30, b=0))
    fig4.update_xaxes(title_text="Number of Bedrooms")
    fig4.update_yaxes(title_text="Price (₦)", tickformat=',.0f')
    st.plotly_chart(fig4, use_container_width=True)

# --- ROW 3 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("5. Property Size vs. Price")
    fig5 = px.scatter(filtered_df, x='Property Size', y='Price',
                      color='Region Parent Name', opacity=0.6,
                      hover_data=['Title', 'Region Name', 'Bedrooms'])
    fig5.update_layout(height=400, legend_title='State',
                       margin=dict(l=0, r=0, t=30, b=0))
    fig5.update_xaxes(title_text="Property Size (sqm)", tickformat=',.0f')
    fig5.update_yaxes(title_text="Price (₦)", tickformat=',.0f')
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    st.subheader("6. Furnishing Type Distribution")
    furnishing_counts = filtered_df['Furnishing'].value_counts().reset_index()
    furnishing_counts.columns = ['Furnishing_Type', 'Count']
    fig6 = px.pie(furnishing_counts, values='Count', names='Furnishing_Type',
                  hole=0.4,
                  color='Furnishing_Type',
                  color_discrete_map={
                      'Unfurnished': '#636EFA',
                      'Semi-Furnished': '#00CC96',
                      'Furnished': '#EF553B',
                      'Unknown': '#AB63FA'
                  })
    fig6.update_traces(textposition='inside', textinfo='percent+label')
    fig6.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig6, use_container_width=True)

# --- ROW 4 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("7. Correlation Heatmap of Numeric Variables")
    numeric_df = filtered_df[['Price', 'Property Size',
                              'Bedrooms', 'Bathrooms']].dropna()

    if len(numeric_df) > 1:
        corr_matrix = numeric_df.corr()
        fig7 = px.imshow(corr_matrix, text_auto='.2f',
                         color_continuous_scale='RdBu_r', aspect="auto")
        fig7.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig7, use_container_width=True)
    else:
        st.warning(
            "Not enough data to compute correlation for the selected filters.")

with col2:
    st.subheader("📊 Correlation Insights")
    if len(numeric_df) > 1:
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Price vs Size",
                      f"{corr_matrix.loc['Price', 'Property Size']:.3f}")
            st.metric("Price vs Bedrooms",
                      f"{corr_matrix.loc['Price', 'Bedrooms']:.3f}")
        with m2:
            st.metric("Price vs Bathrooms",
                      f"{corr_matrix.loc['Price', 'Bathrooms']:.3f}")
            st.metric("Bedrooms vs Bathrooms",
                      f"{corr_matrix.loc['Bedrooms', 'Bathrooms']:.3f}")
    else:
        st.info("Adjust filters to see correlation insights.")

st.markdown("---")

# ==========================================
# TASK 5 & 6: SUMMARY & INSIGHTS
# ==========================================
st.header("📝 Summary of Findings & Business Insights")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Key Findings (Task 5)")
    st.info("""
    1. **Highest-Priced States**: Lagos and Abuja (FCT) consistently feature the highest-priced listings.
    2. **Most Affordable States**: States like Ogun, Edo, and Oyo offer the most affordable housing options.
    3. **Furnishing Impact**: Furnished homes consistently command a premium over unfurnished ones.
    4. **Feature Influence**: Property size and bedrooms show a strong positive correlation with price.
    5. **Boosted Listings**: Boosted (Enterprise/VIP) listings are typically more expensive.
    6. **Premium Property Types**: 5+ bedroom duplexes in gated estates attract the highest pricing.
    7. **Regional Patterns**: Lagos dominates volume, while Abuja leads in high-value, spacious properties.
    """)

with col_right:
    st.subheader("Business Recommendations (Task 6)")
    st.success("""
    1. **Best Performing Feature**: 4–5 bedroom semi-furnished duplexes in secure estates.
    2. **Top Revenue Potential**: Lagos State (Lekki, Ikoyi, Ikeja GRA) contributes the most revenue.
    3. **Underperforming States**: Regions like Ekiti, Kwara, and Plateau underperform in volume/value.
    4. **Listing Activity**: Q4 and early Q1 typically record the highest activity (diaspora returns).
    5. **Low-Performing Strategy**: Promote affordable housing schemes and flexible payment plans.
    6. **Seller Visibility**: Invest in 'Boosted' listings and professional photography to justify premium pricing.
    """)
