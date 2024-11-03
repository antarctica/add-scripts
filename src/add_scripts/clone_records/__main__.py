import json
from enum import Enum
from pathlib import Path


class AddDatasetCodes(Enum):
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


ADD_CURRENT_COLLECTION = "e74543c0-4c4e-4b41-aa33-5bb2f67df389"
RECORDS_BASE = Path("records")
OUTPUT_BASE = Path("next_release")

# comment out items that are not part of the next release
DATASETS_TO_CLONE = [
    AddDatasetCodes.C01,  # coast_line_h
    AddDatasetCodes.C02,  # coast_line_m
    AddDatasetCodes.C03,  # coast_poly_h
    AddDatasetCodes.C04,  # coast_poly_m
    # AddDatasetCodes.C05,  # contours_h
    # AddDatasetCodes.C06,  # contours_m
    # AddDatasetCodes.C07,  # rock_auto
    AddDatasetCodes.C08,  # rock_poly_h
    AddDatasetCodes.C09,  # rock_poly_m
    AddDatasetCodes.C10,  # moraine_h
    AddDatasetCodes.C11,  # moraine_m
    AddDatasetCodes.C12,  # lakes_h
    AddDatasetCodes.C13,  # lakes_m
    # AddDatasetCodes.C14,  # streams
    AddDatasetCodes.C15,  # seamask_poly_h
    AddDatasetCodes.C16,  # seamask_poly_m
    # AddDatasetCodes.C17,  # data_limit
]

# change to next release version
NEXT_RELEASE = "7.10"


def get_record_data(file_identifier: str) -> dict:
    record_path = RECORDS_BASE / "records" / f"{file_identifier}.json"
    with record_path.open() as f:
        return json.load(f)


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


def index_add_records() -> dict[str, dict]:
    current_records = {}

    add_collection = get_record_data(ADD_CURRENT_COLLECTION)
    current_record_ids = get_collection_record_ids(add_collection)
    records_by_title = {}

    for record_id in current_record_ids:
        record_data = get_record_data(record_id)
        record_title = record_data["identification"]["title"]["value"]
        records_by_title[record_title] = record_id
        record_code = AddDatasetCodes(record_title)
        current_records[record_code.name] = record_data

    return current_records


def get_selected_records() -> list[dict]:
    selected_records = []
    current_records = index_add_records()

    for dataset in DATASETS_TO_CLONE:
        selected_records.append(current_records[dataset.name])

    return selected_records


def format_file_name(code, file_identifier):
    if code == AddDatasetCodes.C01:
        return f"C01_coast_line_h-{file_identifier[:8]}.json"
    if code == AddDatasetCodes.C02:
        return f"C02_coast_line_m-{file_identifier[:8]}.json"
    if code == AddDatasetCodes.C03:
        return f"C03_coast_poly_h-{file_identifier[:8]}.json"
    if code == AddDatasetCodes.C04:
        return f"C04_coast_poly_m-{file_identifier[:8]}.json"
    if code == AddDatasetCodes.C05:
        return f"C05_contours_h-{file_identifier[:8]}.json"
    if code == AddDatasetCodes.C06:
        return f"C06_contours_m-{file_identifier[:8]}.json"
    if code == AddDatasetCodes.C07:
        return f"C07_rock_auto-{file_identifier[:8]}.json"
    if code == AddDatasetCodes.C08:
        return f"C08_rock_poly_h-{file_identifier[:8]}.json"
    if code == AddDatasetCodes.C09:
        return f"C09_rock_poly_m-{file_identifier[:8]}.json"
    if code == AddDatasetCodes.C10:
        return f"C10_moraine_h-{file_identifier[:8]}.json"
    if code == AddDatasetCodes.C11:
        return f"C11_moraine_m-{file_identifier[:8]}.json"
    if code == AddDatasetCodes.C12:
        return f"C12_lakes_h-{file_identifier[:8]}.json"
    if code == AddDatasetCodes.C13:
        return f"C13_lakes_m--{file_identifier[:8]}.json"
    if code == AddDatasetCodes.C14:
        return f"C14_streams-{file_identifier[:8]}.json"
    if code == AddDatasetCodes.C15:
        return f"C15_seamask_poly_h-{file_identifier[:8]}.json"
    if code == AddDatasetCodes.C16:
        return f"C16_seamask_poly_m-{file_identifier[:8]}.json"
    if code == AddDatasetCodes.C17:
        return f"C17_data_limit-{file_identifier[:8]}.json"

    raise ValueError(f"Unknown dataset code: {code}")


def save_selected_records():
    print(f"Any existing records in '{OUTPUT_BASE.resolve()}' will be deleted.")
    _input = input("Type 'y' if you are happy with this:")
    if _input != "y":
        print("Aborted")
        exit(0)

    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    for record in OUTPUT_BASE.glob("*.json"):
        record.unlink()

    for record in get_selected_records():
        record_code = AddDatasetCodes(record["identification"]["title"]["value"])
        record_path = OUTPUT_BASE / format_file_name(
            record_code, record["file_identifier"]
        )
        with record_path.open(mode="w") as f:
            json.dump(record, f, indent=2)

    print(f"Selected dataset records cloned to '{OUTPUT_BASE.resolve()}'")


def main():
    save_selected_records()
    print("Script exited normally.")


if __name__ == "__main__":
    main()
