# OpenSUSE Linux USB Drive Partitioning Guide

## Quick Steps

Replace `X` in the commands below with your device letter (b, c, d, etc.):

```bash
# List all disks to find your USB device
sudo fdisk -l

# Unmount USB if mounted
sudo umount /dev/sdX1

# Create new partition table and partition
sudo fdisk /dev/sdX
# Type these commands in fdisk:
# d    (delete partition)
# n    (new partition)
# p    (primary)
# 1    (partition number)
# Enter (default first sector)
# Enter (default last sector)
# w    (write changes)

# Format the new partition
sudo mkfs.ext4 /dev/sdX1
```

---

## Detailed Instructions

### Prerequisites
- OpenSUSE Linux system
- Root privileges (sudo access)
- USB drive to partition

### 1. Identify Your USB Drive

```bash
# List all disk devices
sudo fdisk -l
```
Look for your USB drive - it will typically be listed as `/dev/sdX` where X is a letter (b, c, d, etc.).
The drive can be identified by its size and manufacturer information.

**Warning**: Make sure you identify the correct drive to avoid data loss!

### 2. Using fdisk (Command Line Method)

#### Start fdisk
```bash
sudo fdisk /dev/sdX  # Replace X with your device letter
```

#### Common fdisk Commands
- `m` - Show help menu
- `p` - Print partition table
- `d` - Delete a partition
- `n` - Create new partition
- `w` - Write changes to disk
- `q` - Quit without saving

#### Step-by-Step Process
1. Delete existing partitions:
   ```bash
   Command (m for help): d
   Partition number (1-4): 1
   ```
   Repeat for each partition

2. Create new partition:
   ```bash
   Command (m for help): n
   Partition type: p (primary)
   Partition number (1-4): 1
   First sector: [Press Enter for default]
   Last sector: [Press Enter for default]
   ```

3. Write changes:
   ```bash
   Command (m for help): w
   ```

### 3. Format the Partition

#### Common Filesystem Types
- ext4 (Linux standard):
  ```bash
  sudo mkfs.ext4 /dev/sdX1
  ```
- FAT32 (Cross-platform compatibility):
  ```bash
  sudo mkfs.vfat -F 32 /dev/sdX1
  ```
- NTFS (Windows compatibility):
  ```bash
  sudo mkfs.ntfs /dev/sdX1
  ```

### 4. Using parted (Alternative Method)
parted is another command-line tool that's more modern than fdisk:

```bash
# Start parted
sudo parted /dev/sdX

# Common parted commands
(parted) print         # Show current partition table
(parted) mklabel gpt  # Create new GPT partition table
(parted) mkpart primary ext4 0% 100%  # Create partition
(parted) quit
```

### 5. Using YaST (GUI Alternative)
1. Open YaST from system menu
2. Select "Partitioner"
3. Find your USB device
4. Use the graphical interface to:
   - Delete existing partitions
   - Create new partitions
   - Format partitions
   - Apply changes

## Tips
- Use `lsblk` to see block devices and their mount points
- Use `blkid` to see filesystem types and UUIDs
- Always unmount drives before partitioning:
  ```bash
  sudo umount /dev/sdX1
  ```

## Troubleshooting

### Common Issues
1. Device is busy:
   ```bash
   sudo fuser -m /dev/sdX  # Find processes using the device
   sudo umount -l /dev/sdX  # Force unmount if needed
   ```

2. Permission denied:
   - Ensure you're using sudo
   - Check if device is mounted
   - Verify device permissions

3. Device not showing up:
   ```bash
   sudo dmesg | tail  # Check system messages
   ```

### Safety Tips
- Always backup important data before partitioning
- Double-check device name before executing commands
- Use `lsblk` or `fdisk -l` to verify changes
- Never partition a mounted drive