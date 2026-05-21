# Task: Port Embedded Project from Raspberry Pi to NXP i.MX

## Objective
Perform a deep review of this project and port it from the Raspberry Pi platform (internal codename: Acadia) to the NXP i.MX platform (internal codename: Pinnacle).

## Source Platform
- Hardware: Raspberry Pi
- Codename: Acadia

## Target Platform
- Hardware: NXP i.MX
- Default board: FRDM i.MX 93 Development Board
- Codename: Pinnacle

## Requirements
- Conduct a complete review of the existing project structure, dependencies, build system, kernel configuration, device tree, drivers, userspace components, and any platform-specific code paths before making changes.
- Identify every Raspberry Pi / Acadia–specific dependency, including but not limited to: BCM SoC drivers, GPIO/I2C/SPI/UART peripheral mappings, bootloader (config.txt, cmdline.txt), Raspberry Pi OS packages, dtoverlays, VideoCore firmware, and any Pi-specific libraries.
- Replace each with the appropriate NXP i.MX 93 / FRDM equivalent, including but not limited to: i.MX 93 Arm Cortex-A55 + Cortex-M33 architecture, EdgeLock Secure Enclave, NPU (Ethos-U65), i.MX-specific peripheral mappings (LPUART, LPI2C, LPSPI, FlexCAN, ENET), U-Boot + ATF + OP-TEE boot flow, device tree (arch/arm64/boot/dts/freescale/imx93-*.dts), Yocto-based rootfs using meta-imx, and NXP BSP libraries.
- Remove all references to "Acadia" and "Raspberry Pi" throughout the codebase — source files, comments, documentation, build scripts, configuration files, variable/function/class names, log strings, and commit-relevant metadata.
- Replace all such references with "Pinnacle" / "NXP i.MX" / "i.MX 93" / "FRDM-IMX93" as appropriate to context.
- Ensure the ported project builds and runs correctly on the FRDM i.MX 93 Development Board as the default target.

## Reference Materials
- Use NXP's official i.MX Linux BSP, meta-imx Yocto layers, and the FRDM-IMX93 board documentation as the authoritative sources for repository, branch, and revision information.
- Align with the current NXP i.MX 93 BSP release for U-Boot, Linux kernel, ATF, OP-TEE, and firmware (ele-imx, imx-mkimage, etc.).

## Constraints
- Correctness is the highest priority. There is no time limit.
- Do not skip the review phase or take shortcuts on platform abstraction.
- Do not leave residual Acadia/Raspberry Pi references anywhere.
- Preserve original functionality and behavior unless an i.MX-specific change is required.
- Account for i.MX 93 heterogeneous architecture (A55 application cores + M33 real-time core) where the original Pi project assumed a single application-core domain.

## Deliverables
- A summary of the review findings (architecture, dependencies, Pi-specific surfaces identified).
- A migration plan mapping each Acadia component to its Pinnacle equivalent.
- The fully ported codebase targeting FRDM i.MX 93, built against the current NXP BSP.
- A changelog of all renames and reference removals.
- Build and flash instructions for the FRDM i.MX 93 Development Board.

---

# Pinnacle-OS

Yocto-based Linux OS for the **FRDM i.MX 93 Development Board** (NXP i.MX 93 SoC).

