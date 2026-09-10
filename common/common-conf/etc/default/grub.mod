# If you change this file, run 'update-grub' afterwards to update
# /boot/grub/grub.cfg.
# For full documentation of the options in this file, see:
#   info -f grub -n 'Simple configuration'

GRUB_DEFAULT=0
GRUB_TIMEOUT_STYLE=menu
GRUB_TIMEOUT=5
GRUB_CMDLINE_LINUX_DEFAULT="amd_iommu=on iommu=pt default_hugepagesz=2M hugepagesz=2M hugepages=68544 swiotlb=262144 mitigations=off"
GRUB_CMDLINE_LINUX=""

