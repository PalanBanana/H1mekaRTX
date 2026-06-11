#!/usr/bin/env bash
set -euo pipefail

PROJECT="apps/H1mekaRTXProbeHost/H1mekaRTXProbeHost.xcodeproj"
HOST_SCHEME="H1mekaRTXProbeInstaller"
DRIVER_SCHEME="H1mekaRTXProbeHost"

HOST_ENTITLEMENTS="apps/H1mekaRTXProbeHost/H1mekaRTXProbeInstaller H1mekaRTXProbeInstaller/H1mekaRTXProbeInstaller_H1mekaRTXProbeInstaller.entitlements"
DRIVER_INFO="apps/H1mekaRTXProbeHost/H1mekaRTXProbeHost/Info.plist"
HOST_ACTIVATION="apps/H1mekaRTXProbeHost/H1mekaRTXProbeInstaller H1mekaRTXProbeInstaller/H1mekaRTXProbeActivationManager.swift"

echo "== H1mekaRTX signing readiness audit =="

echo
echo "== Toolchain =="
sw_vers || true
xcodebuild -version || true

echo
echo "== Required files =="
for f in "$PROJECT/project.pbxproj" "$HOST_ENTITLEMENTS" "$DRIVER_INFO" "$HOST_ACTIVATION"; do
  if [ -e "$f" ]; then
    echo "OK: $f"
  else
    echo "MISSING: $f"
  fi
done

echo
echo "== Host App entitlement =="
/usr/libexec/PlistBuddy -c "Print :com.apple.developer.system-extension.install" "$HOST_ENTITLEMENTS" 2>/dev/null || echo "MISSING: com.apple.developer.system-extension.install"

echo
echo "== DriverKit PCI match =="
/usr/libexec/PlistBuddy -c "Print :IOKitPersonalities" "$DRIVER_INFO" 2>/dev/null | grep -E "IOPCIMatch|2f0410de|IOProviderClass|IOPCIDevice" || true

echo
echo "== Activation identifier in Host App =="
grep -n "extensionIdentifier\|activationRequest\|deactivationRequest" "$HOST_ACTIVATION" || true

echo
echo "== Host App build settings =="
xcodebuild -project "$PROJECT" -scheme "$HOST_SCHEME" -configuration Debug -showBuildSettings 2>/dev/null | \
  grep -E "PRODUCT_BUNDLE_IDENTIFIER|CODE_SIGN_ENTITLEMENTS|DEVELOPMENT_TEAM|CODE_SIGN_STYLE|CODE_SIGN_IDENTITY|PROVISIONING_PROFILE" || true

echo
echo "== DriverKit build settings =="
xcodebuild -project "$PROJECT" -scheme "$DRIVER_SCHEME" -configuration Debug -showBuildSettings 2>/dev/null | \
  grep -E "PRODUCT_BUNDLE_IDENTIFIER|CODE_SIGN_ENTITLEMENTS|DEVELOPMENT_TEAM|CODE_SIGN_STYLE|CODE_SIGN_IDENTITY|PROVISIONING_PROFILE" || true

echo
echo "== Boundary =="
echo "Audit only. No activation. No MMIO. No BAR access. No GPU reset. No graphics acceleration."
