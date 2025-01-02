 
import streamlit as st
import plotly.express as px
from datetime import datetime

class Dashboard:
    def __init__(self, db_client):
        self.db = db_client
        
    def render(self):
        st.title("Knowledge Management System Monitor")
        
        # Status Overview
        stats = {
            "pending": self.db.sources.count_documents({"status": "pending"}),
            "processed": self.db.sources.count_documents({"status": "processed"}),
            "error": self.db.sources.count_documents({"status": "error"})
        }
        
        # Create visualization
        fig = px.pie(values=list(stats.values()), names=list(stats.keys()))
        st.plotly_chart(fig)
