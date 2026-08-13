# Step 8 — AI Agent Tools
#
# LLM responsibilities:
# - Understand user intent
# - Select the appropriate tool
# - Explain verified tool results
#
# Python / FastAPI responsibilities:
# - Retrieve data
# - Calculate KPIs
# - Sort results
# - Format numeric values
# - Preserve deterministic behavior


import requests


API_BASE_URL = "http://127.0.0.1:8000"


# =========================================================
# Factory Overview
# =========================================================

def get_factory_overview():
    """Get overall factory manufacturing KPIs."""

    response = requests.get(
        f"{API_BASE_URL}/analytics/overview",
        timeout=5
    )

    response.raise_for_status()

    data = response.json()

    return {
        "total_wafers": int(
            data["total_wafers"]
        ),

        "total_lots": int(
            data["total_lots"]
        ),

        "average_yield": round(
            float(data["average_yield"]),
            6
        ),

        "average_defect_count": round(
            float(data["average_defect_count"]),
            2
        ),

        "average_defect_density": round(
            float(data["average_defect_density"]),
            4
        )
    }


# =========================================================
# Low-Yield Lots
# =========================================================

def get_low_yield_lots(
    limit: int = 5
):
    """
    Get production lots with the lowest average yield.

    Results are deterministically sorted from
    lowest average yield to highest average yield.
    """

    limit = int(limit)

    response = requests.get(
        f"{API_BASE_URL}/analytics/lots",
        timeout=5
    )

    response.raise_for_status()

    lots = response.json()

    # Deterministic ranking in Python
    lots = sorted(
        lots,
        key=lambda x: float(
            x["average_yield"]
        )
    )

    result = []

    for lot in lots[:limit]:

        result.append({
            "lot_id": str(
                lot["lot_id"]
            ),

            "wafer_count": int(
                lot["wafer_count"]
            ),

            "average_yield": round(
                float(
                    lot["average_yield"]
                ),
                6
            ),

            "average_defect_count": round(
                float(
                    lot["average_defect_count"]
                ),
                2
            ),

            "average_defect_density": round(
                float(
                    lot["average_defect_density"]
                ),
                4
            )
        })

    return result


# =========================================================
# Tool Analysis
# =========================================================

def get_tool_analysis():
    """
    Get yield and defect performance by manufacturing tool.

    Each tool category is deterministically sorted from
    lowest average yield to highest average yield.
    """

    response = requests.get(
        f"{API_BASE_URL}/analytics/tools",
        timeout=5
    )

    response.raise_for_status()

    data = response.json()

    result = {}

    for tool_type, tools in data.items():

        # Deterministic ranking
        sorted_tools = sorted(
            tools,
            key=lambda x: float(
                x["average_yield"]
            )
        )

        formatted_tools = []

        for tool in sorted_tools:

            formatted_tools.append({
                tool_type: str(
                    tool[tool_type]
                ),

                "wafer_count": int(
                    tool["wafer_count"]
                ),

                "average_yield": round(
                    float(
                        tool["average_yield"]
                    ),
                    6
                ),

                "average_defect_density": round(
                    float(
                        tool["average_defect_density"]
                    ),
                    4
                )
            })

        result[tool_type] = (
            formatted_tools
        )

    return result


# =========================================================
# Traceability
# =========================================================

def get_traceability(
    lot_id,
    wafer_id
):
    """
    Get the production traceability record
    for a specific wafer.
    """

    response = requests.get(
        f"{API_BASE_URL}/traceability/{lot_id}/{wafer_id}",
        timeout=5
    )

    if response.status_code == 404:

        return {
            "error":
                "No matching production data was found."
        }

    response.raise_for_status()

    return response.json()


# =========================================================
# Yield Factor Analysis
# =========================================================

def get_yield_factor_analysis():
    """
    Compare low-yield and high-yield wafers
    and return manufacturing features with
    the largest standardized differences.
    """

    response = requests.get(
        f"{API_BASE_URL}/analytics/yield-factors",
        timeout=5
    )

    response.raise_for_status()

    data = response.json()

    result = {
        "low_yield_threshold": round(
            float(
                data["low_yield_threshold"]
            ),
            6
        ),

        "high_yield_threshold": round(
            float(
                data["high_yield_threshold"]
            ),
            6
        ),

        "top_factors": []
    }

    factors = sorted(
        data["top_factors"],
        key=lambda x: float(
            x["absolute_standardized_difference"]
        ),
        reverse=True
    )

    for factor in factors:

        result["top_factors"].append({
            "feature": str(
                factor["feature"]
            ),

            "low_yield_mean": round(
                float(
                    factor["low_yield_mean"]
                ),
                4
            ),

            "high_yield_mean": round(
                float(
                    factor["high_yield_mean"]
                ),
                4
            ),

            "standardized_difference": round(
                float(
                    factor["standardized_difference"]
                ),
                4
            ),

            "absolute_standardized_difference": round(
                float(
                    factor[
                        "absolute_standardized_difference"
                    ]
                ),
                4
            )
        })

    return result