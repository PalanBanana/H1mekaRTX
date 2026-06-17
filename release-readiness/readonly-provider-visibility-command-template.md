# Read-Only Provider Visibility Command Template

- Generated At UTC: `2026-06-17T22:29:09.941020+00:00`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Ready For Provider Match: `False`
- Missing Ready Field Count: `11`
- Commands Executed By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `phase62h-local-readonly-provider-visibility-capture-wrapper`

## Commands

### ioreg_search_rtx5070_pci_identity

```bash
ioreg -l -p IOService | grep -Ei '10de|2f04|0x2f0410de|H1mekaRTX|IOPCIDevice' | head -200
```

### ioreg_full_provider_visibility_readonly

```bash
ioreg -l -p IOService -r -n H1mekaRTXDriver 2>/dev/null || true
```

### systemextensions_list_readonly

```bash
systemextensionsctl list | grep -Ei 'H1mekaRTX|DriverKit|dev.h1meka' || true
```

### kmutil_loaded_readonly

```bash
kmutil showloaded | grep -Ei 'H1mekaRTX|DriverKit|dev.h1meka' || true
```

### driverkit_log_readonly_recent

```bash
log show --last 30m --style compact --predicate 'eventMessage CONTAINS[c] "H1mekaRTX" OR eventMessage CONTAINS[c] "DriverKit" OR eventMessage CONTAINS[c] "PCIDriverKit"' | tail -300
```

## Forbidden Tokens

- `IOServiceOpen`
- `ioreg -w`
- `nvram`
- `kextload`
- `kmutil load`
- `dd `
- `pciconf`
- `setpci`
- `ioreg -c IOPCIDevice -w`

## Missing Ready Fields

- `apple_developer_program_active`
- `apple_team_id_available`
- `driverkit_entitlement_request_submitted`
- `pcidriverkit_transport_entitlement_request_submitted`
- `system_extension_capability_requested`
- `host_app_id_configured`
- `driver_app_id_configured`
- `driverkit_entitlement_approved`
- `pcidriverkit_transport_entitlement_approved`
- `system_extension_capability_approved`
- `provisioning_profiles_regenerated_after_approval`
