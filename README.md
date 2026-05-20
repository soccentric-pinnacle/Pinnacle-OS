# Raspberry Pi Yocto BSP

A fully containerised Yocto/OpenEmbedded build system for the entire Raspberry Pi family — from the original RPi 1 / Compute Module 1 through to the RPi 5 and CM5. Every build runs inside a Docker container via [kas](https://kas.readthedocs.io), so your host machine never needs Yocto dependencies installed.

Key features:
- **One `make` command** builds a flashable SD card image
- **A/B OTA updates** via SWUpdate with a built-in web UI (RPi 5 / CM5)
- **Systemd** init with DHCP Ethernet, Wi-Fi, and Bluetooth out of the box
- **gRPC + Protobuf** (C++ runtime, compiler, and Python bindings) pre-installed
- **Persistent `/home` partition** that survives OTA updates
- **Standard and extensible SDK** generation for cross-compilation
- **Bash tab-completion** for all `make` targets and board names

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Supported Boards](#supported-boards)
4. [Project Structure](#project-structure)
5. [Makefile Reference](#makefile-reference)
6. [KAS Configuration](#kas-configuration)
7. [Image Contents](#image-contents)
8. [Partition Layout (RPi 5 / CM5)](#partition-layout-rpi-5--cm5)
9. [OTA Updates with SWUpdate](#ota-updates-with-swupdate)
10. [SDK / Cross-Compilation](#sdk--cross-compilation)
11. [SDK Docker Images](#sdk-docker-images)
12. [First-Boot Services](#first-boot-services)
13. [Customising the Image](#customising-the-image)
14. [Bash Tab-Completion](#bash-tab-completion)
15. [Tips & Troubleshooting](#tips--troubleshooting)

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Docker | 20.10+ |
| GNU Make | 4.0+ |
| curl | any recent |
| bmaptool | for `make flash` |

No Yocto host dependencies (Python, BitBake, etc.) are required — everything runs inside the container.

---

## Quick Start

```bash
# 1. Clone the repository
git clone <this-repo> rpi && cd rpi

# 2. (Optional) install bash tab-completion
make completion && source ~/.bashrc

# 3. Build for Raspberry Pi 5 (default)
make image rpi5

# 4. Flash to SD card
make flash rpi5 DEVICE=/dev/sdX
```

The first build downloads all sources and populates the sstate cache — this takes a while. Subsequent builds for the same or a different board reuse the shared cache and are much faster.

---

## Supported Boards

Pass the board name directly after the target. The default is `rpi5`.

```bash
make image  rpi5       # build SD card image for RPi 5
make image  rpi4-64    # build for RPi 4 (64-bit)
make sdk    rpi5       # build cross-toolchain SDK for RPi 5
make esdk   rpi3-64    # build eSDK for RPi 3 (64-bit)
make shell  cm5        # open build shell for CM5
make flash  rpi5 DEVICE=/dev/sdb
```

| Board | Yocto `MACHINE` | SoC / Notes |
|----------|-----------------|-------------|
| `rpi5` *(default)* | `raspberrypi5` | BCM2712, Cortex-A76 64-bit, A/B OTA |
| `cm5` | `raspberrypi-cm5-io-board` | CM5 on IO Board, same SoC as RPi 5 |
| `rpi4-64` | `raspberrypi4-64` | BCM2711, Cortex-A72 64-bit |
| `rpi4` | `raspberrypi4` | BCM2711, Cortex-A72 32-bit |
| `rpi3-64` | `raspberrypi3-64` | BCM2837, Cortex-A53 64-bit |
| `rpi3` | `raspberrypi3` | BCM2837, Cortex-A53 32-bit |
| `rpi2` | `raspberrypi2` | BCM2836, Cortex-A7 32-bit |
| `rpi1` | `raspberrypi` | BCM2835, ARM1176 32-bit |
| `rpi0` | `raspberrypi0` | BCM2835, ARM1176 32-bit |
| `rpi0-wifi` | `raspberrypi0-wifi` | RPi Zero W, ARM1176 32-bit |
| `rpi0-2w` | `raspberrypi0-2w` | RPi Zero 2 W, Cortex-A53 32-bit |
| `rpi0-2w-64` | `raspberrypi0-2w-64` | RPi Zero 2 W, Cortex-A53 64-bit |
| `cm1` | `raspberrypi-cm` | Compute Module 1 |
| `cm3` | `raspberrypi-cm3` | Compute Module 3 |
| `rpi-armv7` | `raspberrypi-armv7` | Generic ARMv7 32-bit |
| `rpi-armv8` | `raspberrypi-armv8` | Generic ARMv8 64-bit |

**Examples:**

```bash
make image  rpi4-64
make flash  rpi4-64  DEVICE=/dev/mmcblk0
make sdk    rpi3-64
make shell  cm5
```

---

## Project Structure

```
rpi/
├── Makefile                    # Top-level build orchestration
├── kas-container               # kas helper script (auto-downloaded)
├── rpi-make-completion.bash    # Bash tab-completion script
│
├── kas/
│   ├── base.yaml               # Shared: repos, layers, local_conf defaults
│   ├── rpi5.yaml               # RPi 5 — includes base + A/B OTA WKS override
│   ├── cm5.yaml                # CM5 IO Board
│   ├── rpi4-64.yaml            # ... one file per board (all include base.yaml)
│   └── ...
│
├── docker/
│   ├── yocto/                  # KAS Yocto build container
│   │   ├── Dockerfile          # Extends kas:latest with bmap-tools, fdisk, etc.
│   │   └── Makefile
│   ├── sdk/                    # Standard SDK Docker image
│   │   ├── Dockerfile          # Ubuntu 22.04 + cross-toolchain SDK pre-installed
│   │   ├── Makefile
│   │   └── sdk.sh              # SDK installer (staged by 'make sdk-image')
│   └── esdk/                   # Extensible SDK Docker image
│       ├── Dockerfile          # Ubuntu 22.04 + eSDK + devtool pre-installed
│       ├── Makefile
│       └── esdk.sh             # eSDK installer (staged by 'make esdk-image')
│
├── meta/
│   └── meta-acadia/            # Project-specific Yocto layer
│       ├── conf/layer.conf
│       ├── recipes-core/
│       │   ├── images/core-image-full-cmdline.bbappend  # Image customisation
│       │   └── rpi5-home-init/  # Persistent /home first-boot init
│       ├── recipes-connectivity/
│       │   └── rpi5-connectivity/  # systemd-networkd, wpa_supplicant, Bluetooth
│       ├── recipes-kernel/
│       │   └── linux/linux-raspberrypi_6.6.bbappend  # Kernel pin + nobranch fix
│       ├── recipes-support/
│       │   └── expand-rootfs/  # First-boot partition expansion
│       ├── recipes-swupdate/
│       │   └── rpi5-swupdate-config/  # SWUpdate daemon config + boot-check
│       └── wic/
│           └── sdimage-rpi5.wks  # A/B OTA partition layout
│
├── layers/                     # Cloned by kas (not committed)
│   ├── poky/
│   ├── meta-openembedded/
│   ├── meta-raspberrypi/
│   └── meta-swupdate/
│
├── build/                      # BitBake build directory (not committed)
├── downloads/                  # Source tarballs shared across builds
└── sstate-cache/               # Shared state cache
```

---

## Makefile Reference

### Board Selection

Type the board name directly after the target — no prefix needed:

```bash
make image  rpi5
make sdk    rpi4-64
make esdk   rpi3-64
make shell  cm5
make flash  rpi5 DEVICE=/dev/sdb
```

The default board is `rpi5` when no board is specified.

### Yocto Build Targets

| Target | Description |
|--------|-------------|
| `image` | Build Yocto SD card image for `BOARD` — alias for `build` |
| `build` *(default)* | Ensure KAS container, build Yocto image, deploy to `deploy/images/` |
| `rebuild-image` | Clean sstate for `IMAGE_TARGET`, then rebuild |
| `sdk` | Build cross-toolchain SDK installer → `deploy/sdk/` (no Docker image) |
| `esdk` | Build extensible SDK installer → `deploy/esdk/` (no Docker image) |
| `shell` | Interactive kas/BitBake shell inside the build container |
| `swu` | Package a `.swu` OTA bundle from the latest `rootfs.ext4` |
| `flash` | Flash the latest `.wic.bz2` to `DEVICE` using bmaptool |

### Docker Image Targets

| Target | Description |
|--------|-------------|
| `kas-image` | Build/rebuild the KAS Yocto build container (`docker/yocto/`) |
| `ensure-image` | Build KAS image only if absent (used internally) |
| `sdk-image` | **Full chain**: `bitbake populate_sdk` → stage installer → `docker build` → deploy |
| `ensure-sdk-image` | Run `sdk-image` chain only when the image is absent |
| `esdk-image` | **Full chain**: `bitbake populate_sdk_ext` → stage installer → `docker build` → deploy |
| `ensure-esdk-image` | Run `esdk-image` chain only when the image is absent |

### Deployment Targets

Called automatically by the build targets above; can also be invoked manually.

| Target | Destination |
|--------|-------------|
| `deploy-images` | `deploy/images/BOARD_YYYYMMDD_HHMMSS/` |
| `deploy-sdk` | `deploy/sdk/BOARD_YYYYMMDD_HHMMSS/` |
| `deploy-esdk` | `deploy/esdk/BOARD_YYYYMMDD_HHMMSS/` |
| `deploy-swu` | `deploy/swu/BOARD_YYYYMMDD_HHMMSS/` |

### Clean Targets

| Target | Description |
|--------|-------------|
| `clean` | Remove `build/` |
| `clean-docker` | Remove all three Docker images (kas, sdk, esdk) |
| `clean-all` | Remove `build/`, `downloads/`, `sstate-cache/` |

### Utilities

| Target | Description |
|--------|-------------|
| `completion` | Install bash tab-completion into `~/.bashrc` |
| `help` | Print usage and board list |

### Boards

| Board | Description |
|-------|-------------|
| `rpi5` *(default)* | BCM2712, Cortex-A76 64-bit, A/B OTA |
| `rpi4-64` / `rpi4` | BCM2711, Cortex-A72 64/32-bit |
| `rpi3-64` / `rpi3` | BCM2837, Cortex-A53 64/32-bit |
| `rpi2` | BCM2836, Cortex-A7 32-bit |
| `rpi1` | BCM2835, ARM1176 32-bit |
| `rpi0` / `rpi0-wifi` | BCM2835, ARM1176 32-bit |
| `rpi0-2w` / `rpi0-2w-64` | RPi Zero 2 W, Cortex-A53 32/64-bit |
| `cm1` / `cm3` / `cm5` | Compute Modules |
| `rpi-armv7` / `rpi-armv8` | Generic ARMv7/ARMv8 |

---

## KAS Configuration

The kas configuration is split into two levels:

### `kas/base.yaml` — shared baseline

Defines all external layer repos (pinned to `scarthgap`) and the common `local.conf` settings applied to every board:

- `INIT_MANAGER = "systemd"`
- `IMAGE_FSTYPES = "wic.bz2 wic.bmap ext4"`
- `ENABLE_UART = "1"` / `GPU_MEM = "128"`
- Proprietary firmware licence acceptance
- Shared `DL_DIR` / `SSTATE_DIR` paths (bind-mounted by the container)
- `CONF_VERSION = "2"` (required by Poky sanity checks)

### `kas/<BOARD>.yaml` — per-board overrides

Each file includes `base.yaml` via `header.includes` and sets the `machine:` field. Boards that need a non-default `WKS_FILE` (currently `rpi5` and `cm5`) add a `local_conf_header` override.

**Adding a new board** is as simple as:

```yaml
# kas/my-custom-board.yaml
header:
  version: 14
  includes:
    - base.yaml

machine: my-custom-machine
```

Then run `make build my-custom-board`.

---

## Image Contents

The image is `core-image-full-cmdline` with the following additions from `meta-acadia`:

### Connectivity (`rpi5-connectivity`)
- **Ethernet** — DHCP via systemd-networkd (`10-eth.network`)
- **Wi-Fi** — wpa_supplicant on `wlan0` with VLAN-aware netdev/network units
- **Bluetooth** — bluez5 with rfkill / iw tools
- Edit `/etc/wpa_supplicant/wpa_supplicant-wlan0.conf` on the target to set your SSID and PSK

### OTA (`swupdate`, `rpi5-swupdate-config`)
- SWUpdate daemon with the Mongoose web server enabled
- Web UI on **port 8080** for drag-and-drop `.swu` delivery
- Boot-check service that confirms a successful boot and marks the slot healthy

### gRPC + Protobuf
- `protobuf`, `protobuf-compiler`, `protobuf-lite`
- `grpc`
- `python3-grpcio`, `python3-protobuf`

### User account
- Username: **`rpi`** / Password: **`rpi`**
- Member of the `sudo` group
- Home directory on the persistent `/home` partition (p4)

### Kernel
- Linux **6.6.x** pinned to `bba53a117a4a5c29da892962332ff1605990e17a`
- `nobranch=1` fetch workaround for force-pushed `rpi-6.6.y` branch

---

## Partition Layout (RPi 5 / CM5)

The custom WKS file (`meta-acadia/wic/sdimage-rpi5.wks`) creates a four-partition A/B layout optimised for 256 GB cards:

```
┌─────────────────────────────────────────────────────────────┐
│  p1  /boot      256 MB   FAT32   kernel, DTBs, config.txt   │
│  p2  /          8192 MB  ext4    rootfs-a  ← active slot    │
│  p3  (none)     8192 MB  ext4    rootfs-b  ← standby slot   │
│  p4  /home      512 MB*  ext4    persistent home            │
└─────────────────────────────────────────────────────────────┘
* Expanded to fill the card on first boot by rpi5-home-init
```

All other boards use the standard `sdimage-raspberrypi.wks` from `meta-raspberrypi` (single-slot, no A/B OTA).

---

## OTA Updates with SWUpdate

### Generating a `.swu` package

```bash
# After a successful build:
make swu                          # version = current timestamp
make swu SWU_VERSION=1.2.3        # explicit version string
```

The package is written to `build/rpi5-<VERSION>.swu`.

### Delivering the update

**Web UI (recommended):**
```
http://<device-ip>:8080
```
Drag and drop the `.swu` file onto the upload area. SWUpdate will write the new rootfs to the inactive slot, update `/boot/cmdline.txt`, and reboot automatically.

**CLI push:**
```bash
swupdate-client -v <device-ip> build/rpi5-<VERSION>.swu
```

### How it works

1. **pre-install.sh** — detects the currently active slot (`/dev/mmcblk0p2` or `p3`) and creates a `/dev/swupdate-inactive` symlink pointing at the other slot.
2. The SWUpdate `raw` handler streams `rootfs.ext4.gz` directly onto the inactive partition.
3. **post-install.sh** — resolves the `PARTUUID` of the newly written partition, remounts `/boot` read-write, patches `root=PARTUUID=…` in `/boot/cmdline.txt`, then restores `/boot` to read-only.
4. SWUpdate triggers a reboot; the RPi firmware boots the new slot.
5. **swupdate-bootcheck.service** — runs once after the reboot, confirms the system came up healthy, and marks the slot permanent.

---

## SDK / Cross-Compilation

### Standard SDK

Generates a self-contained installer (`*.sh`) containing the cross-toolchain and target sysroot:

```bash
make sdk rpi5
# Installer deployed to: deploy/sdk/rpi5_YYYYMMDD_HHMMSS/
```

Install and activate on any host machine:
```bash
./poky-glibc-x86_64-*.sh -d ~/rpi-sdk
source ~/rpi-sdk/environment-setup-*
aarch64-poky-linux-gcc --version
```

### Extensible SDK (eSDK)

Includes `devtool`, recipe management, and a full layer checkout:

```bash
make esdk rpi5
# Installer deployed to: deploy/esdk/rpi5_YYYYMMDD_HHMMSS/
```

Use `devtool add <recipe> <source>` to iterate on recipes without a full rebuild.

---

## SDK Docker Images

For teams that want a fully pre-configured container with the SDK already installed, two additional Docker images are provided.

### SDK image (`docker/sdk/`)

A single command runs the full chain — Yocto SDK build, installer staging, Docker image build, and deployment:

```bash
make sdk-image rpi5
```

What happens internally:
1. Ensure the KAS build container is present
2. Run `bitbake -c populate_sdk` inside the container
3. Locate the generated `.sh` installer and copy it to `docker/sdk/sdk.sh`
4. Build the `rpi5-sdk:latest` Docker image (Ubuntu 22.04 + SDK at `/opt/poky/sdk`)
5. Deploy the installer to `deploy/sdk/rpi5_YYYYMMDD_HHMMSS/`

Using the SDK container:
```bash
docker run --rm -it rpi5-sdk:latest
# Inside the container:
source /opt/poky/sdk/environment-setup-*
aarch64-poky-linux-gcc --version
```

Override the install path or image name:
```bash
# These internal variables are rarely needed
make sdk-image rpi5 SDK_INSTALL_DIR=/opt/my-sdk
```

### eSDK image (`docker/esdk/`)

Same chain for the extensible SDK:

```bash
make esdk-image rpi5
```

What happens internally:
1. Ensure the KAS build container is present
2. Run `bitbake -c populate_sdk_ext` inside the container
3. Locate the generated `*-ext-*.sh` installer and copy it to `docker/esdk/esdk.sh`
4. Build the `rpi5-esdk:latest` Docker image (Ubuntu 22.04 + eSDK at `/opt/poky/esdk`)
5. Deploy the installer to `deploy/esdk/rpi5_YYYYMMDD_HHMMSS/`

Using the eSDK container:
```bash
docker run --rm -it rpi5-esdk:latest
# Inside the container:
source /opt/poky/esdk/environment-setup-*
devtool add my-recipe ~/src/my-project
```

### Conditional rebuild

```bash
# Only builds if the image does not already exist in Docker
make ensure-sdk-image
make ensure-esdk-image
```

### `kas-image` — force-rebuild the KAS Docker image

```bash
make kas-image
```

### Removing all Docker images

```bash
make clean-docker   # removes rpi5-kas, rpi5-sdk, and rpi5-esdk images
```

---

## First-Boot Services

Two one-shot systemd services run on the very first boot:

### `rpi5-home-init.service`
The persistent `/home` partition (p4) is an empty ext4 filesystem at flash time. This service detects the empty mount, creates `/home/rpi` with correct ownership, and copies `/etc/skel` so the `rpi` user can log in immediately. It disables itself after running once.

### `expand-rootfs.service`
Grows the root partition to fill the available SD card space using `parted` + `resize2fs`. Required because the `.wic` image is built with a fixed partition size for the active rootfs slot. This service also disables itself after running once.

---

## Customising the Image

### Adding packages

Edit `meta/meta-acadia/recipes-core/images/core-image-full-cmdline.bbappend`:

```bitbake
IMAGE_INSTALL:append = " my-package another-package"
```

Then run:
```bash
make rebuild-image rpi5
```

### Adding a new recipe

Place it under `meta/meta-acadia/recipes-<category>/<name>/<name>.bb`. The layer's `conf/layer.conf` auto-discovers all `recipes-*/*/*.bb` files.

### Configuring Wi-Fi credentials

After flashing, mount the root partition and edit:
```
/etc/wpa_supplicant/wpa_supplicant-wlan0.conf
```
Or build the credentials directly into the image by modifying `recipes-connectivity/rpi5-connectivity/files/wpa_supplicant-wlan0.conf`.

### Pinning or updating the kernel

Edit `meta/meta-acadia/recipes-kernel/linux/linux-raspberrypi_6.6.bbappend` and update `SRCREV_machine` to the desired commit hash.

### Changing the Poky/layer branch

All external layers are pinned to the **scarthgap** (Yocto 5.0 LTS) branch in `kas/base.yaml`. Update `branch:` and `commit:` fields there and re-run `make build`.

---

## Bash Tab-Completion

```bash
make completion   # appends source line to ~/.bashrc
source ~/.bashrc
```

After activation, pressing `<Tab>` completes:

| Input | Completions |
|-------|-------------|
| `make <Tab>` | all targets |
| `make image <Tab>` | board names |
| `make sdk <Tab>` | board names |
| `make esdk <Tab>` | board names |
| `make flash <Tab>` | board names |

Board names are read dynamically from `kas/boards/`, so new boards are automatically available without editing the completion script.

---

## Tips & Troubleshooting

### Speed up rebuilds with a shared sstate cache

The `DL_DIR` and `SSTATE_DIR` directories are mounted into the container and shared across all `BOARD` builds. A populated cache from one board dramatically speeds up subsequent builds for related boards that share packages.

### Interactive BitBake shell

```bash
make shell rpi4-64
# Inside the container:
bitbake core-image-full-cmdline
bitbake -c devshell my-recipe
bitbake-layers show-layers
```

### Inspecting build logs

```bash
# After a failed build:
cat build/tmp/work/<arch>/<recipe>/<version>/temp/log.do_<task>.*
```

### `CONF_VERSION` mismatch error

If you see `NotImplementedError: Your version of local.conf was generated from an older/newer version`, ensure `CONF_VERSION = "2"` is present in `kas/base.yaml`. KAS regenerates `build/conf/local.conf` on every invocation, so manual edits to that file are overwritten.

### `kas shell` command syntax

Pass commands to the kas shell with `-c "..."`, not `-- ...`:
```bash
# Correct
kas-container shell kas/rpi5.yaml -c "bitbake my-recipe"
# Wrong (kas 5.x rejects this)
kas-container shell kas/rpi5.yaml -- bitbake my-recipe
```

### Docker images are stale

```bash
make kas-image        # force-rebuild the KAS Yocto build container
make sdk-image rpi5   # rebuild the SDK Docker image (re-runs full chain)
make esdk-image rpi5  # rebuild the eSDK Docker image (re-runs full chain)
make clean-docker     # remove all three images (kas + sdk + esdk)
```

### Freeing disk space

```bash
make clean        # removes build/ (~50–100 GB)
make clean-all    # also removes downloads/ and sstate-cache/
make clean-docker # removes Docker images
```
