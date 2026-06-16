# Complaint Analyzer

**Live Demo**: [🚀 Try Live App] https://complaint-analyzer-hfwazsdbf5v3btxt379kzw.streamlit.app/

## Overview
An **AI-powered Complaint Analysis** system that intelligently analyzes customer complaints using Google Gemini. It categorizes complaints, identifies severity, extracts root issues, and provides actionable recommendations.

## Features
- Structured complaint analysis
- Automatic categorization (Product, Service, Delivery, Support, etc.)
- Severity assessment (High/Medium/Low)
- Root cause identification
- Actionable recommendations
- Clean and professional Streamlit interface

## Example Output
```json
{
  "complaint_category": "Product and Customer Support",
  "severity": "High",
  "root_issue": "Damaged product and unresponsive customer support",
  "recommended_action": "Respond to customer email, replace or refund damaged product, and improve customer support responsiveness"
}

Tech Stack

Python
LangChain
Google Gemini API
Streamlit

How to Run Locally:

Bash git clone https://github.com/Adepuharshavardhan2001/Complaint-analyzer.git
cd Complaint-analyzer
pip install -r requirements.txt
streamlit run app.py

<img width="64" height="37" alt="image" src="https://github.com/user-attachments/assets/7ca23237-1d9d-4ff0-bdf4-ebb770208256" />
<img width="64" height="29" alt="image" src="https://github.com/user-attachments/assets/008651fd-23f3-499c-9c1d-4f2c690dfe77" />

Project Highlights

Real-world customer support use case
Structured JSON output for easy integration
Transparent AI reasoning
Production-ready design

Future Improvements

Batch processing of multiple complaints
Complaint trend analytics dashboard
Email auto-response generation
Integration with CRM/ticketing tools
