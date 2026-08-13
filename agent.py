import os
from google import genai

from agent_tools import (
    get_factory_overview,
    get_low_yield_lots,
    get_tool_analysis,
    get_traceability
)


client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


SYSTEM_INSTRUCTION = """
You are a manufacturing analytics assistant.

Rules:
1. Factory KPIs must come from tools.
2. Do not invent production data.
3. If a tool returns no data, clearly say no matching data was found.
4. Do not claim causality unless the data supports it.
5. Use terms such as potential contributing factor or associated factor.
"""


def ask_factory_agent(question: str):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=question,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            "tools": [
                get_factory_overview,
                get_low_yield_lots,
                get_tool_analysis,
                get_traceability
            ],
        },
    )

    return response.text