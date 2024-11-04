from add_scripts.data import (
    AddDatasetCode,
    load_new_records,
    save_new_records,
    load_table,
    OUTPUT_BASE,
)


def load_table1() -> list[dict]:
    table = load_table(table_path=OUTPUT_BASE / "table1.md")

    rows_ = []
    for row in table:
        row_ = {
            "code": AddDatasetCode[row["#"]],
            "title": row["Title"],
            "previous_id": row["Previous ID"],
            "previous_edition": row["Previous Edition"],
            "new_id": row["New ID"],
            "new_edition": row["New Edition"],
        }
        rows_.append(row_)
    return rows_


def set_record_id(record: dict, record_id: str) -> dict:
    record["file_identifier"] = record_id
    if "identifiers" not in record["identification"]:
        record["identification"]["identifiers"] = []
    record["identification"]["identifiers"].append(
        {
            "identifier": record_id,
            "href": f"https://data.bas.ac.uk/items/{record_id}",
            "namespace": "data.bas.ac.uk",
        }
    )
    return record


def process_resources(
    records: dict[AddDatasetCode, dict], datasets: list[dict]
) -> dict[AddDatasetCode, dict]:
    for dataset in datasets:
        record = records[dataset["code"]]
        records[dataset["code"]] = set_record_id(record, dataset["new_id"])
    return records


def cleanup_original_records(file_names: dict[AddDatasetCode, str]) -> None:
    for record_code, file_name in file_names.items():
        record_path = OUTPUT_BASE / "records" / f"{file_name}.json"
        record_path.unlink()


def main() -> None:
    file_names, records = load_new_records()
    datasets = load_table1()
    records = process_resources(records, datasets)
    save_new_records(file_names, records)
    cleanup_original_records(file_names)
    print("Script exited normally.")


if __name__ == "__main__":
    main()
