from add_scripts.data import (
    ADD_CURRENT_COLLECTION,
    ADD_PREVIOUS_COLLECTION,
    load_record_from_store,
    load_new_records,
    save_record_to_store,
    update_record_date_stamp,
    update_date,
)


def increment_collection_edition(collection: dict) -> dict:
    collection["identification"]["edition"] = str(
        int(collection["identification"]["edition"]) + 1
    )
    collection = update_record_date_stamp(collection)
    collection = update_date(collection, "revision")
    return collection


def get_revision_of_identifier(record: dict) -> dict:
    if "aggregations" in record["identification"]:
        for i, aggregation in enumerate(record["identification"]["aggregations"]):
            if (
                "association_type" in aggregation
                and aggregation["association_type"] == "revisionOf"
            ):
                return aggregation["identifier"]


def update_current_collection(collection: dict, new_records: list[dict]) -> dict:
    old_new_ids: dict[str, str] = {}
    new_ids = []
    for record in new_records:
        old_id = get_revision_of_identifier(record)["identifier"]
        if old_id is None:
            new_ids.append(record["file_identifier"])
            continue
        old_new_ids[old_id] = record["file_identifier"]

    aggregations = []
    for aggregation in collection["identification"]["aggregations"]:
        if (
            aggregation["association_type"] == "isComposedOf"
            and aggregation["initiative_type"] == "collection"
            and aggregation["identifier"]["identifier"] in old_new_ids
        ):
            new_id = old_new_ids[aggregation["identifier"]["identifier"]]
            aggregations.append(
                {
                    "association_type": "isComposedOf",
                    "initiative_type": "collection",
                    "identifier": {
                        "identifier": new_id,
                        "href": f"https://data.bas.ac.uk/items/{new_id}",
                        "namespace": "data.bas.ac.uk",
                    },
                }
            )
        else:
            aggregations.append(aggregation)

    # append any new datasets (where no previous record will exist)
    for old_new_id in old_new_ids:
        if old_new_id[0] is None:
            aggregations.append(
                {
                    "association_type": "isComposedOf",
                    "initiative_type": "collection",
                    "identifier": {
                        "identifier": old_new_id[1],
                        "href": f"https://data.bas.ac.uk/items/{old_new_id[1]}",
                        "namespace": "data.bas.ac.uk",
                    },
                }
            )
    collection["identification"]["aggregations"] = aggregations

    return collection


def update_previous_collection(collection: dict, new_records: list[dict]) -> dict:
    old_ids = [
        get_revision_of_identifier(record)["identifier"] for record in new_records
    ]

    new_aggregations = []
    for old_id in old_ids:
        new_aggregations.append(
            {
                "association_type": "isComposedOf",
                "initiative_type": "collection",
                "identifier": {
                    "identifier": old_id,
                    "href": f"https://data.bas.ac.uk/items/{old_id}",
                    "namespace": "data.bas.ac.uk",
                },
            }
        )
    # prepend new aggregations so they appear first when viewed
    collection["identification"]["aggregations"] = (
        new_aggregations + collection["identification"]["aggregations"]
    )

    return collection


def main():
    new_file_names, new_records = load_new_records()

    previous_collection = load_record_from_store(ADD_PREVIOUS_COLLECTION)
    previous_collection = update_previous_collection(
        previous_collection, list(new_records.values())
    )
    previous_collection = increment_collection_edition(previous_collection)
    save_record_to_store(previous_collection)

    current_collection = load_record_from_store(ADD_CURRENT_COLLECTION)
    current_collection = update_current_collection(
        current_collection, list(new_records.values())
    )
    current_collection = increment_collection_edition(current_collection)
    save_record_to_store(current_collection)
    print("Script exited normally.")


if __name__ == "__main__":
    main()
