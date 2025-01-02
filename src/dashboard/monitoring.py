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

        # Recent Errors
        st.subheader("Recent Errors")
        errors = self.db.sources.find(
            {"status": "error"},
            limit=5,
            sort=[("timestamp", -1)]
        )
        for error in errors:
            st.error(f"{error['url']}: {error.get('error_msg', 'Unknown error')}")
