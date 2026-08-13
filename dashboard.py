import pandas as pd
import requests
import streamlit as st

from local_agent import ask_factory_agent


API_BASE_URL = "http://127.0.0.1:8000"


# =========================================================
# Page Config
# =========================================================

st.set_page_config(
    page_title="Smart Manufacturing Copilot",
    layout="wide"
)


# =========================================================
# Language
# =========================================================

language = st.sidebar.radio(
    "Language / 語言",
    ["English", "中文"]
)

is_zh = language == "中文"


TEXT = {
    "title": {
        "en": "Smart Manufacturing AI Analytics & Traceability Copilot",
        "zh": "智慧製造 AI 分析與追溯 Copilot"
    },
    "caption": {
        "en": "Yield Analytics · Tool Analysis · Traceability · FastAPI",
        "zh": "良率分析 · 設備分析 · 製程追溯 · FastAPI"
    },
    "overview": {
        "en": "Factory Overview",
        "zh": "工廠總覽"
    },
    "total_wafers": {
        "en": "Total Wafers",
        "zh": "Wafer 總數"
    },
    "average_yield": {
        "en": "Average Yield",
        "zh": "平均良率"
    },
    "defect_density": {
        "en": "Average Defect Density",
        "zh": "平均缺陷密度"
    },
    "low_yield_lots": {
        "en": "Low-Yield Lots",
        "zh": "低良率 Lot"
    },
    "tool_performance": {
        "en": "Tool Performance",
        "zh": "設備表現"
    },
    "select_tool": {
        "en": "Select Tool Type",
        "zh": "選擇設備類型"
    },
    "traceability": {
        "en": "Wafer Traceability",
        "zh": "Wafer 製程追溯"
    },
    "lot_id": {
        "en": "Lot ID",
        "zh": "Lot ID"
    },
    "wafer_id": {
        "en": "Wafer ID",
        "zh": "Wafer ID"
    },
    "search_traceability": {
        "en": "Search Traceability",
        "zh": "查詢製程追溯"
    },
    "record_found": {
        "en": "Production record found.",
        "zh": "已找到製造紀錄。"
    },
    "wafer_yield": {
        "en": "Wafer Yield",
        "zh": "Wafer 良率"
    },
    "product": {
        "en": "Product",
        "zh": "產品資訊"
    },
    "tools": {
        "en": "Tools",
        "zh": "設備資訊"
    },
    "process_parameters": {
        "en": "Process Parameters",
        "zh": "製程參數"
    },
    "quality_measurements": {
        "en": "Quality Measurements",
        "zh": "品質量測"
    },
    "defects": {
        "en": "Defects",
        "zh": "缺陷資訊"
    },
    "no_record": {
        "en": "No matching production data was found.",
        "zh": "找不到符合條件的製造資料。"
    },
    "copilot": {
        "en": "AI Manufacturing Copilot",
        "zh": "AI 製造分析 Copilot"
    },
    "copilot_caption": {
        "en": "Local Qwen 3.5 9B · Function Calling · FastAPI",
        "zh": "Local Qwen 3.5 9B · Function Calling · FastAPI"
    },
    "suggested_questions": {
        "en": "Suggested Questions",
        "zh": "建議問題"
    },
    "ask_copilot": {
        "en": "Ask the Copilot",
        "zh": "詢問 Copilot"
    },
    "ask_button": {
        "en": "Ask Copilot",
        "zh": "送出問題"
    },
    "copilot_response": {
        "en": "Copilot Response",
        "zh": "Copilot 回覆"
    },
    "empty_question": {
        "en": "Please enter a manufacturing question.",
        "zh": "請輸入製造相關問題。"
    },
    "analyzing": {
        "en": "Local AI Agent is analyzing factory data...",
        "zh": "Local AI Agent 正在分析工廠資料..."
    },
    "api_error": {
        "en": "Cannot connect to the FastAPI backend.",
        "zh": "無法連線至 FastAPI 後端。"
    }
}


def t(key):
    return TEXT[key]["zh" if is_zh else "en"]


# =========================================================
# Title
# =========================================================

st.title(t("title"))

st.caption(
    t("caption")
)


# =========================================================
# Factory Overview
# =========================================================

st.header(t("overview"))

try:
    response = requests.get(
        f"{API_BASE_URL}/analytics/overview",
        timeout=5
    )

    response.raise_for_status()
    overview = response.json()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        t("total_wafers"),
        overview["total_wafers"]
    )

    col2.metric(
        t("average_yield"),
        f'{overview["average_yield"]:.2%}'
    )

    col3.metric(
        t("defect_density"),
        f'{overview["average_defect_density"]:.3f}'
    )

except requests.RequestException:
    st.error(
        t("api_error")
    )


# =========================================================
# Low-Yield Lots
# =========================================================

st.header(t("low_yield_lots"))

try:
    response = requests.get(
        f"{API_BASE_URL}/analytics/lots",
        timeout=5
    )

    response.raise_for_status()

    lots = pd.DataFrame(
        response.json()
    )

    lots["yield_percent"] = (
        lots["average_yield"] * 100
    ).round(2)

    display_lots = lots[
        [
            "lot_id",
            "wafer_count",
            "yield_percent",
            "average_defect_density"
        ]
    ].head(10)

    st.dataframe(
        display_lots,
        use_container_width=True,
        hide_index=True
    )

except requests.RequestException:
    st.error(
        t("api_error")
    )


# =========================================================
# Tool Performance
# =========================================================

st.header(t("tool_performance"))

tool_type = st.selectbox(
    t("select_tool"),
    [
        "etch_tool",
        "litho_tool",
        "deposition_tool",
        "implant_tool"
    ]
)

