from add_scripts.data import (
    ADD_PREVIOUS_COLLECTION,
    load_record_from_store,
    get_collection_record_ids,
    save_record_to_store,
    update_record_date_stamp,
)


def get_previous_records() -> list[str]:
    collection = load_record_from_store(ADD_PREVIOUS_COLLECTION)
    return get_collection_record_ids(collection)


def remove_record_services(record_id: str) -> None:
    record = load_record_from_store(record_id)

    update_record = False
    distributions = []
    if "distribution" in record:
        for distribution in record["distribution"]:
            # omit any service distribution option
            if (
                "format" in distribution
                and "href" in distribution["format"]
                and "https://metadata-resources.data.bas.ac.uk/media-types/x-service/"
                in distribution["format"]["href"]
            ):
                update_record = True
                continue
            distributions.append(distribution)
    record["distribution"] = distributions
    if len(distributions) == 0:
        del record["distribution"]

    if not update_record:
        return None

    update_record_date_stamp(record)
    save_record_to_store(record)


def main():
    for record_id in get_previous_records():
        remove_record_services(record_id)
    print("Script exited normally.")


if __name__ == "__main__":
    main()
