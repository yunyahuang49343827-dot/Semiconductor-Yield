#建立測試檔 

from agent_tools import (
    get_factory_overview,
    get_low_yield_lots,
    get_tool_analysis,
    get_traceability
)


print("\n=== Factory Overview ===")
print(
    get_factory_overview()
)


print("\n=== Lowest Yield Lots ===")
print(
    get_low_yield_lots(3)
)


print("\n=== Tool Analysis ===")
tools = get_tool_analysis()

print(
    tools["etch_tool"]
)


print("\n=== Traceability ===")
print(
    get_traceability(
        "LOT_0024",
        "W001"
    )
)


print("\n=== Invalid Traceability ===")
print(
    get_traceability(
        "LOT_9999",
        "W999"
    )
)





