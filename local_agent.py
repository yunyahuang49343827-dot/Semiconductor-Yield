import re

from ollama import chat

from agent_tools import (
    get_factory_overview,
    get_low_yield_lots,
    get_tool_analysis,
    get_traceability,
    get_yield_factor_analysis
)


# =========================================================
# Available Tools
# =========================================================

AVAILABLE_TOOLS = {
    "get_factory_overview": get_factory_overview,
    "get_low_yield_lots": get_low_yield_lots,
    "get_tool_analysis": get_tool_analysis,
    "get_traceability": get_traceability,
    "get_yield_factor_analysis": get_yield_factor_analysis,
}


# =========================================================
# System Prompt
# =========================================================

SYSTEM_PROMPT = """
You are a semiconductor manufacturing analytics assistant.

Your role is to help manufacturing engineers understand factory data
using verified backend tools.

Rules:

1. Use the provided tools for factory data, traceability, and KPIs.

2. Never invent manufacturing values.

3. Do not calculate factory KPIs yourself when a tool can provide
   the verified result.

4. If a tool returns no matching data, clearly state that no matching
   production data was found.

5. Keep answers concise, clear, and suitable for manufacturing engineers.

6. Do not claim causality unless explicitly supported by tool results.

7. Do not use words such as "significant" or "statistically significant"
   unless an actual statistical significance test was performed.

8. Do not infer specific failure mechanisms such as contamination,
   equipment damage, alignment problems, light source problems,
   dose control failure, etch damage, chamber instability,
   or throughput impact unless explicitly supported by tool results.

9. When tool-level yield is lower, describe the equipment only as:
   - "showing lower average yield"
   - "associated with lower yield"
   - "a candidate for further investigation"
   - "a priority for follow-up analysis"

10. Do not recommend a specific maintenance action unless the backend
    tool result or an approved SOP explicitly supports that action.

11. When identifying suspicious tools, explain that tool performance
    may be affected by product mix, technology node, lot mix,
    or other process conditions.

12. Prefer recommending further investigation using:
    - technology node
    - lot-level analysis
    - process parameters
    - defect metrics
    - wafer traceability

13. Clearly distinguish:
    observation → association → hypothesis → confirmed root cause.

14. Unless confirmed by additional evidence, never label equipment
    as faulty or as the root cause.

15. Manufacturing calculations must remain tool-grounded.

16. When recommending follow-up analysis, only reference data fields
    that are actually available in the tool results or backend dataset.
    Do not introduce unavailable fields such as defect type,
    defect location, gas flow, alignment status, or maintenance state
    unless explicitly provided.

17. Never invent, infer, guess, or display measurement units
    unless the unit is explicitly included in the backend tool result.
    If a backend value has no unit metadata, display only the numeric value.
    Missing unit metadata must remain unspecified.

18. Preserve numerical values exactly in meaning.
    Do not change magnitude, scale, exponent, or measurement unit.
    Presentation formatting and rounding are allowed only when
    the numeric meaning remains unchanged.

19. Never describe defect count or defect density as high, low,
    elevated, abnormal, or reduced unless the tool result includes
    an explicit comparison baseline and the comparison supports it.
    Otherwise report defect metrics neutrally.

20. You may format values for readability without changing their meaning.
    Yield values stored as decimals between 0 and 1 should normally
    be displayed as percentages.

21. You may round long decimal values for presentation:
    - percentages: 2 decimal places
    - ordinary numeric metrics: up to 4 decimal places
    - very large or very small values: scientific notation when useful

22. Do not display both a raw decimal yield and its percentage
    unless the user explicitly asks for raw values.

23. When discussing standardized differences, describe them as
    "larger standardized differences" rather than statistically
    significant differences unless a statistical test was performed.

24. When presenting rankings, keep the displayed order consistent
    with the ranking conclusion.
"""


# =========================================================
# Final Answer Sanitizer
# =========================================================

