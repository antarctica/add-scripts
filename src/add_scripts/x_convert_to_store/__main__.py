import json
from pathlib import Path

from add_scripts.data import OUTPUT_BASE, AddDatasetCode, load_new_records


def clean_output(records_path: Path) -> None:
    if not records_path.exists():
        return
    for item in records_path.glob("*.json"):
        item.unlink()


def save_resources(records_path: Path, records: dict[AddDatasetCode, dict]) -> None:
    records_path.mkdir(exist_ok=True, parents=True)

    for record in records.values():
        record_path = records_path / f"{record['file_identifier']}.json"
        with open(record_path, "w") as f:
            json.dump(record, f, indent=4)


def main():
    file_names, records = load_new_records()
    records_path = OUTPUT_BASE / "records_store"
    clean_output(records_path)
    save_resources(records_path, records)
    print("Script exited normally.")


if __name__ == "__main__":
    main()
