import json
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
        record_code = AddDatasetCode[record_path.stem.split('_')[0]]
        with record_path.open() as f:
            record_data = json.load(f)
        file_names[record_code] = record_path.stem
        records_data[record_code] = record_data

    return file_names, records_data
