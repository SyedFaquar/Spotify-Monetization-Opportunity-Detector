import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(page_title="Podcast Monetization Dashboard", layout="wide")

# Header
st.title("Podcast Monetization Dashboard")
st.markdown("---")

# Simple Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Episodes", value="248")
with col2:
    st.metric(label="Avg Duration", value="45m")
with col3:
    st.metric(label="Revenue", value="$2,450")
with col4:
    st.metric(label="Engagement", value="87%")

# Simple Data
try:
    engagement_data = {
        'time': ['0-5', '5-10', '10-15', '15-20', '20-25', '25-30', '30-35', '35-40', '40-45'],
        'score': [0.5, 0.9, 0.7, 0.6, 0.8, 0.9, 0.7, 0.9, 0.6]
    }
    engagement_df = pd.DataFrame(engagement_data)
    
    # Engagement Chart
    st.subheader("Engagement Score")
    fig = px.line(engagement_df, x='time', y='score', title='Listener Engagement Over Episode Duration')
    st.plotly_chart(fig, use_container_width=True)
    
except Exception as e:
    st.error(f"Error in engagement chart: {str(e)}")

# Ad Placement Recommendations
try:
    st.subheader("Ad Placement Recommendations")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("Optimal Ad Break Points")
        st.write("• First break: 8.89 minutes")
        st.write("• Second break: 36.11 minutes")
    
    with col2:
        st.success("Revenue Potential")
        st.write("• Per episode: $60")
        st.write("• Monthly: $1,800")
        
except Exception as e:
    st.error(f"Error in recommendations: {str(e)}")