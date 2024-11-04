from datetime import datetime, timezone

from add_scripts.data import load_new_records, save_new_records, update_record_date_stamp


def update_dates(record: dict) -> dict:
    now = datetime.now(tz=timezone.utc).replace(microsecond=0)

    # handle new records
    if 'publication' not in record["identification"]["dates"]:
        record["identification"]["dates"]["publication"] = ''
    if 'released' not in record["identification"]["dates"]:
        record["identification"]["dates"]["released"] = ''

    record["identification"]["dates"]["publication"] = now.isoformat()
    record["identification"]["dates"]["released"] = now.isoformat()
    record = update_record_date_stamp(record)

    return record

def main() -> None:
    file_names, records = load_new_records()
    for record_code, record in records.items():
        records[record_code] = update_dates(record)
    save_new_records(file_names, records)
    print("Script exited normally.")


if __name__ == "__main__":
    main()
