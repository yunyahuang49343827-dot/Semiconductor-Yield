#Step 1A — 載入 Dataset
import pandas as pd

file_path = "/Users/sleep/深度學習/Semiconductor Yield/semiconductor_yield_forecasting_data.csv"

df = pd.read_csv(file_path)

print("Dataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 Rows:")
print(df.head())

#Step 1B：Data Types + Missing Values + Duplicates + Unique Key 檢查

print("\n=== Data Types ===")
print(df.dtypes)

print("\n=== Missing Values ===")
print(df.isnull().sum())

print("\n=== Duplicate Rows ===")
duplicate_rows = df.duplicated().sum()
print(duplicate_rows)

print("\n=== Duplicate Lot + Wafer IDs ===")
duplicate_keys = df.duplicated(
    subset=["lot_id", "wafer_id"]
).sum()

print(duplicate_keys)

print("\n=== Unique Lots ===")
print(df["lot_id"].nunique())

print("\n=== Unique Wafer IDs ===")
print(df["wafer_id"].nunique())

print("\n=== Unique Lot + Wafer Combinations ===")
unique_records = (
    df[["lot_id", "wafer_id"]]
    .drop_duplicates()
    .shape[0]
)

print(unique_records)

#lot_id + wafer_id 可以當作這份 dataset 的 composite key

#Step 1C — 看懂 Categorical / Numerical Variables
#我們要把欄位分成兩類：
#1. Categorical variables：像 Product、Technology Node、Tool
#2. Numerical variables：像 pressure、temperature、defect_density、yield
#然後檢查每個 manufacturing dimension 有哪些值、各自有多少筆資料

print("\n=== Categorical Columns ===")

categorical_columns = [
    "lot_id",
    "wafer_id",
    "product_type",
    "technology_node",
    "process_date",
    "etch_tool",
    "litho_tool",
    "deposition_tool",
    "implant_tool"
]

for column in categorical_columns:
    print(f"\n--- {column} ---")
    print("Unique values:", df[column].nunique())
    print(df[column].value_counts().head(10))

#接著加入 numerical columns：
print("\n=== Numerical Columns Summary ===")

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
    "resistance",
    "yield"
]

print(df[numerical_columns].describe().T)


#value_counts() 是什麼？每個 product type 各有幾筆 wafer？
#describe() 在看什麼？快速看數值欄位


#Step 1D — Data Quality Sanity Check
#先做日期轉換
print("\n=== Convert process_date to datetime ===")

df["process_date"] = pd.to_datetime(
    df["process_date"],
    errors="coerce"
)

print(df["process_date"].dtype)

invalid_dates = df["process_date"].isnull().sum()

print("Invalid dates:", invalid_dates)

print("Earliest date:", df["process_date"].min())
print("Latest date:", df["process_date"].max())


#2. 檢查 Yield
print("\n=== Yield Validation ===")

print("Minimum yield:", df["yield"].min())
print("Maximum yield:", df["yield"].max())

invalid_yield = df[
    (df["yield"] < 0) |
    (df["yield"] > 1)
]

print("Invalid yield records:", len(invalid_yield))


#3. 檢查 Defect Values
print("\n=== Defect Validation ===")

negative_defect_count = df[
    df["defect_count"] < 0
]

negative_defect_density = df[
    df["defect_density"] < 0
]

print(
    "Negative defect_count records:",
    len(negative_defect_count)
)

print(
    "Negative defect_density records:",
    len(negative_defect_density)
)

#4. 檢查 Tool Category Consistency
tool_columns = [
    "etch_tool",
    "litho_tool",
    "deposition_tool",
    "implant_tool"
]

print("\n=== Tool Category Check ===")

for column in tool_columns:
    print(f"\n{column}:")
    print(sorted(df[column].unique()))


#5. 檢查數值範圍
print("\n=== Numerical Range Check ===")

for column in numerical_columns:
    print(
        f"{column}: "
        f"min={df[column].min():.4f}, "
        f"max={df[column].max():.4f}"
    )


#Step 2A — Factory KPI Overview + Lot Yield Analysis。

#1. Overall Yield
print("\n=== Factory Overview ===")

total_wafers = len(df)

overall_yield = df["yield"].mean()

print("Total Wafers:", total_wafers)
print(f"Overall Yield: {overall_yield:.2%}")

#3. Yield by Lot
#接著開始做 Lot Analysis。
print("\n=== Yield by Lot ===")

lot_yield = (
    df.groupby("lot_id")["yield"]
    .mean()
    .reset_index()
)

lot_yield = lot_yield.rename(
    columns={
        "yield": "average_yield"
    }
)

print(lot_yield.head())

#4. 找 Lowest Yield Lots
print("\n=== Lowest Yield Lots ===")

lowest_yield_lots = (
    lot_yield
    .sort_values(
        by="average_yield",
        ascending=True
    )
    .head(5)
)

print(lowest_yield_lots)

#5. 現在加入 Defect 資訊
#Low-yield Lot 是否同時有比較高的 defect metrics？
print("\n=== Lot KPI Summary ===")

lot_summary = (
    df.groupby("lot_id")
    .agg(
        wafer_count=("wafer_id", "count"),
        average_yield=("yield", "mean"),
        average_defect_count=("defect_count", "mean"),
        average_defect_density=("defect_density", "mean")
    )
    .reset_index()
)

lot_summary = lot_summary.sort_values(
    by="average_yield",
    ascending=True
)

print(lot_summary.head(5))


#Step 2B — Yield by Product / Technology Node / Date

