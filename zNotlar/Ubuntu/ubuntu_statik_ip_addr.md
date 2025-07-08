sudo chmod 600 /etc/netplan/01-netcfg.yaml

sudo nano /etc/netplan/01-netcfg.yaml


*************

network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.1.xxx/24  # xxx, sanal makinenize atamak istediğiniz IP'nin son oktetidir.
      gateway4: 192.168.1.1
      nameservers:
        addresses: [192.168.1.1, 8.8.8.8]




************
sudo netplan apply
