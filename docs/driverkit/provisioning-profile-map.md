# Provisioning Profile Map

## Purpose

Track future Host App and DriverKit provisioning profile requirements.

This stage is documentation-only.

## Host App

- Needs explicit App ID
- Needs System Extension install entitlement
- Needs development provisioning profile
- Needs bundle identifier aligned with Xcode target

## DriverKit Extension

- Needs explicit App ID
- Needs DriverKit entitlement
- Needs PCI transport entitlement
- Needs development provisioning profile
- Needs bundle identifier aligned with activation identifier

## RTX 5070 PCI Target

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de

## Boundary

This document does not enable real activation.

No graphics acceleration, MMIO writes, BAR access, GPU reset, GSP initialization, display engine initialization, framebuffer support, or Metal support is attempted.
