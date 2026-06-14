# Local Signing Run Instructions + Identity Selector Helper

## Decision

Phase 57A is required before Phase 57B.

The latest activation preflight decision was blocked until signed artifact verification is proven.

Therefore, the next safe path is:

1. select a local codesigning identity
2. run actual local signing with Phase 54 hard opt-in flags
3. rerun Phase 55 signed artifact verification sanitizer
4. rerun Phase 56 activation preflight
5. proceed to Phase 57B only if activation preflight becomes ready

## Local Signing Command Template

Replace SIGNING_IDENTITY_HERE with a real identity printed by the helper.

Command:

python3 scripts/actual-local-signing-hard-optin.py \
  --root . \
  --i-understand-local-signing \
  --signing-identity "SIGNING_IDENTITY_HERE" \
  --output-under-host-report-bundle

Then rerun:

./scripts/run-signed-artifact-verification-report-sanitizer.sh
./scripts/run-manual-activation-preflight-after-signed-verification.sh

## Activation Boundary

Do not run --submit-activation yet unless Phase 56 reports activation_preflight_ready=true.

Provider open remains blocked.

BAR mapping remains blocked.

GPU command submission remains blocked.

Dock/transparency/blur proof remains blocked.
