import json
import re


def clean(text):
    return re.sub(r"\s+", " ", text).strip() if text else None


def clean_data(raw_data):
    cleaned = []
    for row in raw_data:
        program = clean(row.get("program"))
        university = clean(row.get("university") or row.get("program"))

        row["llm-generated-program"] = program
        row["llm-generated-university"] = university
        cleaned.append(row)

    return cleaned


def save_data(cleaned_data, output_path="applicant_data.json"):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=True)


def load_data(input_path="raw_data.json"):
    # Support either JSON list or JSON Lines from the LLM tool.
    if input_path.endswith(".jsonl"):
        rows = []
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows
    with open(input_path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean GradCafe data and write applicant_data.json.",
    )
    parser.add_argument(
        "--input",
        default="raw_data.json",
        help="Path to input JSON list or JSONL file.",
    )
    parser.add_argument(
        "--output",
        default="applicant_data.json",
        help="Path to output JSON file.",
    )
    args = parser.parse_args()

    raw = load_data(args.input)
    cleaned = clean_data(raw)
    save_data(cleaned, args.output)
    print(f"Saved cleaned data: {len(cleaned)} entries")
