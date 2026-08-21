# Pinnacle-OS Build and Deployment

## Purpose and scope

Pinnacle-OS is the NXP i.MX 93 Yocto build orchestration repository. The root Makefile drives KAS in Docker for the `frdm-imx93` board, builds the `pinnacle-image`, produces SDK/eSDK installers, creates SWUpdate OTA packages, flashes WIC images, and copies artifacts into timestamped `deploy/` directories.

## 1. Prerequisites

- Linux host with GNU Make, Docker, `curl`, `grep`, `awk`, `find`, `gzip`, `cpio`, `openssl`, and `bmaptool` for the relevant targets.
- Docker daemon and enough disk/network capacity for Yocto downloads, `build/`, `downloads/`, and `sstate-cache/`.
- KAS container support; `make kas-container-script` downloads KAS `4.5` from the pinned Siemens release URL.
- For flashing: a validated `.wic.bz2`, matching `.bmap`, and a removable block device path. Root/device permissions may be required.
- The selected board must match `kas/boards/<BOARD>.yaml`; the tracked board is `frdm-imx93`, machine `imx93-11x11-lpddr4x-frdm`.

## 2. Setup

Download the pinned helper if needed and inspect target help:

```bash
make kas-container-script
make help
```

Board can be positional, as shown below, or the default `frdm-imx93` can be used. Override `BUILD_DIR`, `DL_DIR`, `SSTATE_DIR`, `DEPLOY_DIR`, and image names with Make variables when isolating caches.

## 3. Build and compile

Build the Yocto image and automatically stage WIC artifacts:

```bash
make build frdm-imx93
# equivalent image alias:
make image frdm-imx93
```

Rebuild the image recipe from cleansstate:

```bash
make rebuild-image frdm-imx93
```

Open a shell in the KAS environment:

```bash
make shell frdm-imx93
```

The KAS image defaults to `imx93frdm-kas:latest`; `IMAGE_TARGET` defaults to `pinnacle-image`. These targets require Docker, network access, and substantial Yocto build time.

## 4. Test and lint

The root Makefile defines no unit-test, lint, or static-analysis target. Build success is the available automated compile check. KAS/BitBake task diagnostics must be run from `make shell frdm-imx93` as appropriate. Boot, service, OTA, and peripheral validation are manual.

## 5. Packaging and artifacts

Cross-toolchain SDK:

```bash
make sdk frdm-imx93
make sdk-image frdm-imx93
```

Extensible SDK:

```bash
make esdk frdm-imx93
make esdk-image frdm-imx93
```

SDK/eSDK installers are staged from `build/tmp/deploy/sdk/` and copied to timestamped `deploy/sdk/<BOARD>_<timestamp>/` or `deploy/esdk/<BOARD>_<timestamp>/`. The SDK Docker images default to `imx93frdm-sdk:latest` and `imx93frdm-esdk:latest`.

Create an OTA SWU:

```bash
make swu frdm-imx93
make swu frdm-imx93 SWU_VERSION=1.2.3
```

This packages rootfs, optional kernel/DTB, pre/post install scripts, and signs `sw-description` only when `meta/meta-pinnacle/swupdate/keys/swupdate-private.pem` exists. Otherwise it deliberately creates an unsigned SWU and warns. The result is `build/<BOARD>-<SWU_VERSION>.swu` and is copied to `deploy/swu/<BOARD>_<timestamp>/`.

## 6. Deployment, install, and run

Flash the latest WIC image to a block device only after verifying the device path:

```bash
make flash frdm-imx93 DEVICE=/dev/sdX
```

The target requires a block device and uses `bmaptool`; it can destroy the selected device. There is no root Makefile target for installing the SDK or starting the resulting OS services. After flashing or OTA installation, boot the board and manually verify partitions, services, networking, WebConfig, Client/HAL integration, and update rollback behavior.

Generate SWUpdate keys once when signing is authorized:

```bash
./scripts/generate-swu-keys.sh
```

The script refuses to overwrite an existing private key. Protect the private key and do not commit or distribute it casually.

## 7. Cleanup

```bash
make clean
make clean-build
make clean-docker
make clean-all
```

`clean`/`clean-build` remove `build/`; `clean-docker` removes the KAS, SDK, and eSDK images; `clean-all` also removes `downloads/` and `sstate-cache/`, which forces expensive redownloads. Use `completion` only if modifying `~/.bashrc` is intended.

## 8. Hardware, cloud, and manual verification caveats

- Yocto compilation and emulated tooling do not prove bootability or peripheral behavior on the i.MX 93 board.
- `flash` is destructive and must be manually reviewed against the actual removable media path.
- SWU signing is conditional on a private key; unsigned OTA packages must not be promoted to production.
- Validate boot, secure transport, first boot provisioning, persistent data, A/B update behavior, power interruption recovery, device peripherals, and fleet/remote-update integration on physical hardware.
- Cloud credentials, artifact publication, OTA server delivery, and production signing custody are outside this Makefile.
