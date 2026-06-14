# H1mekaRTXDriverKit Xcode Project Materialization

Create the project manually in Xcode:

1. File > New > Project > macOS App.
2. Name: H1mekaRTXDriverKit.
3. Bundle ID: dev.h1meka.H1mekaRTXHost.
4. Add target: DriverKit Driver.
5. Dext target name: H1mekaRTXDriver.
6. Dext bundle ID: dev.h1meka.H1mekaRTXDriver.
7. Copy the source files from Sources/.
8. Copy Info.plist and entitlement templates from Config/.
9. Ensure the DriverKit target embeds into the host app at Contents/Library/SystemExtensions.
10. Do not add provider open, IOServiceOpen, BAR mapping, MMIO writes, or GPU command submission.

After project exists, run Phase 60L local build gate with:

python3 scripts/real-driverkit-dext-build-gate.py \
  --root . \
  --i-understand-local-driverkit-build \
  --output-under-host-report-bundle \
  --project apps/H1mekaRTXDriverKit/H1mekaRTXDriverKit.xcodeproj \
  --scheme H1mekaRTXHost \
  --configuration Debug \
  --derived-data-path host-report-bundle/real-driverkit-build/DerivedData