#1. Yield by Product
print("\n=== Yield by Product Type ===")

product_summary = (
    df.groupby("product_type")
    .agg(
        wafer_count=("wafer_id", "count"),
        average_yield=("yield", "mean"),
        average_defect_density=("defect_density", "mean")
    )
    .reset_index()
    .sort_values(
        by="average_yield",
        ascending=True
    )
)

print(product_summary)

#2. Yield by Technology Node
print("\n=== Yield by Technology Node ===")

node_summary = (
    df.groupby("technology_node")
    .agg(
        wafer_count=("wafer_id", "count"),
        average_yield=("yield", "mean"),
        average_defect_density=("defect_density", "mean")
    )
    .reset_index()
    .sort_values(
        by="average_yield",
        ascending=True
    )
)

print(node_summary)

#4. Yield by Process Date
print("\n=== Yield by Process Date ===")

date_summary = (
    df.groupby("process_date")
    .agg(
        wafer_count=("wafer_id", "count"),
        average_yield=("yield", "mean"),
        average_defect_density=("defect_density", "mean")
    )
    .reset_index()
    .sort_values(
        by="process_date",
        ascending=True
    )
)

print(date_summary.head())

#5. 找 Yield 最差的日期
print("\n=== Lowest Yield Dates ===")

lowest_yield_dates = (
    date_summary
    .sort_values(
        by="average_yield",
        ascending=True
    )
    .head(5)
)

print(lowest_yield_dates)


#Step 3 — Tool Analysis
#Which manufacturing tools are associated with lower yield?
print("\n=== Tool Analysis ===")

tool_columns = [
    "etch_tool",
    "litho_tool",
    "deposition_tool",
    "implant_tool"
]

for tool_column in tool_columns:

    print(f"\n=== {tool_column} ===")

    tool_summary = (
        df.groupby(tool_column)
        .agg(
            wafer_count=("wafer_id", "count"),
            average_yield=("yield", "mean"),
            average_defect_density=("defect_density", "mean")
        )
        .reset_index()
        .sort_values(
            by="average_yield",
            ascending=True
        )
    )

    # 讓 yield 額外顯示成百分比，方便閱讀
    tool_summary["yield_percent"] = (
        tool_summary["average_yield"] * 100
    ).round(2)

    print(
        tool_summary[
            [
                tool_column,
                "wafer_count",
                "yield_percent",
                "average_defect_density"
            ]
        ]
    )

#每台 Tool 到底處理哪些 Technology Node？

#先只檢查 Etch Tool，避免一次寫太多。
print("\n=== Etch Tool vs Technology Node ===")

etch_node_table = pd.crosstab(
    df["etch_tool"],
    df["technology_node"]
)

print(etch_node_table)


#在相同 Technology Node 裡，不同 Etch Tool 的 Yield 還有沒有差異？
print("\n=== Yield by Technology Node and Etch Tool ===")

node_etch_yield = (
    df.groupby(
        ["technology_node", "etch_tool"]
    )
    .agg(
        wafer_count=("wafer_id", "count"),
        average_yield=("yield", "mean")
    )
    .reset_index()
)

node_etch_yield["yield_percent"] = (
    node_etch_yield["average_yield"] * 100
).round(2)

print(
    node_etch_yield[
        [
            "technology_node",
            "etch_tool",
            "wafer_count",
            "yield_percent"
        ]
    ].sort_values(
        ["technology_node", "yield_percent"]
    )
)

#Step 4 — Process Investigation
print("\n=== Low vs High Yield Investigation ===")

low_threshold = df["yield"].quantile(0.25)
high_threshold = df["yield"].quantile(0.75)

low_yield_group = df[
    df["yield"] <= low_threshold
]

high_yield_group = df[
    df["yield"] >= high_threshold
]

print(f"Low Yield Threshold: {low_threshold:.2%}")
print(f"High Yield Threshold: {high_threshold:.2%}")

print("Low Yield Wafers:", len(low_yield_group))
print("High Yield Wafers:", len(high_yield_group))

#2. 比較 Process / Quality Features
investigation_columns = [
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

comparison = pd.DataFrame({
    "low_yield_mean":
        low_yield_group[investigation_columns].mean(),

    "high_yield_mean":
        high_yield_group[investigation_columns].mean()
})

comparison["difference"] = (
    comparison["low_yield_mean"]
    - comparison["high_yield_mean"]
)

print("\n=== Low vs High Yield Comparison ===")
print(comparison)

#5. 建議再加入標準化差異
import numpy as np

low_std = low_yield_group[investigation_columns].std()
high_std = high_yield_group[investigation_columns].std()

pooled_std = np.sqrt(
    (
        low_std ** 2
        + high_std ** 2
    ) / 2
)

comparison["standardized_difference"] = (
    comparison["difference"]
    / pooled_std
)

comparison["absolute_standardized_difference"] = (
    comparison["standardized_difference"].abs()
)

comparison = comparison.sort_values(
    by="absolute_standardized_difference",
    ascending=False
)

print(
    comparison[
        [
            "low_yield_mean",
            "high_yield_mean",
            "standardized_difference"
        ]
    ].head(10)
)


#Step 5 — Traceability
#給我某一個 Lot + Wafer，我能不能快速把它的產品、設備、製程條件、品質量測與 Yield 全部查出來？

from traceability import get_traceability

trace = get_traceability(

    df,

    "LOT_0024",

    "W001"

)

print("\n=== Traceability Result ===")

print(trace)


