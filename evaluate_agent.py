from evaluation_cases import EVALUATION_CASES
from local_agent import ask_factory_agent


def normalize_arguments(arguments):
    normalized = {}

    for key, value in arguments.items():

        if isinstance(value, str):
            stripped = value.strip()

            if stripped.isdigit():
                normalized[key] = int(stripped)
            else:
                normalized[key] = stripped

        else:
            normalized[key] = value

    return normalized


def contains_all_keywords(answer, keywords):
    if not keywords:
        return True

    answer_lower = answer.lower()

    return all(
        keyword.lower() in answer_lower
        for keyword in keywords
    )


def contains_any_keyword(answer, keywords):
    if not keywords:
        return True

    answer_lower = answer.lower()

    return any(
        keyword.lower() in answer_lower
        for keyword in keywords
    )


def avoids_forbidden_keywords(answer, keywords):
    if not keywords:
        return True

    answer_lower = answer.lower()

    return all(
        keyword.lower() not in answer_lower
        for keyword in keywords
    )


def evaluate():

    total_cases = len(EVALUATION_CASES)

    tool_correct = 0

    argument_cases = 0
    argument_correct = 0

    groundedness_cases = 0
    groundedness_correct = 0

    guardrail_cases = 0
    guardrail_correct = 0


    print("\n==============================")
    print("Agent Evaluation")
    print("==============================\n")


    for case in EVALUATION_CASES:

        case_id = case["id"]
        question = case["question"]

        expected_tool = case.get("expected_tool")
        allowed_tools = case.get("allowed_tools")

        expected_arguments = case.get(
            "expected_arguments"
        )

        expected_keywords = case.get(
            "expected_keywords",
            []
        )

        expected_keywords_any = case.get(
            "expected_keywords_any",
            []
        )

        forbidden_keywords = case.get(
            "forbidden_keywords",
            []
        )

        evaluation_type = case.get(
            "evaluation_type",
            "standard"
        )


        print("------------------------------")
        print(f"Case: {case_id}")
        print(f"Question: {question}")


        result = ask_factory_agent(
            question,
            language="English",
            return_trace=True
        )


        actual_tool = result["tool_name"]

        actual_arguments = normalize_arguments(
            result["arguments"]
        )

        answer = result["answer"] or ""


        # =================================================
        # Tool Selection
        # =================================================

        if allowed_tools is not None:

            tool_pass = (
                actual_tool in allowed_tools
            )

            print(
                f"Allowed Tools: "
                f"{allowed_tools}"
            )

        else:

            tool_pass = (
                actual_tool == expected_tool
            )

            print(
                f"Expected Tool: "
                f"{expected_tool}"
            )


        print(
            f"Actual Tool:   "
            f"{actual_tool}"
        )


        if tool_pass:
            tool_correct += 1


        print(
            "Tool Selection:",
            "PASS ✅"
            if tool_pass
            else "FAIL ❌"
        )


        # =================================================
        # Argument Accuracy
        # =================================================

        if expected_arguments is not None:

            argument_cases += 1

            expected_arguments = (
                normalize_arguments(
                    expected_arguments
                )
            )


            argument_pass = (
                actual_arguments
                == expected_arguments
            )


            if argument_pass:
                argument_correct += 1


            print(
                f"Expected Arguments: "
                f"{expected_arguments}"
            )

            print(
                f"Actual Arguments:   "
                f"{actual_arguments}"
            )


            print(
                "Argument Accuracy:",
                "PASS ✅"
                if argument_pass
                else "FAIL ❌"
            )


        # =================================================
        # Answer Conditions
        # =================================================

        all_keywords_pass = (
            contains_all_keywords(
                answer,
                expected_keywords
            )
        )

        any_keywords_pass = (
            contains_any_keyword(
                answer,
                expected_keywords_any
            )
        )

        forbidden_pass = (
            avoids_forbidden_keywords(
                answer,
                forbidden_keywords
            )
        )


        answer_condition_pass = (
            all_keywords_pass
            and any_keywords_pass
            and forbidden_pass
        )


        # =================================================
        # Groundedness
        # =================================================

        if evaluation_type == "groundedness":

            groundedness_cases += 1

            groundedness_pass = (
                tool_pass
                and answer_condition_pass
            )


            if groundedness_pass:
                groundedness_correct += 1


            print(
                "Groundedness:",
                "PASS ✅"
                if groundedness_pass
                else "FAIL ❌"
            )


        # =================================================
        # Guardrail
        # =================================================

        elif evaluation_type == "guardrail":

            guardrail_cases += 1

            guardrail_pass = (
                tool_pass
                and answer_condition_pass
            )


            if guardrail_pass:
                guardrail_correct += 1


            print(
                "Guardrail Compliance:",
                "PASS ✅"
                if guardrail_pass
                else "FAIL ❌"
            )


        # =================================================
        # Standard Content
        # =================================================

        else:

            if (
                expected_keywords
                or expected_keywords_any
            ):

                print(
                    "Expected Content:",
                    "PASS ✅"
                    if answer_condition_pass
                    else "FAIL ❌"
                )


        print("\nAnswer Preview:")
        print(answer[:500])
        print()


    # =====================================================
    # Summary
    # =====================================================

    tool_accuracy = (
        tool_correct
        / total_cases
        * 100
    )


    argument_accuracy = (
        argument_correct
        / argument_cases
        * 100
        if argument_cases
        else 0
    )


    groundedness_accuracy = (
        groundedness_correct
        / groundedness_cases
        * 100
        if groundedness_cases
        else 0
    )


    guardrail_accuracy = (
        guardrail_correct
        / guardrail_cases
        * 100
        if guardrail_cases
        else 0
    )


    print("\n==============================")
    print("Evaluation Summary")
    print("==============================")


    print(
        f"Tool Selection Accuracy: "
        f"{tool_correct}/{total_cases} "
        f"({tool_accuracy:.2f}%)"
    )


    print(
        f"Argument Accuracy: "
        f"{argument_correct}/{argument_cases} "
        f"({argument_accuracy:.2f}%)"
    )


    print(
        f"Groundedness: "
        f"{groundedness_correct}/"
        f"{groundedness_cases} "
        f"({groundedness_accuracy:.2f}%)"
    )


    print(
        f"Guardrail Compliance: "
        f"{guardrail_correct}/"
        f"{guardrail_cases} "
        f"({guardrail_accuracy:.2f}%)"
    )


if __name__ == "__main__":
    evaluate()