from hashlib import sha1 as sha1_alg
from io import BytesIO
from pathlib import Path

import requests
from lxml import etree
from tqdm import tqdm

from add_scripts.data import OUTPUT_BASE, load_table3


def hash_file(path: Path) -> str:
    file = path.open(mode="rb")
    try:
        sha1 = sha1_alg()
        sha1.update(file.read())
        return sha1.hexdigest()
    finally:
        file.close()


def hash_dir(path: Path) -> dict[Path, str]:
    hashes = {}
    for file_path in path.glob("*.*"):
        hashes[file_path] = hash_file(file_path)
    return hashes


def get_dois() -> list[str]:
    table3 = load_table3()
    return [row["doi_identifier"] for row in table3]


def get_urls_for_doi(doi: str) -> list[str]:
    doi_id = doi.split("/")[-1]
    doi_req = requests.get(f"https://doi.org/{doi}", allow_redirects=False)
    doi_req.raise_for_status()

    loc = doi_req.headers.get("location")
    if loc != f"https://data.bas.ac.uk/items/{doi_id}":
        print(f"Warning: Unexpected location: {loc} for DOI: {doi}")
        return []

    rec_req = requests.get(
        f"https://data.bas.ac.uk/records/{doi_id}/iso-xml/{doi_id}.xml"
    )
    rec_req.raise_for_status()
    record = etree.parse(BytesIO(rec_req.content))
    return record.xpath(
        "//gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource/gmd:linkage/gmd:URL/text()",
        namespaces={
            "gmd": "http://www.isotc211.org/2005/gmd",
            "gmi": "http://www.isotc211.org/2005/gmi",
        },
    )


def get_urls_for_dois(dois: list[str]) -> list[str]:
    urls = []
    for doi in tqdm(dois):
        urls.extend(get_urls_for_doi(doi))
    return urls


def filter_artefact_urls(urls: list[str]) -> list[str]:
    filtered_urls = []
    for url in urls:
        if "https://ramadda.data.bas.ac.uk" in url:
            if ".gpkg" in url or ".shp.zip" in url:
                filtered_urls.append(url)
    return filtered_urls


def download_artefacts(base_path: Path, urls: list[str]) -> None:
    for url in tqdm(urls):
        res = requests.get(url, stream=True)
        path = base_path / res.headers["content-disposition"].split("filename=")[1]
        total_size = int(res.headers["content-length"])

        if path.exists():
            if path.stat().st_size != total_size:
                path.unlink()
            else:
                print(f"Skipping {url.split('?')[0]}, {path.resolve()} already exists")
                continue

        print(f"Saving {url.split('?')[0]} as {path.resolve()}")
        with tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
            with path.open(mode="wb") as file:
                for data in res.iter_content(4096):
                    progress_bar.update(len(data))
                    file.write(data)

        if total_size != 0 and progress_bar.n != total_size:
            raise RuntimeError("Could not download file")


def compare_hashes(reference: dict[Path, str], downloads: dict) -> None:
    ref_hash: list[tuple[str, str]] = [
        (path.name, hash_) for path, hash_ in reference.items()
    ]
    dwn_hash: list[tuple[str, str]] = [
        (path.name, hash_) for path, hash_ in downloads.items()
    ]

    if set(ref_hash) == set(dwn_hash):
        return

    print("hash mismatch!")


def main():
    dois = get_dois()
    transfer_opts = get_urls_for_dois(dois)
    artefact_urls = filter_artefact_urls(transfer_opts)

    download_base = OUTPUT_BASE / "downloads"
    download_base.mkdir(exist_ok=True, parents=True)
    download_artefacts(download_base, artefact_urls)

    sha1_artefacts = hash_dir(OUTPUT_BASE / "artefacts")
    sha1_downloads = hash_dir(download_base)
    compare_hashes(sha1_artefacts, sha1_downloads)

    print("Script completed normally.")


if __name__ == "__main__":
    main()