Built with [kas](https://kas.readthedocs.io/) against the NXP i.MX Linux BSP release **6.18.2-1.0.0** (`whinlatter`, Yocto 5.2).

| Component | Details |
|---|---|
| SoC | NXP i.MX 93 (Cortex-A55 + Cortex-M33) |
| Board | FRDM i.MX 93 (`imx93-11x11-lpddr4x-frdm`) |
| BSP release | 6.18.2-1.0.0 (`whinlatter`) |
| Yocto codename | whinlatter (5.2) |
| Distro | `fsl-imx-headless` |
| Image | `pinnacle-image` |
| Boot | U-Boot + ATF (TF-A) + OP-TEE + ele-imx firmware |
| OTA | SWUpdate A/B rootfs with U-Boot boot environment |
| kas version | 4.5 |

---

## Quick Start

### Prerequisites

- Docker (tested with Docker Engine 24+)
- `make`
- `curl` (for downloading `kas-container` on first run)
- `bmaptool` (for flashing — install via `apt install bmap-tools`)

### 1. Build the KAS Docker image

```bash
make kas-image
```

### 2. Build the Yocto OS image

```bash
make image frdm-imx93
```

Artifacts land in `deploy/images/frdm-imx93_<timestamp>/`.

### 3. Flash to SD card

```bash
make flash frdm-imx93 DEVICE=/dev/sdX
```

Replace `/dev/sdX` with the correct block device (e.g. `/dev/sdb`). The command
uses `bmaptool` for fast, verified flashing.

---

## All Make Targets

```
make <target> [board]

Yocto build:
  image               Build Yocto SD card image for BOARD  (alias for build)
  build               Build Yocto SD card image for BOARD
  rebuild-image       cleansstate image recipe, then rebuild
  sdk                 Build cross-toolchain SDK → deploy/sdk/
  esdk                Build extensible SDK → deploy/esdk/
  shell               Interactive kas shell in the build container
  swu                 Build .swu OTA package  [SWU_VERSION=YYYYMMDDHHMM]
  flash               Flash SD card / eMMC  (requires DEVICE=/dev/sdX)

Docker images:
  kas-image           Build/rebuild KAS build container  (docker/yocto/)
  ensure-image        Build KAS image only when absent
  sdk-image           Full chain: SDK build → stage → docker build → deploy
  esdk-image          Full chain: eSDK build → stage → docker build → deploy

Deployment:
  deploy-images       Copy .wic artifacts → deploy/images/BOARD_TS/
  deploy-sdk          Copy SDK installer   → deploy/sdk/BOARD_TS/
  deploy-esdk         Copy eSDK installer  → deploy/esdk/BOARD_TS/
  deploy-swu          Copy .swu package    → deploy/swu/BOARD_TS/

Clean:
  clean               Remove build/
  clean-docker        Remove kas/sdk/esdk Docker images
  clean-all           Remove build/, downloads/, sstate-cache/

Utilities:
  completion          Install bash tab-completion into ~/.bashrc

Boards:
  frdm-imx93
```

---

## Board: FRDM i.MX 93

| Key | Value |
|---|---|
| Yocto MACHINE | `imx93-11x11-lpddr4x-frdm` |
| kas board file | `kas/boards/frdm-imx93.yaml` |
| WKS file | `sdimage-imx93.wks` (A/B OTA layout) |
| Kernel image | `Image` |
| DTB | `imx93-11x11-lpddr4x-frdm.dtb` |
| Boot | U-Boot → ATF (BL31) → OP-TEE (BL32) → Linux (BL33) |

---

## Layer Stack

| Layer | Source | Purpose |
|---|---|---|
| `meta` (poky) | Yocto Project `whinlatter` | OpenEmbedded core |
| `meta-poky` | Yocto Project `whinlatter` | Poky distro policy |
| `meta-yocto-bsp` | Yocto Project `whinlatter` | Yocto reference BSPs |
| `meta-oe` | OpenEmbedded `whinlatter` | Extended recipes |
| `meta-python` | OpenEmbedded `whinlatter` | Python packages |
| `meta-networking` | OpenEmbedded `whinlatter` | Networking tools |
| `meta-multimedia` | OpenEmbedded `whinlatter` | Multimedia support |
| `meta-arm` | Yocto Project `whinlatter` | TF-A / OP-TEE |
| `meta-imx-bsp` | NXP `whinlatter-6.18.2-1.0.0` | i.MX SoC BSP |
| `meta-imx-sdk` | NXP `whinlatter-6.18.2-1.0.0` | NXP distros (`fsl-imx-*`) |
| `meta-swupdate` | sbabic `whinlatter` | SWUpdate OTA framework |
| `meta-pinnacle` | SiliconCentric `whinlatter` | Pinnacle application layer |

---

## Flashing the FRDM i.MX 93

### First-time SD card flash

```bash
# Build the image
make image frdm-imx93

# Flash (replace /dev/sdX with your SD card device)
make flash frdm-imx93 DEVICE=/dev/sdX
```

### OTA update via SWUpdate

1. Build the `.swu` package:
   ```bash
   make swu frdm-imx93
   # Output: build/frdm-imx93-<version>.swu
   ```

2. Push to a running device (web UI on port 8080, or via `swupdate-client`):
   ```bash
   curl -F "file=@build/frdm-imx93-<version>.swu" http://<device-ip>:8080/upload
   ```

3. The device reboots into the new slot. `swupdate-bootcheck.service` confirms the
   boot on first successful startup; if the new slot fails, U-Boot falls back to
   the previous slot on the next reboot.

---

## SDK / eSDK

Build and install the cross-compilation SDK into a Docker image:

```bash
# Cross-toolchain SDK
make sdk-image frdm-imx93

# Extensible SDK
make esdk-image frdm-imx93
```

---

## Tab Completion

```bash
# Add to ~/.bashrc
source /path/to/pinnacle-os/pinnacle-make-completion.bash

# Or install automatically
make completion
```

---

## NXP i.MX 93 Boot Flow

```
Power-on
  └─ ROM bootloader (on-chip)
       └─ ele-imx firmware (EdgeLock Secure Enclave — BL2)
            └─ U-Boot SPL (DDR init, clock init)
                 └─ ATF BL31 (EL3 secure monitor)
                      └─ OP-TEE BL32 (TEE OS — optional)
                           └─ U-Boot proper BL33 (boot environment, A/B selection)
                                └─ Linux kernel (Image + imx93-11x11-lpddr4x-frdm.dtb)
                                     └─ systemd → pinnacle-hal + pinnacle-client
```

---

## i.MX 93 Platform Notes

### Heterogeneous Architecture

The i.MX 93 contains two CPU domains:

| Domain | Core | Role |
|---|---|---|
| Application domain | 2× Cortex-A55 | Runs Linux + Pinnacle applications |
| Real-time domain | Cortex-M33 | Real-time / safety tasks (remoteproc/RPMsg) |

The Pinnacle-HAL and Pinnacle-Client run in the **application domain** under Linux.
M33 firmware (if used) is loaded via the Linux `remoteproc` driver.

### Peripheral Mapping (vs Raspberry Pi)

| Function | Raspberry Pi (Acadia) | i.MX 93 (Pinnacle) |
|---|---|---|
| UART | PL011 / mini-UART | LPUART (`lpuart1`–`lpuart8`) |
| I²C | BSC / `i2c-bcm2835` | LPI2C (`lpi2c1`–`lpi2c8`) |
| SPI | `spi-bcm2835` | LPSPI (`lpspi1`–`lpspi8`) |
| CAN | — | FlexCAN (`flexcan1`, `flexcan2`) |
| Ethernet | GENET | ENET-QOS / ENET1 |
| GPIO | `pinctrl-bcm2835` | `imx93-pinctrl` |
| Crypto | — | EdgeLock Secure Enclave (ele-imx) |
| NPU | — | Ethos-U65 |
| Boot env | `config.txt` / `cmdline.txt` | U-Boot environment (FAT `/boot.scr`) |
| Trusted exec | — | OP-TEE (BL32) |

---

## Migration Changelog

See [CHANGELOG.md](CHANGELOG.md) for a full record of all renames and reference removals.
