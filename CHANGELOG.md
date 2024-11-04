# SCAR Antarctic Digital Database (ADD) Release Scripts - Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

* Initial clone records script
* Initial set resource IDs script
* Initial update collections script

### Changed

* Switched from Black to Ruff for code formatting
* Updating README
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
