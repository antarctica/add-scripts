from copy import deepcopy
from datetime import datetime

from add_scripts.data import load_table3, OUTPUT_BASE, load_new_records, AddDatasetCode


def fix_citations(rows: list[dict], records: dict[AddDatasetCode, dict]) -> list[dict]:
    current_year = datetime.now().year
    updated_rows: list[dict] = []

    record_editions = {}
    for record in records.values():
        record_editions[record["file_identifier"]] = record["identification"]["edition"]

    for row in rows:
        updated_row = deepcopy(row)
        updated_row["citation"] = row["citation"].replace(f" - VERSION {record_editions[row['record_id']]} ", "")
        updated_row["citation"] = (
            f"{updated_row['citation']}\\n\\nIf using for a graphic or if short on space, please cite as 'Data from the SCAR Antarctic Digital Database, {current_year}'."
        )
        updated_rows.append(updated_row)

    return updated_rows


def make_table(rows: list[dict]) -> None:
    table_path = OUTPUT_BASE / "table3.md"
    table_path.parent.mkdir(parents=True, exist_ok=True)

    with table_path.open(mode="w") as f:
        f.write("| Resource ID | DOI (Value) | Citation |\n")
        f.write("| ----------- | ----------- | -------- |\n")
        for row in rows:
            f.write(
                f"| {row['record_id']} | {row['doi_identifier']} | {row['citation']} |\n"
            )

    print(f"Table written to '{table_path.resolve()}'")


def main() -> None:
    file_names, records = load_new_records()
    rows = fix_citations(rows=load_table3(), records=records)
    make_table(rows=rows)
    print("Script exited normally.")


if __name__ == "__main__":
    main()
