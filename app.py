import os
import streamlit as st
from dotenv import load_dotenv

from pydantic import BaseModel, Field, field_validator

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from langchain_core.output_parsers import (
    PydanticOutputParser
)

from langchain_groq import ChatGroq


# ======================================
# Load Environment Variables
# ======================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found in .env file"
    )


# ======================================
# Streamlit Page Config
# ======================================

st.set_page_config(
    page_title="Complaint Analyzer",
    layout="centered"
)


# ======================================
# Pydantic Output Schema
# ======================================

class ComplaintAnalysis(BaseModel):

    complaint_category: str = Field(
        description="Category of complaint"
    )

    severity: str = Field(
        description="Severity level"
    )

    root_issue: str = Field(
        description="Main issue identified"
    )

    recommended_action: str = Field(
        description="Recommended business action"
    )

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value):

        allowed = ["High", "Medium", "Low"]

        if value not in allowed:
            raise ValueError(
                "Severity must be High, Medium, or Low"
            )

        return value


# ======================================
# Output Parser
# ======================================

parser = PydanticOutputParser(
    pydantic_object=ComplaintAnalysis
)


# ======================================
# Prompt Templates
# ======================================

system_prompt = (
    SystemMessagePromptTemplate.from_template(
        """
You are an AI Complaint Analyzer.

Analyze customer complaints carefully.

Rules:
- Use ONLY information present.
- Do NOT assume unsupported facts.
- Keep explanations concise.
- Severity must ONLY be:
  High, Medium, or Low.

Severity Guidelines:

High:
- Financial loss
- Major issue
- Serious inconvenience
- Repeated unresolved issue

Medium:
- Delayed service
- Poor support
- Moderate inconvenience

Low:
- Minor inconvenience
- Mild dissatisfaction

Return the response strictly
in the required JSON format.

{format_instructions}
"""
    )
)

human_prompt = (
    HumanMessagePromptTemplate.from_template(
        """
Complaint:
{complaint}
"""
    )
)


# ======================================
# Create Prompt
# ======================================

prompt = ChatPromptTemplate.from_messages(
    [
        system_prompt,
        human_prompt
    ]
).partial(
    format_instructions=(
        parser.get_format_instructions()
    )
)


# ======================================
# Initialize Groq Model
# ======================================

try:

    model = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=GROQ_API_KEY,
        temperature=0
    )

except Exception as e:

    st.error(
        "Failed to initialize Groq model."
    )

    st.exception(e)

    st.stop()


# ======================================
# LangChain Pipeline
# ======================================

chain = prompt | model | parser


# ======================================
# Streamlit UI
# ======================================

st.title("Complaint Analyzer")

st.write(
    "Analyze customer complaints using AI."
)



complaint = st.text_area(
    "Enter Customer Complaint",
    height=180,
    placeholder=(
        "Example: My food order arrived "
        "two hours late and it was cold."
    )
)


# ======================================
# Analyze Button
# ======================================

if st.button("Analyze Complaint"):

    if complaint.strip() == "":

        st.warning(
            "Please enter a complaint."
        )

    else:

        try:

            with st.spinner(
                "Analyzing complaint..."
            ):

                result = chain.invoke(
                    {
                        "complaint": complaint
                    }
                )

            st.success(
                "Analysis Complete "
            )

            st.subheader(
                "Structured Output"
            )

            st.json(
                result.model_dump()
            )

        except Exception as e:

            st.error(
                "An error occurred while "
                "processing the complaint."
            )

            st.exception(e)