try:
    response = requests.get(
        f"{API_BASE_URL}/analytics/tools",
        timeout=5
    )

    response.raise_for_status()

    tools = response.json()

    tool_df = pd.DataFrame(
        tools[tool_type]
    )

    tool_df["yield_percent"] = (
        tool_df["average_yield"] * 100
    ).round(2)

    st.dataframe(
        tool_df[
            [
                tool_type,
                "wafer_count",
                "yield_percent",
                "average_defect_density"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

except requests.RequestException:
    st.error(
        t("api_error")
    )


# =========================================================
# Traceability
# =========================================================

st.header(t("traceability"))

col1, col2 = st.columns(2)

with col1:
    lot_id = st.text_input(
        t("lot_id"),
        value="LOT_0024"
    )

with col2:
    wafer_id = st.text_input(
        t("wafer_id"),
        value="W001"
    )


if st.button(
    t("search_traceability"),
    use_container_width=True
):

    try:
        response = requests.get(
            f"{API_BASE_URL}/traceability/{lot_id}/{wafer_id}",
            timeout=5
        )

        if response.status_code == 200:

            traceability = response.json()

            st.success(
                t("record_found")
            )

            st.metric(
                t("wafer_yield"),
                f'{traceability["yield"]:.2%}'
            )

            st.subheader(
                t("product")
            )

            st.json(
                traceability["product"]
            )

            st.subheader(
                t("tools")
            )

            st.json(
                traceability["tools"]
            )

            st.subheader(
                t("process_parameters")
            )

            st.json(
                traceability["process_parameters"]
            )

            st.subheader(
                t("quality_measurements")
            )

            st.json(
                traceability["quality_measurements"]
            )

            st.subheader(
                t("defects")
            )

            st.json(
                traceability["defects"]
            )

        elif response.status_code == 404:

            st.warning(
                t("no_record")
            )

        else:

            st.error(
                t("api_error")
            )

    except requests.RequestException:

        st.error(
            t("api_error")
        )


# =========================================================
# AI Manufacturing Copilot
# =========================================================

st.header(
    t("copilot")
)

st.caption(
    t("copilot_caption")
)


if is_zh:

    suggested_questions = [
        "目前整體工廠平均良率是多少？",

        "良率最低的三個 Lot 是哪些？",

        "哪些蝕刻設備的平均良率最低？",

        (
            "請顯示 LOT_0024 中 W001 "
            "這片 Wafer 的製造與追溯資料。"
        ),

        (
            "根據良率表現，哪些設備應優先進一步調查？"
        ),

        (
            "低良率與高良率 Wafer 之間，"
            "哪些製造特徵的差異最大？"
        )
    ]

else:

    suggested_questions = [
        "What is the current overall factory yield?",

        "Which three lots have the lowest yield?",

        "Which etch tools have the lowest yield?",

        (
            "Show me the manufacturing record "
            "for LOT_0024 wafer W001."
        ),

        (
            "Which tools should be investigated "
            "based on yield performance?"
        ),

        (
            "What manufacturing factors differ most "
            "between low-yield and high-yield wafers?"
        )
    ]


# =========================================================
# Session State
# =========================================================

if "copilot_input" not in st.session_state:
    st.session_state.copilot_input = ""


st.subheader(
    t("suggested_questions")
)


# =========================================================
# Suggested Question Buttons
# =========================================================

col1, col2, col3 = st.columns(3)


with col1:

    if st.button(
        "整體良率"
        if is_zh
        else "Overall Yield",
        use_container_width=True
    ):
        st.session_state.copilot_input = (
            suggested_questions[0]
        )

    if st.button(
        "Wafer 追溯"
        if is_zh
        else "Wafer Traceability",
        use_container_width=True
    ):
        st.session_state.copilot_input = (
            suggested_questions[3]
        )


with col2:

    if st.button(
        "最低良率 Lot"
        if is_zh
        else "Lowest Yield Lots",
        use_container_width=True
    ):
        st.session_state.copilot_input = (
            suggested_questions[1]
        )

    if st.button(
        "可疑設備"
        if is_zh
        else "Suspicious Tools",
        use_container_width=True
    ):
        st.session_state.copilot_input = (
            suggested_questions[4]
        )


with col3:

    if st.button(
        "蝕刻設備表現"
        if is_zh
        else "Etch Tool Performance",
        use_container_width=True
    ):
        st.session_state.copilot_input = (
            suggested_questions[2]
        )

    if st.button(
        "低良率因素"
        if is_zh
        else "Low-Yield Factors",
        use_container_width=True
    ):
        st.session_state.copilot_input = (
            suggested_questions[5]
        )


# =========================================================
# Copilot Input
# =========================================================

question = st.text_area(
    t("ask_copilot"),
    key="copilot_input",
    height=100,
    placeholder=(
        "請詢問良率、Lot、設備、追溯或製造因素..."
        if is_zh
        else
        "Ask about yield, lots, tools, "
        "traceability, or manufacturing factors..."
    )
)


# =========================================================
# Ask Copilot
# =========================================================

if st.button(
    t("ask_button"),
    type="primary",
    use_container_width=True
):

    if not question.strip():

        st.warning(
            t("empty_question")
        )

    else:

        with st.spinner(
            t("analyzing")
        ):

            try:

                answer = ask_factory_agent(
                    question,
                    language=language
                )

                st.subheader(
                    t("copilot_response")
                )

                st.markdown(
                    answer
                )

            except Exception as error:

                st.error(
                    f"Copilot error: {error}"
                )