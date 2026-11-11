---
bump: minor
floor: minor
inUnreleased: true
---
### Added

- Added an excitation-curve preview for ambiguous imports. Choose the sheet, table, and columns after inspecting sample rows.

### Fixed

- Preserve the first measurement in headerless CSVs and leave the loaded curve in place when an import fails or is cancelled.
- Allow Excel imports without an uncertainty column and support legacy .xls workbooks with xlrd.