def sanitize_final_answer(answer: str) -> str:
    """
    Remove measurement units that the LLM may invent when the backend
    does not provide unit metadata.

    This is intentionally narrow: it targets known hallucinated unit
    patterns without changing the underlying numeric values.
    """

    if not answer:
        return answer

    cleaned = answer

    # Common hallucinated defect-density units
    cleaned = re.sub(
        r"\s*(defects?\s*/\s*cm(?:²|\^2|-2)?)",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(
        r"\s*(cm(?:²|\^2|-2))",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(
        r"\s*(defects?\s+per\s+cm(?:²|\^2|-2)?)",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(
        r"\s*(per\s+unit\s+area)",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    # Clean up double spaces introduced by removals
    cleaned = re.sub(
        r"[ \t]{2,}",
        " ",
        cleaned
    )

    return cleaned.strip()


# =========================================================
# Agent Function
# =========================================================

def ask_factory_agent(
    question: str,
    language: str = "English",
    return_trace: bool = False
):

    # -----------------------------------------------------
    # Language Instruction
    # -----------------------------------------------------

    if language == "中文":

        language_instruction = """
Answer in Traditional Chinese.

Keep technical manufacturing terms such as:
Yield, Lot, Wafer, Tool, FastAPI, Function Calling,
Critical Dimension, Vth, Defect Density
in English when useful for clarity.

Do not use Simplified Chinese.
"""

    else:

        language_instruction = """
Answer in English.
Use concise and professional manufacturing terminology.
"""


    # -----------------------------------------------------
    # Trace Information for Evaluation
    # -----------------------------------------------------

    tool_trace = {
        "tool_name": None,
        "arguments": {}
    }


    # -----------------------------------------------------
    # Conversation
    # -----------------------------------------------------

    messages = [
        {
            "role": "system",
            "content": (
                SYSTEM_PROMPT
                + "\n"
                + language_instruction
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]


    # -----------------------------------------------------
    # Step 1
    # Let Qwen decide whether a tool is required
    # -----------------------------------------------------

    response = chat(
        model="qwen3.5:9b",
        messages=messages,
        tools=[
            get_factory_overview,
            get_low_yield_lots,
            get_tool_analysis,
            get_traceability,
            get_yield_factor_analysis
        ],
        think=False,
        options={
            "temperature": 0
        }
    )

    messages.append(
        response.message
    )


    # -----------------------------------------------------
    # Step 2
    # Execute Tool Calls
    # -----------------------------------------------------

    if response.message.tool_calls:

        for tool_call in response.message.tool_calls:

            function_name = (
                tool_call.function.name
            )

            arguments = (
                tool_call.function.arguments
            )


            # Save trace for evaluation
            tool_trace = {
                "tool_name": function_name,
                "arguments": arguments
            }


            print(
                f"\n[Tool selected] "
                f"{function_name}"
            )

            print(
                f"[Arguments] "
                f"{arguments}"
            )


            # ---------------------------------------------
            # Validate Tool Name
            # ---------------------------------------------

            function = AVAILABLE_TOOLS.get(
                function_name
            )

            if function is None:

                raise ValueError(
                    f"Unknown tool: "
                    f"{function_name}"
                )


            # ---------------------------------------------
            # Execute Tool
            # ---------------------------------------------

            try:

                tool_result = function(
                    **arguments
                )

            except Exception as error:

                tool_result = {
                    "error":
                        f"Tool execution failed: "
                        f"{str(error)}"
                }


            print(
                f"[Tool result] "
                f"{tool_result}"
            )


            # ---------------------------------------------
            # Add Tool Result to Conversation
            # ---------------------------------------------

            messages.append(
                {
                    "role": "tool",
                    "tool_name": function_name,
                    "content": str(
                        tool_result
                    )
                }
            )


        # -------------------------------------------------
        # Step 3
        # Qwen explains verified tool result
        # -------------------------------------------------

        final_response = chat(
            model="qwen3.5:9b",
            messages=messages,
            think=False,
            options={
                "temperature": 0
            }
        )


        answer = (
            final_response
            .message
            .content
        )

        # Deterministic final-answer cleanup
        answer = sanitize_final_answer(
            answer
        )


        # ---------------------------------------------
        # Evaluation Mode
        # ---------------------------------------------

        if return_trace:

            return {
                "answer": answer,
                "tool_name": tool_trace["tool_name"],
                "arguments": tool_trace["arguments"]
            }


        return answer


    # -----------------------------------------------------
    # No Tool Required
    # -----------------------------------------------------

    answer = response.message.content

    answer = sanitize_final_answer(
        answer
    )


    if return_trace:

        return {
            "answer": answer,
            "tool_name": None,
            "arguments": {}
        }


    return answer


# =========================================================
# Local Test
# =========================================================

if __name__ == "__main__":

    result = ask_factory_agent(
        (
            "Show the defect density and "
            "average yield for the factory."
        ),
        language="English",
        return_trace=True
    )

    print(
        "\n=== Evaluation Trace ==="
    )

    print(
        result
    )