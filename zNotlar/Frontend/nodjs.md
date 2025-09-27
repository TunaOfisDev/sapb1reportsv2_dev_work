https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-ubuntu-22-04

Ubuntu 22.04.3 üzerine Node.js'in en güncel LTS (Long Term Support) sürümünü kurmak için aşağıdaki adımları takip edebilirsiniz. LTS sürümü, genellikle üretim ortamları için önerilen, uzun süreli desteklenen sürümdür.

1. **Curl ve diğer gerekli paketlerin kurulması:**
   Terminali açın ve `curl` gibi gerekli araçların kurulu olduğundan emin olun. Eğer `curl` kurulu değilse, aşağıdaki komutla kurun:

   ```bash
   sudo apt update
   sudo apt install curl
   ```

2. **Node.js Kurulum Scriptini İndirme:**
   NodeSource, Node.js'in Ubuntu için kolay bir kurulum scripti sağlar. Bu scripti `curl` ile indirin ve çalıştırın:

   ```bash
   curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
   ```

   Burada `setup_16.x` LTS sürümü için olan kurulum scriptidir. Eğer `20.9.0` gibi belirli bir sürüm kurmak istiyorsanız, bu sürüm NodeSource'da mevcut olmayabilir, çünkü NodeSource genellikle sadece LTS sürümleri için kurulum scriptleri sunar. 20.9.0 LTS olmadığı için, en son LTS sürümü için yukarıdaki scripti kullanmanız gerekecektir.

