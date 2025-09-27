# Disk kullanımını özetle
df -hT

# LVM yapılarını görüntüle
sudo lvs
sudo vgs
sudo pvs

# EXT4 canlı fs kontrol
sudo tune2fs -l /dev/mapper/ubuntu--vg-ubuntu--lv | grep -i 'block\|size'

# En büyük klasörleri gör
sudo du -h --max-depth=2 /var | sort -hr | head -n 15
