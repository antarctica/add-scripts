import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

ADD_CURRENT_COLLECTION = "e74543c0-4c4e-4b41-aa33-5bb2f67df389"
ADD_PREVIOUS_COLLECTION = "8ff8240d-dcfa-4906-ad3b-507929842012"
RECORDS_BASE = Path("records")  # records store
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


def format_file_name(code):
    if code == AddDatasetCode.C01:
        return "C01_coast_line_h.json"
    if code == AddDatasetCode.C02:
        return "C02_coast_line_m.json"
    if code == AddDatasetCode.C03:
        return "C03_coast_poly_h.json"
    if code == AddDatasetCode.C04:
        return "C04_coast_poly_m.json"
    if code == AddDatasetCode.C05:
        return "C05_contours_h.json"
    if code == AddDatasetCode.C06:
        return "C06_contours_m.json"
    if code == AddDatasetCode.C07:
        return "C07_rock_auto.json"
    if code == AddDatasetCode.C08:
        return "C08_rock_poly_h.json"
    if code == AddDatasetCode.C09:
        return "C09_rock_poly_m.json"
    if code == AddDatasetCode.C10:
        return "C10_moraine_h.json"
    if code == AddDatasetCode.C11:
        return "C11_moraine_m.json"
    if code == AddDatasetCode.C12:
        return "C12_lakes_h.json"
    if code == AddDatasetCode.C13:
        return "C13_lakes_m.json"
    if code == AddDatasetCode.C14:
        return "C14_streams.json"
    if code == AddDatasetCode.C15:
        return "C15_seamask_poly_h.json"
    if code == AddDatasetCode.C16:
        return "C16_seamask_poly_m.json"
    if code == AddDatasetCode.C17:
        return "C17_data_limit.json"

    raise ValueError(f"Unknown dataset code: {code}")


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


def cleanup_original_records(file_names: dict[AddDatasetCode, str]) -> None:
    for record_code, file_name in file_names.items():
        record_path = OUTPUT_BASE / "records" / f"{file_name}.json"
        record_path.unlink()


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


def load_table3() -> list[dict]:
    table = load_table(table_path=OUTPUT_BASE / "table3.md")

    rows_ = []
    for row in table:
        row_ = {
            "record_id": row["Resource ID"],
            "doi_identifier": row["DOI (Value)"],
            "citation": row["Citation"],
        }
        rows_.append(row_)
    return rows_


def get_collection_record_ids(record: dict) -> list[str]:
    related_ids = []

    if "identification" in record and "aggregations" in record["identification"]:
        for aggregation in record["identification"]["aggregations"]:
            if (
                "association_type" in aggregation
                and aggregation["association_type"] == "isComposedOf"
                and "initiative_type" in aggregation
                and aggregation["initiative_type"] == "collection"
                and "identifier" in aggregation
            ):
                related_ids.append(aggregation["identifier"]["identifier"])

    return related_ids


def update_record_date_stamp(record: dict) -> dict:
    now = datetime.now(tz=timezone.utc).replace(microsecond=0)
    record["metadata"]["date_stamp"] = now.strftime("%Y-%m-%d")
    return record


def update_date(record: dict, date_type: str) -> dict:
    now = datetime.now(tz=timezone.utc).replace(microsecond=0)
    record["identification"]["dates"][date_type] = now.isoformat()
    return record
