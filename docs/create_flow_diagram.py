"""
Create User Flow Diagram

Requirements:
  pip install diagrams

Usage:
  python docs/create_flow_diagram.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.programming.flowchart import StartEnd, Action, Decision, InputOutput

with Diagram("User Interaction Flow",
             filename="docs/flow_diagram",
             show=False,
             direction="TB"):
    
    start = StartEnd("User Opens App")
    
    with Cluster("Live Session"):
        init = Action("Initialize Gemini\nLive Session")
        voice_or_text = Decision("Voice or\nText Input?")
        
        voice = InputOutput("🎤 Voice Input")
        text = InputOutput("⌨️ Text Input")
        
        process = Action("Gemini Processes\nRequest")
        
    with Cluster("Scraping"):
        fetch = Action("Fetch Webpage")
        analyze = Action("Gemini Analyzes\nVisual Structure")
        extract = Action("Extract Data")
        
    with Cluster("Interactive"):
        interrupt = Decision("User\nInterrupts?")
        adjust = Action("Adjust Strategy")
        continue_scrape = Action("Continue Scraping")
    
    with Cluster("Results"):
        display = Action("Display Results")
        chat = Action("Chat About Data")
        download = Action("Download CSV")
    
    end = StartEnd("Session End")
    
    # Flow
    start >> init >> voice_or_text
    voice_or_text >> Edge(label="voice") >> voice >> process
    voice_or_text >> Edge(label="text") >> text >> process
    process >> fetch >> analyze >> extract
    extract >> interrupt
    interrupt >> Edge(label="yes") >> adjust >> continue_scrape >> extract
    interrupt >> Edge(label="no") >> display >> chat >> download >> end

print("✅ Flow diagram created: docs/flow_diagram.png")
