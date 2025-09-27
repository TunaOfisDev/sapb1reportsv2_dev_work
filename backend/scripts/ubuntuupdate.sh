# backend/scripts/ubuntuupdate.sh
#!/bin/bash

# Renk tanımlamaları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner fonksiyonu
print_banner() {
    echo -e "${BLUE}================================================"
    echo -e "     Ubuntu Sistem Güncelleme Scripti"
    echo -e "     Tarih: $(date '+%d-%m-%Y %H:%M:%S')"
    echo -e "================================================${NC}"
}

# Mesaj yazdırma fonksiyonu
print_message() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Hata kontrolü fonksiyonu
check_error() {
    if [ $? -ne 0 ]; then
        print_message "${RED}HATA: $1${NC}"
        exit 1
    else
        print_message "${GREEN}BAŞARILI: $1${NC}"
    fi
}

# **APT Önbellek Güncelleme**
update_apt_cache() {
    print_message "${YELLOW}APT önbelleği güncelleniyor...${NC}"
    sudo apt update
    check_error "APT önbellek güncellendi"
}

# **Sistem Güncelleme**
upgrade_system() {
    print_message "${YELLOW}Yükseltilebilir paketler listeleniyor...${NC}"
    apt list --upgradable

    print_message "${YELLOW}Sistem güncellemeleri yükleniyor...${NC}"
    sudo apt full-upgrade -y
    check_error "Sistem güncellemesi tamamlandı"
}

# **Gereksiz Paketleri Temizleme**
clean_old_packages() {
    print_message "${YELLOW}Gereksiz paketler temizleniyor...${NC}"
    sudo apt autoremove -y
    sudo apt autoclean
    check_error "Gereksiz paketler kaldırıldı"
}

# **Eski Kernel İmajlarını Temizleme**
clean_old_kernels() {
    print_message "${YELLOW}Eski kernel imajları temizleniyor...${NC}"
    sudo apt-get purge $(dpkg -l | awk '/^ii linux-image-[0-9]/ {print $2}' | grep -v $(uname -r)) -y
    check_error "Eski kernel temizliği tamamlandı"
}

# **Disk Alanını Kontrol Et**
check_disk_space() {
    local disk_usage=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')
    print_message "${YELLOW}Disk Kullanımı: ${disk_usage}%${NC}"

    if [ "$disk_usage" -gt 90 ]; then
        print_message "${RED}UYARI: Disk kullanımı %90'ın üzerinde! Güncellemeler disk alanını doldurabilir.${NC}"
        exit 1
    fi
}

# **Yeniden Başlatma Kontrolü**
check_reboot_required() {
    if [ -f /var/run/reboot-required ]; then
        print_message "${RED}Sistem yeniden başlatma gerektiriyor!${NC}"
        echo -e "${YELLOW}Sistem yeniden başlatılsın mı? (e/h)${NC}"
        read -r reboot_response
        if [[ "$reboot_response" =~ ^[Ee]$ ]]; then
            print_message "${YELLOW}Sistem yeniden başlatılıyor...${NC}"
            sudo reboot
        fi
    else
        print_message "${GREEN}Sistem yeniden başlatma gerektirmiyor.${NC}"
    fi
}

# **Ana Güncelleme İşlemi**
run_update() {
    print_banner
    check_disk_space

    echo -e "${YELLOW}Sistem güncellemesi başlatılsın mı? (e/h)${NC}"
    read -r response
    if [[ "$response" =~ ^[Ee]$ ]]; then
        update_apt_cache
        upgrade_system
        clean_old_packages
        clean_old_kernels
        check_reboot_required
    else
        print_message "${YELLOW}Güncelleme işlemi iptal edildi.${NC}"
    fi
}

# **Scripti çalıştır**
run_update
