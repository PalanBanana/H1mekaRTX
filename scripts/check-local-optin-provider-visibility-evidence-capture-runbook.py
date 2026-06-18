#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'release-readiness'
OUT.mkdir(parents=True, exist_ok=True)

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding='utf-8'))

def add(checks, name, ok, detail=''):
    checks.append({'name': name, 'passed': bool(ok), 'detail': detail})

manifest_path = ROOT / 'tools/hackintosh/local-optin-provider-visibility-evidence-capture-runbook.json'
doc_path = ROOT / 'docs/hackintosh/local-optin-provider-visibility-evidence-capture-runbook.md'
manifest = read_json(manifest_path)
doc = doc_path.read_text(encoding='utf-8', errors='replace') if doc_path.exists() else ''

checks = []
add(checks, 'manifest_exists', manifest_path.exists(), str(manifest_path))
add(checks, 'doc_exists', doc_path.exists(), str(doc_path))
add(checks, 'manifest_schema', bool(manifest and manifest.get('schema') == 'h1mekartx.local_optin_provider_visibility_evidence_capture_runbook.v1'), 'manifest schema')

for field in ['rtx5070_target_retained', 'runbook_only']:
    add(checks, f'manifest_{field}_true', bool(manifest and manifest.get(field) is True), field)

false_fields = [
    'fallback_gpu_substitution_allowed',
    'commands_executed_by_this_phase',
    'raw_capture_parsed_by_this_phase',
    'raw_capture_committed',
    'private_paths_committed',
    'raw_stdout_committed',
    'raw_stderr_committed',
    'provider_open_attempted',
    'ioserviceopen_attempted',
    'bar_mapping_attempted',
    'bar0_read_attempted',
    'bar0_write_attempted',
    'bar_mmio_mutation_attempted',
    'configuration_writes_attempted',
    'firmware_load_attempted',
    'gpu_reset_attempted',
    'framebuffer_init_attempted',
    'display_engine_init_attempted',
    'gpu_command_submission_attempted',
    'metal_proof_claimed',
    'current_rtx5070_metal_acceleration_claimed',
    'current_rtx5070_ui_smoothness_claimed',
    'dock_transparency_blur_acceleration_claimed',
]
for field in false_fields:
    add(checks, f'manifest_{field}_false', bool(manifest and manifest.get(field) is False), field)

expected_pairs = [
    ('rtx5070_vendor_id', '0x10de'),
    ('rtx5070_device_id', '0x2f04'),
    ('rtx5070_iopcimatch', '0x2f0410de'),
    ('expected_driverkit_bundle_identifier', 'dev.h1meka.H1mekaRTXDriver'),
    ('capture_hard_opt_in_env', 'H1MEKARTX_ALLOW_READONLY_PROVIDER_VISIBILITY'),
    ('parse_hard_opt_in_env', 'H1MEKARTX_PARSE_LOCAL_PROVIDER_VISIBILITY_CAPTURE'),
    ('next_gate', 'phase62l-sanitized-provider-visibility-evidence-promotion-gate'),
]
for key, value in expected_pairs:
    add(checks, f'manifest_{key}', bool(manifest and manifest.get(key) == value), f'{key}={value}')

doc_tokens = [
    'This phase is runbook-only',
    'This phase does not execute provider visibility capture',
    'This phase does not parse raw capture',
    'This phase does not open a provider',
    'This phase does not call IOServiceOpen',
    'This phase does not map BAR memory',
    'This phase does not read BAR0',
    'This phase does not write BAR0',
    'This phase does not submit GPU commands',
    'This phase does not claim RTX 5070 Metal acceleration',
    'This phase does not claim Dock/transparency/blur acceleration',
    'H1MEKARTX_ALLOW_READONLY_PROVIDER_VISIBILITY=I_UNDERSTAND_READONLY_PROVIDER_VISIBILITY_ONLY',
    'H1MEKARTX_PARSE_LOCAL_PROVIDER_VISIBILITY_CAPTURE=I_UNDERSTAND_SANITIZED_READONLY_PROVIDER_VISIBILITY_PARSE_ONLY',
    'host-report-bundle/readonly-provider-visibility/',
]
for token in doc_tokens:
    add(checks, 'doc_contains_' + token.replace(' ', '_'), token in doc, token)

for forbidden in ['IOServiceOpen(', 'setpci', 'pciconf', 'ioreg -w', 'kmutil load', 'kextload', 'nvram ']:
    add(checks, 'doc_forbidden_absent_' + forbidden.replace(' ', '_'), forbidden not in doc, forbidden)

failed = sum(1 for c in checks if not c['passed'])
decision = 'PASS_LOCAL_OPTIN_PROVIDER_VISIBILITY_EVIDENCE_CAPTURE_RUNBOOK_READY' if failed == 0 else 'FAIL_LOCAL_OPTIN_PROVIDER_VISIBILITY_EVIDENCE_CAPTURE_RUNBOOK'

report = {
    'schema': 'h1mekartx.local_optin_provider_visibility_evidence_capture_runbook_check.v1',
    'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    'decision': decision,
    'rtx5070_target_retained': True,
    'fallback_gpu_substitution_allowed': False,
    'runbook_only': True,
    'commands_executed_by_this_phase': False,
    'raw_capture_parsed_by_this_phase': False,
    'provider_open_attempted': False,
    'ioserviceopen_attempted': False,
    'bar_mapping_attempted': False,
    'bar0_read_attempted': False,
    'bar0_write_attempted': False,
    'gpu_command_submission_attempted': False,
    'current_rtx5070_metal_acceleration_claimed': False,
    'current_rtx5070_ui_smoothness_claimed': False,
    'dock_transparency_blur_acceleration_claimed': False,
    'next_gate': 'phase62l-sanitized-provider-visibility-evidence-promotion-gate',
    'checks': checks,
}

(OUT / 'local-optin-provider-visibility-evidence-capture-runbook-check.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')

lines = []
lines.append('# Local Opt-In Provider Visibility Evidence Capture Runbook Check')
lines.append('')
lines.append(f'- Decision: `{decision}`')
lines.append('- RTX 5070 Target Retained: `True`')
lines.append('- Fallback GPU Substitution Allowed: `False`')
lines.append('- Runbook Only: `True`')
lines.append('- Commands Executed By This Phase: `False`')
lines.append('- Raw Capture Parsed By This Phase: `False`')
lines.append('- Provider Open Attempted: `False`')
lines.append('- IOServiceOpen Attempted: `False`')
lines.append('- BAR Mapping Attempted: `False`')
lines.append('- BAR0 Read Attempted: `False`')
lines.append('- BAR0 Write Attempted: `False`')
lines.append('- GPU Command Submission Attempted: `False`')
lines.append('- Current RTX 5070 Metal Acceleration Claimed: `False`')
lines.append('- Current RTX 5070 UI Smoothness Claimed: `False`')
lines.append('- Dock/Transparency/Blur Acceleration Claimed: `False`')
lines.append('- Next Gate: `phase62l-sanitized-provider-visibility-evidence-promotion-gate`')
lines.append('')
lines.append('## Checks')
lines.append('')
lines.append('| Check | Status | Detail |')
lines.append('| --- | --- | --- |')
for c in checks:
    status = 'PASS' if c['passed'] else 'FAIL'
    lines.append(f"| `{c['name']}` | {status} | {c['detail']} |")
(OUT / 'local-optin-provider-visibility-evidence-capture-runbook-check.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

print('Decision:', decision)
if failed:
    for c in checks:
        if not c['passed']:
            print('FAIL:', c['name'], '|', c['detail'])
raise SystemExit(0 if failed == 0 else 1)
