import json

from add_scripts.data import (
    OUTPUT_BASE,
    AddDatasetCode,
    format_file_name,
    load_new_records,
    save_new_records,
    cleanup_original_records,
)


def load_resources() -> dict[AddDatasetCode, dict]:
    records = {}
    records_path = OUTPUT_BASE / "records_store"

    for record_path in records_path.glob("*.json"):
        with record_path.open() as f:
            record_data = json.load(f)
        record_code = AddDatasetCode(record_data["identification"]["title"]["value"])
        records[record_code] = record_data

    return records


def save_resources(records: dict[AddDatasetCode, dict]) -> None:
    records_path = OUTPUT_BASE / "records"
    records_path.mkdir(exist_ok=True, parents=True)

    for record_code, record in records.items():
        record_path = records_path / format_file_name(record_code)
        with open(record_path, "w") as f:
            json.dump(record, f, indent=4)


def main():
    records = load_resources()
    save_resources(records)
    file_names, records = load_new_records()
    save_new_records(file_names, records)
    cleanup_original_records(file_names)
    print("Script exited normally.")


if __name__ == "__main__":
    main()
