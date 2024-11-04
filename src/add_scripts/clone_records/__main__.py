import json
from copy import deepcopy

import inquirer

from add_scripts.data import (
    AddDatasetCode,
    ADD_CURRENT_COLLECTION,
    OUTPUT_BASE,
    load_record_from_store,
)


UPDATE_PLACEHOLDER = "!!PLACEHOLDER!!"
DEFAULT_DATASETS_TO_CLONE = [
    AddDatasetCode.C01.name,  # coast_line_h
    AddDatasetCode.C02.name,  # coast_line_m
    AddDatasetCode.C03.name,  # coast_poly_h
    AddDatasetCode.C04.name,  # coast_poly_m
    AddDatasetCode.C15.name,  # seamask_poly_h
    AddDatasetCode.C16.name,  # seamask_poly_m
]


def prompt_for_settings() -> tuple[str, list[AddDatasetCode]]:
    questions = [
        inquirer.Text(name="release", message="What is the next release version?"),
        inquirer.Checkbox(
            name="datasets_core",
            message="Which core datasets will change in this release?",
            choices=[(dataset.value, dataset.name) for dataset in AddDatasetCode],
            default=DEFAULT_DATASETS_TO_CLONE,
        ),
    ]
    answers = inquirer.prompt(questions)
    return answers["release"], [
        AddDatasetCode[dataset] for dataset in answers["datasets_core"]
    ]


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

    add_collection = load_record_from_store(ADD_CURRENT_COLLECTION)
    current_record_ids = get_collection_record_ids(add_collection)
    records_by_title = {}

    for record_id in current_record_ids:
        record_data = load_record_from_store(record_id)
        record_title = record_data["identification"]["title"]["value"]
        records_by_title[record_title] = record_id
        record_code = AddDatasetCode(record_title)
        current_records[record_code.name] = record_data

    return current_records


def get_selected_records(selected_datasets: list[AddDatasetCode]) -> list[dict]:
    selected_records = []
    current_records = index_add_records()

    for dataset in selected_datasets:
        selected_records.append(current_records[dataset.name])

    return selected_records


def clone_records(selected_records: list[dict], next_release: str):
    cloned_records = []

    for record in selected_records:
        clone = deepcopy(record)

        # clear/remove any existing identifiers
        clone["file_identifier"] = UPDATE_PLACEHOLDER
        if "identifiers" in clone["identification"]:
            del clone["identification"]["identifiers"]

        # clear citation as based on identifier
        if "other_citation_details" in clone["identification"]:
            clone["identification"]["other_citation_details"] = UPDATE_PLACEHOLDER

        # update edition
        clone["identification"]["edition"] = next_release

        # update revisionOf aggregation
        if "aggregations" in clone["identification"]:
            for i, aggregation in enumerate(clone["identification"]["aggregations"]):
                if (
                    "association_type" in aggregation
                    and aggregation["association_type"] == "revisionOf"
                ):
                    clone["identification"]["aggregations"][i]["identifier"][
                        "identifier"
                    ] = record["file_identifier"]
                    clone["identification"]["aggregations"][i]["identifier"]["href"] = (
                        f"https://data.bas.ac.uk/items/{record['file_identifier']}"
                    )

        # remove distribution options, except services if present
        distribution_options = []
        if "distribution" in clone:
            for distribution in clone["distribution"]:
                if (
                    "format" in distribution
                    and "href" in distribution["format"]
                    and "https://metadata-resources.data.bas.ac.uk/media-types/x-service/"
                    in distribution["format"]["href"]
                ):
                    distribution_options.append(distribution)
        clone["distribution"] = distribution_options
        if len(distribution_options) == 0:
            del clone["distribution"]

        cloned_records.append(clone)

    return cloned_records


def format_file_name(code):
    if code == AddDatasetCode.C01:
        return f"C01_coast_line_h.json"
    if code == AddDatasetCode.C02:
        return f"C02_coast_line_m.json"
    if code == AddDatasetCode.C03:
        return f"C03_coast_poly_h.json"
    if code == AddDatasetCode.C04:
        return f"C04_coast_poly_m.json"
    if code == AddDatasetCode.C05:
        return f"C05_contours_h.json"
    if code == AddDatasetCode.C06:
        return f"C06_contours_m.json"
    if code == AddDatasetCode.C07:
        return f"C07_rock_auto.json"
    if code == AddDatasetCode.C08:
        return f"C08_rock_poly_h.json"
    if code == AddDatasetCode.C09:
        return f"C09_rock_poly_m.json"
    if code == AddDatasetCode.C10:
        return f"C10_moraine_h.json"
    if code == AddDatasetCode.C11:
        return f"C11_moraine_m.json"
    if code == AddDatasetCode.C12:
        return f"C12_lakes_h.json"
    if code == AddDatasetCode.C13:
        return f"C13_lakes_m.json"
    if code == AddDatasetCode.C14:
        return f"C14_streams.json"
    if code == AddDatasetCode.C15:
        return f"C15_seamask_poly_h.json"
    if code == AddDatasetCode.C16:
        return f"C16_seamask_poly_m.json"
    if code == AddDatasetCode.C17:
        return f"C17_data_limit.json"

    raise ValueError(f"Unknown dataset code: {code}")


def save_cloned_records(cloned_records: list[dict]):
    records_base = OUTPUT_BASE / "records"
    records_base.mkdir(parents=True, exist_ok=True)
    print(f"Any existing records in '{records_base.resolve()}' will be deleted.")
    _input = input("Type 'y' if you are happy with this:")
    if _input != "y":
        print("Aborted")
        exit(0)

    for record in records_base.glob("*.json"):
        record.unlink()

    for record in cloned_records:
        record_code = AddDatasetCode(record["identification"]["title"]["value"])
        record_path = records_base / format_file_name(record_code)
        with record_path.open(mode="w") as f:
            json.dump(record, f, indent=2)

    print(f"Selected dataset records cloned to '{records_base.resolve()}'")


def make_table(selected_records: list[dict], next_release: str):
    table_path = OUTPUT_BASE / "table1.md"
    table_path.parent.mkdir(parents=True, exist_ok=True)

    with table_path.open(mode="w") as f:
        f.write(
            "| # | Title | Previous ID | Previous Edition | New ID | New Edition |\n"
        )
        f.write(
            "| - | ----- | ----------- | ---------------- | ------ | ----------- |\n"
        )
        for record in selected_records:
            title = record["identification"]["title"]["value"]
            code = AddDatasetCode(title)
            previous_id = record["file_identifier"]
            previous_edition = record["identification"]["edition"]
            f.write(
                f"| {code.name} | {title} | {previous_id} | {previous_edition} | {' ' * 36} | {next_release} |\n"
            )

    print(f"Table written to '{table_path.resolve()}'")


def main():
    next_release, selected_datasets = prompt_for_settings()
    selected_records = get_selected_records(selected_datasets)
    cloned_records = clone_records(selected_records, next_release)
    save_cloned_records(cloned_records)
    make_table(selected_records, next_release)
    print("Script exited normally.")


if __name__ == "__main__":
    main()
