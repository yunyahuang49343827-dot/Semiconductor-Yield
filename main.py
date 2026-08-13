#Step 6 — FastAPI

import pandas as pd
from fastapi import FastAPI, HTTPException

from traceability import get_traceability


app = FastAPI(
    title="Smart Manufacturing AI Analytics & Traceability Copilot"
)


# Load dataset once when the API starts
df = pd.read_csv(
    "semiconductor_yield_forecasting_data.csv"
)

df["process_date"] = pd.to_datetime(
    df["process_date"],
    errors="coerce"
)


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }

#What is the overall manufacturing performance? 
@app.get("/analytics/overview")
def get_factory_overview():

    return {
        "total_wafers": len(df),
        "total_lots": int(df["lot_id"].nunique()),
        "average_yield": float(df["yield"].mean()),
        "average_defect_count": float(df["defect_count"].mean()),
        "average_defect_density": float(df["defect_density"].mean())
    }

#Which lots have the lowest yield?
@app.get("/analytics/lots")
def get_lot_analysis():

    lot_summary = (
        df.groupby("lot_id")
        .agg(
            wafer_count=("wafer_id", "count"),
            average_yield=("yield", "mean"),
            average_defect_count=("defect_count", "mean"),
            average_defect_density=("defect_density", "mean")
        )
        .reset_index()
        .sort_values(
            by="average_yield",
            ascending=True
        )
    )

    return lot_summary.to_dict(
        orient="records"
    )



@app.get("/analytics/tools")
def get_tool_analysis():

    tool_columns = [
        "etch_tool",
        "litho_tool",
        "deposition_tool",
        "implant_tool"
    ]

    result = {}

    for tool_column in tool_columns:

        tool_summary = (
            df.groupby(tool_column)
            .agg(
                wafer_count=("wafer_id", "count"),
                average_yield=("yield", "mean"),
                average_defect_density=(
                    "defect_density",
                    "mean"
                )
            )
            .reset_index()
            .sort_values(
                by="average_yield",
                ascending=True
            )
        )

        result[tool_column] = (
            tool_summary.to_dict(
                orient="records"
            )
        )

    return result

@app.get("/analytics/yield-factors")
def get_yield_factor_analysis():

    numerical_columns = [
        "etch_rate",
        "pressure",
        "temperature",
        "exposure_time",
        "focus_offset",
        "dose",
        "deposition_rate",
        "thickness_uniformity",
        "implant_energy",
        "tilt_angle",
        "critical_dimension",
        "oxide_thickness",
        "resistivity",
        "defect_count",
        "defect_density",
        "vth",
        "leakage_current",
        "resistance"
    ]

    low_threshold = df["yield"].quantile(0.25)
    high_threshold = df["yield"].quantile(0.75)

    low_group = df[
        df["yield"] <= low_threshold
    ]

    high_group = df[
        df["yield"] >= high_threshold
    ]

    low_mean = low_group[numerical_columns].mean()
    high_mean = high_group[numerical_columns].mean()

    low_std = low_group[numerical_columns].std()
    high_std = high_group[numerical_columns].std()

    pooled_std = (
        (
            low_std ** 2
            + high_std ** 2
        ) / 2
    ) ** 0.5

    standardized_difference = (
        (low_mean - high_mean)
        / pooled_std
    )

    result = []

    for feature in numerical_columns:

        result.append({
            "feature": feature,
            "low_yield_mean": float(
                low_mean[feature]
            ),
            "high_yield_mean": float(
                high_mean[feature]
            ),
            "standardized_difference": float(
                standardized_difference[feature]
            ),
            "absolute_standardized_difference": float(
                abs(
                    standardized_difference[feature]
                )
            )
        })

    result = sorted(
        result,
        key=lambda x:
            x["absolute_standardized_difference"],
        reverse=True
    )

    return {
        "low_yield_threshold": float(
            low_threshold
        ),
        "high_yield_threshold": float(
            high_threshold
        ),
        "top_factors": result[:5]
    }


@app.get("/traceability/{lot_id}/{wafer_id}")
def traceability(lot_id: str, wafer_id: str):

    result = get_traceability(
        df,
        lot_id,
        wafer_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No matching production data was found."
        )

    return result