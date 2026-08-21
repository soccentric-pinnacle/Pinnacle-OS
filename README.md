# Pinnacle-OS

## Project Summary

Pinnacle-OS is the Yocto/Kas build and release repository for a Pinnacle embedded Linux image.

The `kas` tree defines common configuration, the FRDM i.MX93 board, upstream layer revisions, and the `meta-pinnacle` layer alongside Poky, meta-openembedded, NXP, ARM, and update layers.

The repository provides:

- Dockerized Yocto, SDK, and eSDK workflows.
- A top-level Makefile and build completion script.
- Helper scripts for image and SDK operations.

`config` and board YAMLs hold build inputs rather than application runtime code.

The tracked feature material also includes a Pinnacle feature layer and an update-oriented layout, while `patch_health.py` checks patch state.

`REPO_MAP.md`, `req.md`, `CHANGELOG.md`, and `audit-report.md` document architecture, requirements, changes, and an explicit readiness assessment. That audit is important evidence of scope: the system has a defined embedded distribution build and update design, but it records gaps in bootloader-level A/B slot selection and related recovery behavior.

Those gaps prevent a blanket claim of production-ready failover.

The repository contains little conventional application source and no broad unit-test suite. Validation is primarily reproducible build configuration, layer parsing, patch-health checks, image generation, and target boot/update testing.

Kas container support reduces host variation, but successful execution still depends on network-fetched layers, toolchain availability, board configuration, storage layout, boot firmware, and physical hardware.

Use the documented Makefile targets and inspect `audit-report.md` before treating an image as release-ready.

## Feature Status

| # | Name / Description | Implemented? | Test Coverage? | Manual Test |
|---:|---|---|---|---|
| 1 | Yocto/Kas image configuration for Pinnacle | Yes | Configuration and build tooling exist; image build is environment-dependent | [ ] Manual verification required |
| 2 | FRDM i.MX93 board and upstream layer pins | Yes | YAML and layer metadata are present; hardware boot is not proven | [ ] Manual verification required |
| 3 | Pinnacle feature layer and image customization | Partial | Feature/config files exist; resulting image behavior needs target checks | [ ] Manual verification required |
| 4 | Dockerized Yocto, SDK, and eSDK workflows | Yes | Makefile and Docker helpers are present; full builds are not asserted here | [ ] Manual verification required |
| 5 | Patch-health and release audit tooling | Yes | `patch_health.py` and `audit-report.md` provide checks and findings | [ ] Manual verification required |
| 6 | Update and A/B recovery design | Partial | Requirements and audit evidence exist; bootloader slot selection has documented gaps | [ ] Manual verification required |

## Tests and Commands

Use the top-level Makefile for Kas/container builds, SDK generation, and patch-health checks. Consult `req.md` and `audit-report.md` for the release gate and known failures before flashing a board.

## Limitations

- A successful metadata parse or image build does not establish boot, peripheral support, secure update, rollback, or recovery.
- The audit's bootloader-level A/B limitations remain part of the current status.
