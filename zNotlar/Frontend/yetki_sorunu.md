Hataların Açıklaması

    Module not found: Error: Can't resolve 'reactstrap': Bu hata, React projenizin ViewSubmissionModal bileşeninde reactstrap kütüphanesini bulamadığını söylüyor. Yani, projenizde bu kütüphane yüklü değil.

    npm error code EACCES: Bu hatayı, npm install reactstrap bootstrap komutunu çalıştırdığınızda aldınız. Bu bir yetki (permission) hatasıdır. npm'in önbellek klasörüne (/tmp/npm-cache) yazma izniniz yok. Genellikle daha önce sudo ile npm komutu çalıştırıldığında bu durum oluşur. Hata mesajı çözümün ne olduğunu zaten söylüyor.

çözüm

sudo chown -R $(whoami) ~/.npm
sudo chown -R $(whoami) /tmp/npm-cache