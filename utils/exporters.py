import csv
import io


def convert_to_csv(test_cases: dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "test_type", "id", "title",
        "preconditions", "gherkin", "risk_level", "risk_reason",
        "data_checks", "endpoint", "assertions"
    ])
    for test_type, cases in test_cases.items():
        for case in cases:
            writer.writerow([
                test_type,
                case.get("id", ""),
                case.get("title", ""),
                " | ".join(case.get("preconditions", [])),
                "\n".join(case.get("gherkin", [])),
                case.get("risk_level", ""),
                case.get("risk_reason", ""),
                " | ".join(case.get("data_checks", [])),
                case.get("endpoint", ""),
                " | ".join(case.get("assertions", [])),
            ])
    return output.getvalue()


def convert_to_feature_file(test_cases: dict) -> str:
    lines = ["Feature: Generated Test Cases", ""]
    for test_type, cases in test_cases.items():
        if not cases:
            continue
        lines.append(f"  # {test_type.capitalize()} Tests")
        lines.append("")
        for case in cases:
            lines.append(f"  Scenario: {case.get('title', case.get('id', 'Unnamed'))}")
            for pre in case.get("preconditions", []):
                lines.append(f"    # Precondition: {pre}")
            for step in case.get("gherkin", []):
                lines.append(f"    {step}")
            lines.append("")
    return "\n".join(lines)
