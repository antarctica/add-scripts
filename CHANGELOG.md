# SCAR Antarctic Digital Database (ADD) Release Scripts - Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2024-11-17

### Added

* Initial fix citations script to remove duplicate version and include short citation guidance in table
* Initial check record downloads script, match hashes again reference files and indirectly verifying DOI resolution
* Experimental scripts for loading and saving new records from and to a records store (essentially renaming their files) 
* Documentation on output folder and records store

### Fixed

* set transfer opts script setting all options with values from the last record
* set transfer opts script setting opts that already exist

### Changed

* date update handling

## [0.2.0] - 2024-11-04

### Removed [BREAKING!]

* Download Proxy lookup items script (access URLs now used directly)

### Added

* Initial clone records script
* Initial set resource IDs script
* Initial update collections script
* Initial set citation script
* Initial services cleanup script

### Changed

* Switched from Black to Ruff for code formatting
* README updates
* Rewrite of check transfer options script
* Rewrite of set dates script
* Rewrite of set transfer options script

## [0.1.0] - 2023-11-10

### Added

* Script to check all transfer option URLs are unique in a set of records, to defend against #2
* Initial project with initial scripts for: 
  * registering download proxy lookup items
  * updating transfer options in records to use these lookup items
  * updating release/publication dates prior to import into the ADD Metadata Toolbox

### Fixed

* Selection of per-record transfer option URLs based on registered lookup items
