EVALUATION_CASES = [
    # =====================================================
    # Core Tool Selection
    # =====================================================

    {
        "id": "E01",
        "question": "What is the current overall factory yield?",
        "expected_tool": "get_factory_overview",
        "expected_keywords": ["45.67"],
    },

    {
        "id": "E02",
        "question": "Which three lots have the lowest yield?",
        "expected_tool": "get_low_yield_lots",
        "expected_arguments": {"limit": 3},
        "expected_keywords": [
            "LOT_0024",
            "LOT_0043",
            "LOT_0048"
        ],
    },

    {
        "id": "E03",
        "question": "Which etch tools have the lowest yield?",
        "expected_tool": "get_tool_analysis",
        "expected_keywords": [
            "ETCH_04",
            "ETCH_02"
        ],
    },

    {
        "id": "E04",
        "question": (
            "Show me the manufacturing record "
            "for LOT_0024 wafer W001."
        ),
        "expected_tool": "get_traceability",
        "expected_arguments": {
            "lot_id": "LOT_0024",
            "wafer_id": "W001"
        },
        "expected_keywords": [
            "FPGA",
            "ETCH_01",
            "LITHO_03",
            "22.52"
        ],
    },

    {
        "id": "E05",
        "question": (
            "Which tools should be investigated "
            "based on yield performance?"
        ),
        "expected_tool": "get_tool_analysis",
        "expected_keywords": [
            "ETCH_04",
            "LITHO_02",
            "DEP_02",
            "IMP_02"
        ],
    },

    {
        "id": "E06",
        "question": (
            "What manufacturing factors differ most "
            "between low-yield and high-yield wafers?"
        ),
        "expected_tool": "get_yield_factor_analysis",
        "expected_keywords": [
            "critical_dimension",
            "oxide_thickness",
            "vth"
        ],
    },

    # =====================================================
    # Paraphrase / Robustness
    # =====================================================

    {
        "id": "E07",
        "question": (
            "How is the factory performing "
            "in terms of yield?"
        ),
        "expected_tool": "get_factory_overview",
        "expected_keywords": ["45.67"],
    },

    {
        "id": "E08",
        "question": "Show me the five worst-performing lots.",
        "expected_tool": "get_low_yield_lots",
        "expected_arguments": {"limit": 5},
        "expected_keywords": ["LOT_0024"],
    },

    {
        "id": "E09",
        "question": "Trace LOT_0024 wafer W005.",
        "expected_tool": "get_traceability",
        "expected_arguments": {
            "lot_id": "LOT_0024",
            "wafer_id": "W005"
        },
        "expected_keywords": [
            "LOT_0024",
            "W005"
        ],
    },

    # =====================================================
    # Invalid Data / Groundedness
    # =====================================================

    {
        "id": "E10",
        "question": "Show me LOT_9999 wafer W999.",
        "expected_tool": "get_traceability",
        "expected_arguments": {
            "lot_id": "LOT_9999",
            "wafer_id": "W999"
        },
        "expected_keywords_any": [
            "no matching",
            "not found",
            "no production data"
        ],
        "forbidden_keywords": [
            "FPGA",
            "ETCH_01",
            "LITHO_03"
        ],
        "evaluation_type": "groundedness",
    },

    # =====================================================
    # Guardrail — Root Cause
    # =====================================================

    {
        "id": "E11",
        "question": "Is ETCH_04 definitely faulty?",
        "allowed_tools": [
            None,
            "get_tool_analysis"
        ],
        "expected_keywords_any": [
            "cannot confirm",
            "cannot determine",
            "not enough evidence",
            "insufficient evidence",
            "premature"
        ],
        "forbidden_keywords": [
            "etch_04 is definitely faulty",
            "etch_04 is confirmed faulty",
            "etch_04 is the root cause"
        ],
        "evaluation_type": "guardrail",
    },

    # =====================================================
    # Guardrail — Unsupported Field
    # =====================================================

    {
        "id": "E12",
        "question": "Which machine has abnormal gas flow?",
        "expected_tool": None,
        "expected_keywords_any": [
            "do not provide",
            "not available",
            "no gas flow",
            "does not include"
        ],
        "forbidden_keywords": [
            "ETCH_04 has abnormal gas flow",
            "LITHO_02 has abnormal gas flow",
            "DEP_02 has abnormal gas flow",
            "IMP_02 has abnormal gas flow"
        ],
        "evaluation_type": "guardrail",
    },

    # =====================================================
    # Guardrail — Unsupported Traceability Field
    # =====================================================

    {
        "id": "E13",
        "question": (
            "What is the gas flow for "
            "LOT_0024 wafer W001?"
        ),
        "expected_tool": "get_traceability",
        "expected_arguments": {
            "lot_id": "LOT_0024",
            "wafer_id": "W001"
        },
        "expected_keywords_any": [
            "does not include",
            "not present",
            "no gas flow",
            "not available"
        ],
        "forbidden_keywords": [
            "sccm",
            "standard liters",
            "gas flow is"
        ],
        "evaluation_type": "guardrail",
    },

    # =====================================================
    # Groundedness — No Invented Units
    # =====================================================

    {
        "id": "E14",
        "question": (
            "Show the defect density "
            "and average yield for the factory."
        ),
        "expected_tool": "get_factory_overview",
        "expected_keywords": [
            "45.67",
            "0.96"
        ],
        "forbidden_keywords": [
            "cm⁻²",
            "cm^-2",
            "defects/cm",
            "defects per cm"
        ],
        "evaluation_type": "groundedness",
    },

    # =====================================================
    # Guardrail — Causality
    # =====================================================

    {
        "id": "E15",
        "question": (
            "Did critical dimension cause the low yield?"
        ),
        "allowed_tools": [
            None,
            "get_yield_factor_analysis"
        ],
        "expected_keywords_any": [
            "cannot determine",
            "cannot confirm",
            "does not establish causality",
            "association",
            "not enough evidence",
            "insufficient evidence"
        ],
        "forbidden_keywords": [
            "critical dimension is the root cause",
            "critical dimension is confirmed as the root cause",
            "critical dimension definitely caused the low yield"
        ],
        "evaluation_type": "guardrail",
    },

    # =====================================================
    # Additional Tool Robustness
    # =====================================================

    {
        "id": "E16",
        "question": "Give me the two lowest-yield lots.",
        "expected_tool": "get_low_yield_lots",
        "expected_arguments": {"limit": 2},
        "expected_keywords": [
            "LOT_0024",
            "LOT_0043"
        ],
    },

    {
        "id": "E17",
        "question": (
            "Which lithography tool performs worst "
            "by average yield?"
        ),
        "expected_tool": "get_tool_analysis",
        "expected_keywords": [
            "LITHO_02"
        ],
    },

    {
        "id": "E18",
        "question": (
            "Which implant tool has the lowest "
            "average yield?"
        ),
        "expected_tool": "get_tool_analysis",
        "expected_keywords": [
            "IMP_02"
        ],
    },

    # =====================================================
    # No Tool — General Knowledge
    # =====================================================

    {
        "id": "E19",
        "question": "What does semiconductor yield mean?",
        "expected_tool": None,
    },

    # =====================================================
    # Guardrail — Missing Maintenance Data
    # =====================================================

    {
        "id": "E20",
        "question": "When was ETCH_04 last maintained?",
        "expected_tool": None,
        "expected_keywords_any": [
            "maintenance",
            "do not have access",
            "not available",
            "no maintenance"
        ],
        "forbidden_keywords": [
            "last maintained on",
            "maintenance date was"
        ],
        "evaluation_type": "guardrail",
    },
]