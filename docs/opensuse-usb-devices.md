# OpenSUSE USB and Storage Device Information Guide

This guide explains how to list and get detailed information about USB and storage devices on OpenSUSE Linux using various command-line tools.

## Prerequisites

Some tools required for device listing are not installed by default on OpenSUSE Tumbleweed. Install them using:

```bash
# Install usbutils for lsusb command
sudo zypper install usbutils

# Install util-linux for lsblk command
sudo zypper install util-linux
```
[thumbleweed manual](https://manpages.opensuse.org/Tumbleweed/util-linux-systemd/lsblk.8.en.html)

## Basic Device Listing

### List USB Devices
```bash
# List all USB devices
lsusb

# Show detailed information for all USB devices
lsusb -v

# Show USB device tree
lsusb -t
```

### List Block Devices
```bash
# List all block devices with basic info
lsblk

# Show full device information including filesystem type
lsblk -f

# Show device size information
lsblk -b

# Show device topology
lsblk -t
```

## Detailed Device Information

### Using udevadm
```bash
# Get detailed information about a specific device (replace sdX with your device)
udevadm info --query=all --name=/dev/sdX

# Monitor USB device events in real-time
udevadm monitor --udev --property
```

### Using blkid
```bash
# Show all block devices with UUID and filesystem type
sudo blkid

# Get information for a specific device
sudo blkid /dev/sdX
```

### Using dmesg
```bash
# Show recent device messages
dmesg | grep -i usb

# Watch for new USB device connections
dmesg -w | grep -i usb
```

## Storage Device Types

### Identify Device Types
```bash
# Show device types and models
lsblk -d -o name,rota,type,tran,model

# List only USB storage devices
lsblk -S | grep "usb"
```

The output columns mean:
- `rota`: 1 for rotational (HDD), 0 for non-rotational (SSD)
- `type`: disk, part (partition), rom, etc.
- `tran`: transport type (sata, usb, nvme)
- `model`: device model name

### Smart Status for Storage Devices
```bash
# Install smartmontools if not installed
sudo zypper install smartmontools

# Get SMART information for a device
sudo smartctl -i /dev/sdX

# Run SMART self-test
sudo smartctl -t short /dev/sdX
```

## Examples with Output

### Example: lsusb Output
```
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 003: ID 0781:5567 SanDisk Corp. Cruzer Blade
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```

### Example: lsblk Output
```
NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
sda      8:0    0 931.5G  0 disk 
├─sda1   8:1    0   512M  0 part /boot/efi
├─sda2   8:2    0    32G  0 part [SWAP]
└─sda3   8:3    0   899G  0 part /
sdb      8:16   1    32G  0 disk
└─sdb1   8:17   1    32G  0 part /media/usb
```

## Tips and Tricks

1. **Quick Device Identification**:
   ```bash
   # Combine tools for quick overview
   echo "=== USB Devices ==="; lsusb; echo -e "\n=== Block Devices ==="; lsblk -f
   ```

2. **Monitor Device Changes**:
   ```bash
   # Watch for device changes in real-time
   watch -n 1 lsblk
   ```

3. **Find Device Serial Numbers**:
   ```bash
   # Get serial numbers for USB devices
   lsusb -v 2>/dev/null | grep -A 2 -B 2 Serial
   ```

4. **Check Device Speed**:
   ```bash
   # Show USB device speed
   lsusb -t
   ```

## Troubleshooting

### Common Issues

1. **Device Not Showing Up**:
   ```bash
   # Check system messages
   dmesg | tail
   # Check USB controller status
   lspci | grep -i usb
   ```

2. **Permission Issues**:
   ```bash
   # Check device permissions
   ls -l /dev/sdX
   # Check if you're in the disk group
   groups
   ```

3. **USB Port Problems**:
   ```bash
   # Check USB host controllers
   lspci -v | grep -A 7 -i "usb"
   ```

### Safety Tips
- Always verify device names before running commands
- Use `sudo` when required
- Be careful with device names to avoid data loss
- Monitor system logs if devices aren't recognized