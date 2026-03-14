"""
Generate Architecture Diagram for Gemini Scraper Agent
Creates professional architecture visualization

Requirements:
  pip install diagrams

Usage:
  python docs/architecture_diagram.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.gcp.compute import Run
from diagrams.gcp.ml import AIPlatform
from diagrams.gcp.storage import Storage
from diagrams.gcp.security import KeyManagementService
from diagrams.gcp.devtools import Build
from diagrams.onprem.client import User, Users

# Create diagram
with Diagram("Gemini Scraper Agent - Architecture", 
             filename="docs/architecture_diagram",
             show=False,
             direction="LR"):
    
    # Users
    user = User("User")
    
    with Cluster("Google Cloud Platform"):
        
        with Cluster("Frontend Layer"):
            cloudrun = Run("Cloud Run\n(Streamlit App)")
        
        with Cluster("AI Layer"):
            gemini = AIPlatform("Vertex AI\nGemini 2.0 Flash")
        
        with Cluster("Storage Layer"):
            gcs = Storage("Cloud Storage\n(Scraped Data)")
            secrets = KeyManagementService("Secret Manager\n(API Keys)")
        
        with Cluster("Build Pipeline"):
            cloudbuild = Build("Cloud Build\n(CI/CD)")
    
    # External services
    with Cluster("External"):
        websites = Users("Target Websites")
    
    # Connections
    user >> Edge(label="HTTPS") >> cloudrun
    cloudrun >> Edge(label="API Call") >> gemini
    cloudrun >> Edge(label="Store Data") >> gcs
    cloudrun >> Edge(label="Get Secrets") >> secrets
    cloudrun >> Edge(label="Scrape") >> websites
    cloudbuild >> Edge(label="Deploy") >> cloudrun
    
    gemini >> Edge(label="Multimodal\nResponse", style="dashed") >> cloudrun

print("✅ Architecture diagram created: docs/architecture_diagram.png")
