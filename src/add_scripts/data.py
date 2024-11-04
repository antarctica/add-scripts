import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

ADD_CURRENT_COLLECTION = "e74543c0-4c4e-4b41-aa33-5bb2f67df389"
ADD_PREVIOUS_COLLECTION = "8ff8240d-dcfa-4906-ad3b-507929842012"
RECORDS_BASE = Path("records")
OUTPUT_BASE = Path("next_release")


class AddDatasetCode(Enum):
    C01 = "High resolution vector polylines of the Antarctic coastline"
    C02 = "Medium resolution vector polylines of the Antarctic coastline"
    C03 = "High resolution vector polygons of the Antarctic coastline"
    C04 = "Medium resolution vector polygons of the Antarctic coastline"
    C05 = "High resolution vector contours for Antarctica"
    C06 = "Medium resolution vector contours for Antarctica"
    C07 = "Automatically extracted rock outcrop dataset for Antarctica"
    C08 = "High resolution vector polygons of Antarctic rock outcrop"
    C09 = "Medium resolution vector polygons of Antarctic rock outcrop"
    C10 = "High resolution Antarctic moraine dataset"
    C11 = "Medium resolution Antarctic moraine dataset"
    C12 = "High resolution Antarctic lakes dataset"
    C13 = "Medium resolution Antarctic lakes dataset"
    C14 = "Antarctic streams dataset"
    C15 = "High resolution vector polygon seamask for areas south of 60\u00b0S"
    C16 = "Medium resolution vector polygon seamask for areas south of 60\u00b0S"
    C17 = "Antarctic Digital Database data limit at 60\u00b0S"


def load_record_from_store(file_identifier: str) -> dict:
    record_path = RECORDS_BASE / "records" / f"{file_identifier}.json"
    with record_path.open() as f:
        return json.load(f)


def save_record_to_store(record: dict) -> None:
    record_path = RECORDS_BASE / "records" / f"{record['file_identifier']}.json"
    with record_path.open("w") as f:
        json.dump(record, f, indent=2)


def load_new_records() -> tuple[dict[AddDatasetCode, str], dict[AddDatasetCode, dict]]:
    records_path = OUTPUT_BASE / "records"
    records_data = {}
    file_names = {}

    for record_path in records_path.glob("*.json"):
        record_code = AddDatasetCode[record_path.stem.split("_")[0]]
        with record_path.open() as f:
            record_data = json.load(f)
        file_names[record_code] = record_path.stem
        records_data[record_code] = record_data

    return file_names, records_data


def save_new_records(
    file_names: dict[AddDatasetCode, str], records: dict[AddDatasetCode, dict]
) -> None:
    for record_code, record_data in records.items():
        file_name = file_names[record_code]
        record_id = record_data["file_identifier"]
        if record_id[:8] not in file_name:
            file_name = f"{file_name}-{record_id[:8]}"
        record_path = OUTPUT_BASE / "records" / f"{file_name}.json"
        with record_path.open(mode="w") as f:
            json.dump(record_data, f, indent=2)


def update_record_date_stamp(record: dict) -> dict:
    now = datetime.now(tz=timezone.utc).replace(microsecond=0)
    record["metadata"]["date_stamp"] = now.strftime("%Y-%m-%d")
    return record


def parse_markdown_table(table: str) -> list[dict]:
    lines = table.split("\n")
    headers = lines[0].split("|")
    headers = [h.strip() for h in headers if h.strip()]
    data = []
    for line in lines[2:]:
        row = line.split("|")
        row = [r.strip() for r in row if r.strip()]
        row = dict(zip(headers, row))
        data.append(row)
    return data


def load_table(table_path: Path) -> list[dict]:
    with table_path.open() as f:
        table = f.read()
        # trim blank last line if present
        if table[-1] == "\n":
            table = table[:-1]

    return parse_markdown_table(table)
