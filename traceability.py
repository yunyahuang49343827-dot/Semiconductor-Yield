def get_traceability(df, lot_id, wafer_id):
    result = df[
        (df["lot_id"] == lot_id) &
        (df["wafer_id"] == wafer_id)
    ]

    if result.empty:
        return None

    row = result.iloc[0]

    return {
        "lot_id": str(row["lot_id"]),
        "wafer_id": str(row["wafer_id"]),

        "product": {
            "product_type": str(row["product_type"]),
            "technology_node": str(row["technology_node"]),
            "process_date": str(row["process_date"].date())
        },

        "tools": {
            "etch_tool": str(row["etch_tool"]),
            "litho_tool": str(row["litho_tool"]),
            "deposition_tool": str(row["deposition_tool"]),
            "implant_tool": str(row["implant_tool"])
        },

        "process_parameters": {
            "etch_rate": round(float(row["etch_rate"]), 4),
            "pressure": round(float(row["pressure"]), 4),
            "temperature": round(float(row["temperature"]), 4),
            "exposure_time": round(float(row["exposure_time"]), 4),
            "focus_offset": round(float(row["focus_offset"]), 4),

            # Keep original magnitude.
            # Do not infer or add units.
            "dose": float(row["dose"]),

            "deposition_rate": round(
                float(row["deposition_rate"]),
                4
            ),

            "thickness_uniformity": round(
                float(row["thickness_uniformity"]),
                4
            ),

            "implant_energy": round(
                float(row["implant_energy"]),
                4
            ),

            "tilt_angle": round(
                float(row["tilt_angle"]),
                4
            )
        },

        "quality_measurements": {
            "critical_dimension": round(
                float(row["critical_dimension"]),
                4
            ),

            "oxide_thickness": round(
                float(row["oxide_thickness"]),
                4
            ),

            "resistivity": round(
                float(row["resistivity"]),
                4
            ),

            "vth": round(
                float(row["vth"]),
                4
            ),

            "leakage_current": round(
                float(row["leakage_current"]),
                8
            ),

            "resistance": round(
                float(row["resistance"]),
                4
            )
        },

        "defects": {
            "defect_count": int(
                row["defect_count"]
            ),

            "defect_density": round(
                float(row["defect_density"]),
                4
            )
        },

        # Keep yield as decimal in backend.
        # Presentation layer may display it as percentage.
        "yield": round(
            float(row["yield"]),
            6
        )
    }