3. **Node.js'in Kurulması:**
   NodeSource kurulum scripti, Node.js için gerekli APT repository'sini ve anahtarını sisteminize ekledikten sonra, Node.js'i kurabilirsiniz:

   ```bash
   sudo apt install -y nodejs
   sudo apt install npm

   Bu komut, en güncel Node.js LTS sürümünü sisteminize kuracaktır.

4. **Kurulumun Doğrulanması:**
   Kurulumun başarılı olduğunu doğrulamak için, Node.js ve npm'in sürümlerini kontrol edin:

   ```bash
   node -v
   npm -v
   ```

   Bu komutlar, yüklü Node.js ve npm sürümlerini gösterecektir.

5. **Node.js'in Güncellenmesi (Opsiyonel):**
   Eğer belirli bir sürüm kurmak istiyorsanız ve bu sürüm NodeSource tarafından sağlanmıyorsa, `n` veya `nvm` (Node Version Manager) gibi bir sürüm yöneticisi kullanarak yükleyebilirsiniz. Ancak, bu yöntemlerle tam olarak `20.9.0` sürümünü kurmanız mümkün olmayabilir, çünkü Node.js sürümleri genellikle `x.y.z` formatında olup, `z` değeri genellikle önemli hata düzeltmelerini içerir.

Kurulumun tamamlanmasının ardından, Node.js ile geliştirmeye başlayabilirsiniz. Eğer belirttiğim adımlarla ilgili herhangi bir sorun yaşarsanız ya da daha spesifik bir sürüm kurmak istiyorsanız, lütfen bana bildirin, Selim. Size yardımcı olmaktan mutluluk duyarım.

react
Tabii ki, Selim. `/home/user/sapb1reports_v2/frontend` dizinine bir React projesi kurmak için aşağıdaki adımları izleyin:

1. **Proje Dizinine Git:**
   Terminalde önce `frontend` dizinine gidin:

   ```sh
   cd /home/user/sapb1reports_v2/frontend
   ```
   apt install npm 

   Bu komut, komut satırını React projesini oluşturmak istediğiniz klasöre yönlendirir.

2. **React Projesi Oluştur:**
   Şimdi, `create-react-app` aracını kullanarak yeni bir React projesi başlatın. Bu araç, React projeleri 
   için gerekli olan dosya ve klasör yapısını otomatik olarak oluşturur. Eğer `create-react-app` global olarak 
   yüklü değilse, ilk olarak aşağıdaki komutu kullanarak yükleyin:

   ```sh
   npm install -g create-react-app
   ```

   Global yüklemeyi tercih etmiyorsanız ya da root kullanıcısı olarak kurulum yapmak 
   istemiyorsanız, `npx` komutunu kullanarak tek seferlik bir işlem gerçekleştirebilirsiniz:

   ```sh
   npx create-react-app .
   ```

   Burada `.` (nokta), mevcut dizine yeni bir proje kurulmasını söyler. Eğer `frontend` klasörü boş değilse ve başka dosyalar içeriyorsa, bu komut hata verecektir. Eğer `frontend` dizini boş değilse ve yeni bir React projesi oluşturmak istiyorsanız, mevcut dosyaları yedekleyip başka bir yere taşımalı ya da silmelisiniz.

3. **Bağımlılıkları Yükleyin:**
   `create-react-app` komutu ayrıca projenin bağımlılıklarını yükler, bu yüzden bu adım otomatik olarak gerçekleşecektir. Bu işlem biraz zaman alabilir, bu süre boyunca internet bağlantınızın aktif olduğundan emin olun.

4. **Proje Başlatma:**
   Kurulum işlemi bittikten sonra, yeni oluşturulan React uygulamanızı başlatmak için aşağıdaki komutu kullanabilirsiniz:

   ```sh
   npm start
   ```

   Bu komut, yerel geliştirme sunucunuzu başlatır ve varsayılan web tarayıcınızda yeni React uygulamanızı otomatik olarak açar.

5. **Proje Yapısını İnceleyin:**
   Artık `frontend` dizininizde React projesinin dosya yapısı oluşturulmuş olacak. Örneğin, `src` klasörü, uygulamanızın kaynak kodlarını içeren yerdir.

6. **Proje İçin Git Repo Oluştur:**
   Eğer projeniz için versiyon kontrolü kullanmak istiyorsanız, `git` komutlarını kullanarak bir Git reposu başlatabilirsiniz.

   ```sh
   git init
   git add .
   git commit -m "Initial commit"
   ```

Bu adımları takip ederek, Ubuntu 22.04.3 sunucunuzda yeni bir React projesi başlatabilir ve geliştirmeye başlayabilirsiniz. React ve modern JavaScript ekosistemini öğrenmek, uygulama geliştirme sürecinize büyük değer katacak ve projelerinizi daha dinamik hale getirecektir. Herhangi bir sorunla karşılaşman durumunda yardımcı olmak için buradayım.

**sorun varsa node_modulues yeniden kurmak için
rm -rf node_modules
rm package-lock.json
npm install
**************************

react-table
React Table'ı daha kompakt ve işlevsel bir data table formatına getirmek için kullanabileceğiniz özellikleri adım adım sıralayacağım. Bu sıralama, tabloyu hem görsel olarak hem de işlevsel açıdan geliştirecek özellikleri kapsayacak:

1. **Basic Table Setup**: Temel tablo yapısını kurarak başlayın.
2. **Data Fetching**: Verilerinizi API veya başka bir kaynaktan çekmek.
3. **Columns Setup**: Sütunları tanımlayın, `Header` ve `accessor` kullanın.
4. **Sorting**: Verileri sıralamak için `useSortBy` hook'unu entegre edin.
5. **Filtering**: Filtreleme işlevselliği için `useFilters` hook'unu kullanın.
6. **Pagination**: Sayfalama yapısı kurmak için `usePagination` hook'unu kullanın.
7. **Resizable Columns**: Sütunların genişliklerinin ayarlanabilir olması.
8. **Sticky Columns**: Belli başlı sütunların sabit kalması.
9. **Custom Column Widths**: Her sütun için özel genişlikler tanımlayın.
10. **Row Selection**: Satır seçimi özellikleri ekleyin.
11. **Expandable Rows**: Genişleyebilir satırlar için yapılandırma.
12. **Conditional Row Styles**: Koşullu satır stilleri ekleyin.
13. **Custom Cell Renderers**: Özel hücre render fonksiyonları tanımlayın.
14. **Custom Header Components**: Özel başlık bileşenleri kullanın.
15. **Grouping**: Verileri gruplamak için `useGroupBy` hook'unu kullanın.
16. **Column Hiding**: Kullanıcıların sütunları gizlemesine olanak tanıyın.
17. **Column Ordering**: Sütun sıralamasını dinamik olarak değiştirme.
18. **Export Data**: Veriyi CSV veya Excel olarak dışa aktarma.
19. **Integrated Search**: Entegre arama özellikleri ekleyin.
20. **Aggregated Columns**: Sütunlar için toplu veri hesaplamaları.
21. **Server-side Processing**: Sunucu tarafında veri işleme için yapılandırma.
22. **Debounced Input**: Girişleri geciktirerek performansı artırın.
23. **Custom No-Data Component**: Özel "veri yok" bileşeni kullanın.
24. **Accessibility Enhancements**: Erişilebilirlik iyileştirmeleri yapın.
25. **Loading States**: Yükleme durumları için görsel belirteçler.
26. **Error Handling**: Hata yönetimi mekanizmaları kurun.
27. **Nested Tables**: İç içe tablolar için yapılandırma.
28. **Custom Pagination Component**: Özel sayfalama bileşeni kullanın.
29. **Memoization for Rows and Cells**: Satır ve hücreler için memoization kullanarak performansı artırın.
30. **Virtualized Rows**: Büyük veri setleri için sanal satır render etme.

1. **Custom Footer Components**: Her sütun için özel altbilgi bileşenleri kullanma.
2. **Column Pinning**: Kullanıcıların sütunları sayfanın başına veya sonuna sabitleyebilmesi.
3. **Draggable Columns**: Kullanıcıların sütun sıralamasını sürükleyip bırakarak değiştirebilmesi.
4. **Text Alignment in Columns**: Sütunlarda metin hizalaması seçenekleri.
5. **Highlighting Cells on Hover**: Fare ile üzerine gelindiğinde hücreleri vurgulama.
6. **Row Hover Effects**: Satır üzerine gelindiğinde görsel efektler ekleyebilme.
7. **Context Menu on Right Click**: Sağ tıklama ile açılan bağlam menüsü özellikleri.
8. **Heatmap Rendering**: Veri yoğunluğuna göre renk değişimleri ile heatmap görünümü.
9. **Row Grouping External Controls**: Dış kontroller ile satır gruplama özellikleri.
10. **Dynamic Cell Formatting Based on Data**: Veriye bağlı olarak dinamik hücre biçimlendirme.
11. **Integration with Chart Libraries**: Grafik kütüphaneleri ile entegrasyon.
12. **Undo/Redo Changes**: Değişiklikleri geri alma ve yeniden yapma.
13. **Data Validation**: Veri girişi sırasında veri doğrulama.
14. **Editable Cell Validation**: Düzenlenebilir hücreler için doğrulama kuralları.
15. **Tooltip Integration**: İpuçları için tooltip entegrasyonu.
16. **Column Visibility Toggles from a Dropdown**: Bir açılır menü üzerinden sütun görünürlüğü değiştirme.
17. **Customizable Loading Animations**: Özelleştirilebilir yükleme animasyonları.
18. **Multi-Language Support**: Çoklu dil desteği.
19. **Integration with Redux or MobX for State Management**: Durum yönetimi için Redux veya MobX ile entegrasyon.
20. **Custom Keyboard Shortcuts**: Özel klavye kısayolları.

