# SCAR Antarctic Digital Database (ADD) Release Scripts

Scripts to assist with SCAR Antarctic Digital Database (ADD) releases.

## Overview

**Note:** This project is focused on needs within the British Antarctic Survey. It has been open-sourced in case it is
of interest to others. Some resources, indicated with a '🛡' or '🔒' symbol, can only be accessed by BAS staff or
project members respectively. Contact the [Project Maintainer](#project-maintainer) to request access.

### Purpose

To help speed up and simplify ADD releases by automating boring tasks.

Part of a wider aim to streamline and automate the ADD release workflow 
([#172](https://gitlab.data.bas.ac.uk/MAGIC/add/-/issues/172)) and more generally as a demonstration of the 
[PDC-MAGIC Data Workflows](https://gist.github.com/felnne/57b64396426bfe2ca641a91d7cf9e597) project.

### Status

**Note:** These scripts are in a raw/scrappy form, without tests, a CLI or proper structure. If and as these tasks 
settle, efforts to formalise these tasks into a proper tool may be possible.

Features, bugs, etc. for these scripts are managed in the main [ADD project](https://gitlab.data.bas.ac.uk/MAGIC/add).

## Usage

**Note:** These scripts currently contain hard-coded file paths, specific to @felnne's laptop. In time this may become 
configurable but until then, you will need to review and adjust each script before running.

**Note:** To use these scripts you will need a [Records Store](#records-store).

Scripts should be run in this order (some scripts require other scripts to be run first):

1. [clone previous records](#clone-previous-records)
1. [set resource identifiers](#set-resource-ids)
1. [update collections](#update-collections)
1. [clean up services](#clean-up-services)
1. [set transfer options](#set-transfer-options)
1. [check transfer options](#check-transfer-options)
1. [fix citations](#fix-citation)
1. [set citations](#set-citation)
1. [update dates](#update-dates)
1. [check downloads](#check-downloads)

Additional scripts

* [convert records to local store](#convert-records-to-local-store)
* [convert records from local store](#convert-records-from-local-store)

### Clone previous records

This script copies previous/current records for datasets that will be updated in an upcoming release into a 
[folder](#conventional-folders).

Before running this script you will need to:

- decide which datasets will be updated in the upcoming release

To run this script:

```
$ poetry run python src/add_scripts/clone_records
```

For information, this script will:

- prompt for the next release version (e.g. '7.10')
- prompt for the datasets that should be cloned (datasets that typically change are selected by default)
- get the identifiers for current datasets listed in the ADD (core) collection 
- filter these against `DATASETS_TO_CLONE`
- copy selected records into new records
- removes identifiers and sets the file identifier and citation to a placeholder value
- removes distribution options except services (which are assumed to roll over)
- sets the edition to the upcoming release
- sets the `revisionOf` related record to the source record
- save cloned records as files
- save a MarkDown formatted *table 1* to act as a reference within the relevant release issue

### Set resource IDs

This script sets the resource identifier of cloned records for datasets that will be updated in an upcoming release.

Before running this script you will need to:

- have run the [Clone Previous Records](#clone-previous-records) script
- copy a completed *table 1* from a release issue ('New ID' column MUST be filled in) into `next_release/table1.md`

To run this script:

```
$ poetry run python src/add_scripts/set_resource_id
```

For information, this script will:

- load cloned records and index them by ADD Dataset Code
- parse *table 1* as a MarkDown formatted string (representing a table), indexed by ADD Dataset Code
- set the file identifier and adds an identification identifier for each record based on the relevant 'New ID' value
- save each record incorporating the first segment of the record identifier as a new record
- delete the original cloned records (without the file identifier in the name)

### Update collections

This script updates the ADD core and previous versions collections based on records that will form part of the upcoming
release.

Before running this script you will need to:

- have run the [Set Resource IDs](#set-resource-ids) script

To run this script:

```
$ poetry run python src/add_scripts/update_collections
```

For information, this script will:

- load new records and index them by ADD Dataset Code
- update the previous ADD (core) records collection items, to prepend the identifiers for any records that have been cloned
- update the current ADD (core) collection items, to replace the identifiers for any records that have been cloned
- update the metadata date stamp and increment the edition of the previous & current ADD records collections
- save updated collections back to the records store

### Clean up services

This script checks records in the previous versions collection and removes any service based distribution options from
any records it contains.

When datasets are replaced, the older record needs updating to remove any services it may have listed, as ADD services
only relate to current datasets, represented by the current (core) ADD collection.

Before running this script you will need to:

- have run the [Update Collections](#update-collections) script

To run this script:

```
$ poetry run python src/add_scripts/clean_services
```

For information, this script will:

- load records contained in the previous ADD (core)
- check if a record contains distribution options relating to a service, and if so removes them
- update the metadata date stamp for any record that is updated and save the record back to the records store

### Set transfer options

This script sets distribution options (downloads) in each record in the upcoming release.

Before running this script you will need to:

- have run the [Set Resource IDs](#set-resource-ids) script
- copy a completed *table 2* from a release issue into `next_release/table2.md`

Existing distribution options will not be removed or duplicated, meaning it should be safe to run this script 
multiple times.

**Note:** This script only supports 
[GeoPackage](https://www.iana.org/assignments/media-types/application/geopackage+sqlite3) and 
[Zipped Shapefile](https://metadata-resources.data.bas.ac.uk/media-types/application/vnd.shp+zip) as distribution 
formats.

**Note:** It is assumed all transfer options recorded in *table 2* are files deposited with the PDC, and so hard-codes 
the PDC contact as the distributor role.

To run this script:

```
$ poetry run python src/add_scripts/set_transfer_options
```

For information, this script will:

- load new records and index them by ADD Dataset Code
- parse *table 2* as a MarkDown formatted string (representing a table), indexed by resource/record identifier
- process this information into distribution options, including format, transfer option (size and URL) and distributor
- append distribution options to each record
- save new records

### Check transfer options

This script checks transfer options in each record in the upcoming release have unique URLs, to detect errors from 
other tasks. This script will also check for any download proxy URLs without an artefact specified.

This script is only a check, if it finds problems they will be listed (but not fixed).

Before running this script you will need to:

- have run the [Clone Previous Records](#clone-previous-records) script

To run this script:

```
$ poetry run python src/add_scripts/check_transfer_options
```

For information, this script will:

- load new records and index them by ADD Dataset Code
- extract transfer option URLs and format media types for each record
- create a list of (record_id, transfer_url, transfer_media_type) tuples for all transfer options in all new records
- for each transfer_url find the number of times it appears in any tuple
- if more than once, store the indexes of each matching tuple (e.g. 1st and 7th list index)
- for each set of matching tuples, add to a dict indexed by transfer_option
- check whether each transfer_url points to the Download Proxy, and if so, has an artefact specified
- report on any duplicate or incomplete URLs found

### Fix citation

This script fixes and updates citations to remove duplicate information (version) and add additional guidance. Updated
citations are saved back into table 3 for use by the [Set Citation](#set-citation) script.

For example a citation:

> Gerrish, L. (2024). High resolution vector polygon seamask for areas south of 60S - VERSION 7.10 (Version 7.10) [Data set]. NERC EDS UK Polar Data Centre. https://doi.org/10.5285/9288fd09-681b-4377-84b2-6ab9b9c6c05d

Is updated to:

> Gerrish, L. (2024). High resolution vector polygon seamask for areas south of 60S (Version 7.10) [Data set]. NERC EDS UK Polar Data Centre. https://doi.org/10.5285/9288fd09-681b-4377-84b2-6ab9b9c6c05d
>
> If using for a graphic or if short on space, please cite as 'Data from the SCAR Antarctic Digital Database, 2024.'

**Note:** line breaks are shown in the above example for legibility, real output uses `\n\n` as a single line.)

Before running this script you will need to:

- have run the [Set Resource IDs](#set-resource-ids) script
- copy a completed *table 3* from a release issue into `next_release/table3.md`

```
$ poetry run python src/add_scripts/fix_citation
```

For information, this script will:

- load new records and index them by ADD Dataset Code
- parse *table 3* as a MarkDown formatted string (representing a table), as a list of rows
- for each row, get the edition value from the record it relates to (based on resource ID)
- for each row, update the citation field to remove duplicate edition/version clause
- for each row, update the citation field to include additional guidance text
- save an updated MarkDown formatted *table 3* to act as a reference within the relevant release issue

### Set citation

This script sets the citation and ads an identifier for a DOI in each record in the upcoming release.

Before running this script you will need to:

- have run the [Fix Citations](#fix-citation) script
- have a corrected *table 3* in `next_release/table3.md`

To run this script:

```
$ poetry run python src/add_scripts/set_citation
```

For information, this script will:

- load new records and index them by ADD Dataset Code
- parse *table 3* as a MarkDown formatted string (representing a table), indexed by resource/record identifier
- process this information into a DOI identifier and 'other citation details' elements
- append the DOI identifier if not present and set the other citation details element
- save new records

### Update dates

This script updates the released and publication dates in each record in the upcoming release. It also updates the 
metadata datestamp.

All three dates will be set to the current time. UTC is always used (so in the summer will appear as 1 hour behind).

Before running this script you will need to:

- have run the [Clone Previous Records](#clone-previous-records) script

To run this script:

```
$ poetry run python src/add_scripts/set_dates
```

For information, this script will:

- load new records and index them by ADD Dataset Code
- set or update the *publication* date to the current date and time for each record
- set or update the *released* date to the current date and time for each record
- set the metadata datestamp for each record
- save each updated record

### Check downloads

This script verifies DOIs resolve to a Data Catalogue item page and that any file downloads its related record contains
match the artefacts for the upcoming release.

**Note:** Only all transfer options relating to files deposited with the PDC are verified by this script.

Downloads are verified by calculating SHA1 checksums of reference files and downloaded files from catalogue records.

This script does not verify specific downloads for each download (yet).

Before running this script you will need to:

- have run the [Set Resource IDs](#set-resource-ids) script
- copy a completed *table 3* from a release issue into `next_release/table3.md`
- copy artefacts from the ADD working directory into `next_release/aretfacts/`

To run this script:

```
$ poetry run python src/add_scripts/check_downloads
```

For information, this script will:

- generate a list 
- parse *table 3* as a MarkDown formatted string (representing a table), indexed by resource/record identifier
- derive a list of DOIs from the table
- make a HTTP request for each DOI, extracting the Data Catalogue item ID (file identifier) from the location header
- make a HTTP request for each ISO 19115 XML record and parse the response as XML
- select all distribution option transfer URLs within each XML document, giving a list of URLs
- filter URLs to select only those relating to GeoPackage/Shapefile downloads served from the PDC Ramadda instance
- download all URLs to a directory, skipping files that have been previously downloaded
- calculate the SHA1 hash of each file in the reference files directory and downloaded files directory
- compare the reference and downloaded hashes as sets to detect any differences, returning a message if there are
- save a MarkDown formatted *table 4* to act as a reference within the relevant release issue

### Convert records to local store

This script copies each record in the upcoming release into a folder named after it's resource ID.
The script does not modify the contents of a record, only the file of a file containing it.

This is intended for including records within the [Records Store](#records-store).

**Note:** This is an experimental script and may be removed or revised.

Before running this script you will need to:

- have run the [Set Resource IDs](#set-resource-ids) script

To run this script:

```
$ poetry run python src/add_scripts/x_convert_to_store
```

For information, this script will:

- load new records and index them by ADD Dataset Code
- save each record into a folder based on their resource ID (`file_identifier`) only

### Convert records from local store

This script copies files taken from the [Records Store](#records-store) into a folder for the next/upcoming release.
The script does not modify the contents of a record, only the file of a file containing it.

This is the opposite of the [convert records to local store](#convert-records-to-local-store) script.

**WARNING!** This will overwrite any files in `next_release/records` where their titles match.

**Note:** This is an experimental script and may be removed or revised.

Before running this script you will need to:

- copy one or more records from the [Records Store](#records-store) into `next_release/records_store/`

To run this script:

```
$ poetry run python src/add_scripts/x_convert_from_store
```

For information, this script will:

- load records from a folder
- save each record into the folder for the next release, named to include the relevant ADD code and title summary

## Implementation

Each task is currently structured as its own module, within the [`add_scripts`](src/add_scripts) package.

Some common functions, enums and variables are defined in [`data.py`](src/add_scripts/data.py).

### Records store

A store of catalogue records, typically a folder under version control. A store must:

- be available as `./records` relative to the root of this project (symlink's are ok)
- contain a `./records` subdirectory containing a flat list of record configs as JSON files 
  (e.g. `/records/records/abc123.json`)

**Note:** The `records bulk-export` command from the data catalogue can be used to dump out record configs.

**Note:** It is strongly recommended that this store be under version control, so you can easily see, and if needed 
revert, changes to records made by these scripts.

## Conventional folders

An output/working folder is used for storing cloned and updated records named `next_release`.

**Note:** It is strongly recommended that this folder be under version control, so you can easily see, and if needed 
revert, changes to records made by these scripts (`next_release` is ignored from this project's own Git repo).

This folder is distinct from:

- the ADD release working folder in the MAGIC OneDrive (though this may be used directly in future)
- the [Records Store](#records-store) (which contains all records)

Records will be:

- manually copied from, and possibly to, this output folder and the OneDrive working folder, to allow others to update 
  them
- automatically copied to, and manually from, this output folder into the [Records Store](#records-store), to store them
  alongside other records

The `next_release` folder contains:

- `records/`: records named using ADD codes for easy identification
- `records_store/`: records named using file identifiers only for compatibility with [Records Stores](#records-store)
- `table*.md`: various tables used as part of the ADD release issue/workflow

See `OUTPUT_BASE` in [`data.py`](src/add_scripts/data.py) the definition of this path in code.

## Setup

You will need Python and Poetry installed locally to set this project for use locally.

```
$ git clone https://gitlab.data.bas.ac.uk/MAGIC/add-release-scripts.git
$ cd add-release-scripts
$ poetry install
```

## Development

### Code formatting

All source code should be run through the Ruff code formatter:

```
$ poetry run ruff --format src/
```

## Project maintainer

British Antarctic Survey ([BAS](https://www.bas.ac.uk)) Mapping and Geographic Information Centre
([MAGIC](https://www.bas.ac.uk/teams/magic)). Contact [magic@bas.ac.uk](mailto:magic@bas.ac.uk).

The project lead is [@felnne](https://www.bas.ac.uk/profile/felnne).

## Licence

Copyright (c) 2022 - 2024 UK Research and Innovation (UKRI), British Antarctic Survey (BAS).

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
