# Signing Readiness Audit

## Purpose

Adds a local audit script for checking project state before any future signed System Extension and DriverKit activation attempt.

This stage is audit-only.

## Script

Run:

    ./scripts/check-signing-readiness.sh

## Checks

The script checks:

- macOS version
- Xcode version
- required project files
- Host App System Extension install entitlement
- DriverKit Info.plist PCI match
- Host App activation request identifier references
- Host App signing build settings
- DriverKit signing build settings

## Boundary

This script does not activate a System Extension.

This script does not load a DriverKit driver.

This script does not access MMIO, BAR memory, display engines, GSP firmware, GPU reset paths, or graphics acceleration paths.

## Expected Use

Run this before the first signed activation attempt to confirm that bundle IDs, entitlements, and build settings are visible and auditable.
