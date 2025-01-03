# Windows 11 USB Drive Partitioning Guide

## Quick Steps
1. Press `Windows + X` → Select "Disk Management"
2. Right-click your USB drive partitions → Delete Volume
3. Right-click unallocated space → New Simple Volume
4. Follow wizard: set size → assign letter → format (NTFS/FAT32)
5. Click Finish

---

## Detailed Instructions

### Prerequisites
- A USB drive that you want to partition
- Windows 11 operating system
- Administrative privileges

## Steps to Partition USB Drive

### 1. Open Disk Management
1. Right-click on the Start button (Windows icon)
2. Select "Disk Management" from the menu
   - Alternatively, press `Windows + X` and select "Disk Management"
   - Or type "Create and format hard disk partitions" in the Windows search

### 2. Identify Your USB Drive
1. Look for your USB drive in the list of drives
2. Verify it's the correct drive by checking the size
   - **IMPORTANT**: Make sure you select the correct drive to avoid data loss

### 3. Delete Existing Partitions (if needed)
1. Right-click on each partition of the USB drive
2. Select "Delete Volume"
3. Click "Yes" to confirm
   - **Warning**: This will erase all data on the selected partition

### 4. Create New Partitions
1. Right-click on the unallocated space
2. Select "New Simple Volume"
3. Follow the New Simple Volume Wizard:
   - Choose partition size
   - Assign a drive letter
   - Format the partition (usually NTFS or FAT32)
   - Name your volume (optional)
4. Click "Finish"

### 5. Create Additional Partitions (if desired)
- Repeat step 4 for any remaining unallocated space
- Adjust partition sizes as needed

## Tips
- FAT32 is more compatible but limited to 4GB file size
- NTFS is Windows-native and supports larger files
- Consider ExFAT for cross-platform compatibility with large files

## Troubleshooting
- If you can't delete partitions, ensure the drive isn't in use
- If partition creation fails, try:
  1. Closing and reopening Disk Management
  2. Disconnecting and reconnecting the USB drive
  3. Using Command Prompt's `diskpart` utility as an alternative

## Alternative Method Using DiskPart
If Disk Management doesn't work, you can use Command Prompt:

1. Open Command Prompt as Administrator
2. Type `diskpart`
3. `list disk`
4. `select disk X` (replace X with your USB drive number)
5. `clean`
6. `create partition primary`
7. `format fs=ntfs quick`
8. `assign`

**Warning**: Be extremely careful with DiskPart commands as selecting the wrong disk can lead to data loss.