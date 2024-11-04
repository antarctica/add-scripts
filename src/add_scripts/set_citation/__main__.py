from add_scripts.data import load_new_records, save_new_records, load_table, OUTPUT_BASE


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


def process_citations(rows: list[dict]) -> dict[str, tuple[dict, str]]:
    elements = {}

    for row in rows:
        record_elements = (
            {
                "identifier": row["doi_identifier"],
                "href": f"https://doi.org/{row['doi_identifier']}",
                "namespace": "doi",
            },
            row["citation"],
        )

        elements[row["record_id"]] = record_elements

    return elements


def set_citation(record: dict, elements: tuple[dict, str]) -> dict:
    record["identification"]["other_citation_details"] = elements[1]

    add_identifier = True
    for identifier in record["identification"]["identifiers"]:
        if identifier["namespace"] == "doi":
            add_identifier = False
            break
    if add_identifier:
        record["identification"]["identifiers"].append(elements[0])

    return record


def main() -> None:
    file_names, records = load_new_records()
    elements = process_citations(rows=load_table3())
    for record_code, record in records.items():
        record_id = record["file_identifier"]
        records[record_code] = set_citation(record, elements[record_id])
    save_new_records(file_names, records)
    print("Script exited normally.")


if __name__ == "__main__":
    main()
