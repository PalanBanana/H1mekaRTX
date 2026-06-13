# Project Generator Output Allowlist

- Generated At UTC: `2026-06-13T15:58:10.324433+00:00`
- Classification: `CLASSIFICATION_PROJECT_GENERATOR_OUTPUT_ALLOWLIST_GATE`
- Output Allowlist Report Only: `True`
- Promotion Gate Only: `True`
- Real Xcodeproj Generation Attempted: `False`
- Real PBXProj Generation Attempted: `False`
- Xcode Invocation Attempted: `False`
- Xcodebuild Invocation Attempted: `False`
- Build Attempted: `False`
- Signing Attempted: `False`
- Install Attempted: `False`
- DriverKit Activation Attempted: `False`
- System Extension Activation Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR/MMIO Mutation Attempted: `False`
- Real GPU Command Execution Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Allowed Dry-Run Outputs

| Path | Status |
| --- | --- |
| `tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-dryrun-manifest.json` | ALLOWED_DRYRUN_OUTPUT |
| `tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-dryrun-manifest.md` | ALLOWED_DRYRUN_OUTPUT |
| `tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-output-allowlist.json` | ALLOWED_DRYRUN_OUTPUT |
| `tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-output-allowlist.md` | ALLOWED_DRYRUN_OUTPUT |
| `release-readiness/nonbuilding-project-generator-dryrun-check.json` | ALLOWED_DRYRUN_OUTPUT |
| `release-readiness/nonbuilding-project-generator-dryrun-check.md` | ALLOWED_DRYRUN_OUTPUT |
| `release-readiness/project-generator-output-allowlist-gate-check.json` | ALLOWED_DRYRUN_OUTPUT |
| `release-readiness/project-generator-output-allowlist-gate-check.md` | ALLOWED_DRYRUN_OUTPUT |

## Forbidden Real Project Outputs

| Path | Status |
| --- | --- |
| `tools/driverkit-xcode-layout/H1mekaRTXDriverKit.xcodeproj` | FORBIDDEN_REAL_PROJECT_OUTPUT |
| `tools/driverkit-xcode-layout/H1mekaRTXDriverKit.xcodeproj/project.pbxproj` | FORBIDDEN_REAL_PROJECT_OUTPUT |
| `H1mekaRTXDriverKit.xcodeproj` | FORBIDDEN_REAL_PROJECT_OUTPUT |
| `H1mekaRTXDriverKit.xcodeproj/project.pbxproj` | FORBIDDEN_REAL_PROJECT_OUTPUT |

## Conclusion

This allowlist gate permits dry-run metadata/report outputs only. Real `.xcodeproj`, real `project.pbxproj`, Xcode/xcodebuild, build, signing, install, DriverKit activation, System Extension activation, provider open, BAR mapping, GPU command submission, UI compositor proof, and Metal proof remain blocked.
