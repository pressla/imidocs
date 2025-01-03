# Important precoditions

## 1. disable swap files for the node:

```bash
free -h
cat /proc/swaps
```
```bash

# Edit /etc/fstab and comment out any swap lines
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

```