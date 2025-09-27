## Klavuz: Ürün Yapılandırması İçin İş Akışı

 1. Marka Tanımlaması (Brand)
   - Amacı: Marka, tüm yapılandırmanın en üst seviyesindeki hiyerarşik bir yapıdır.
   - İşlem Adımları:
     - Yeni bir marka oluştururken, markanın adı benzersiz olmalıdır.
     - Marka, doğrudan ürün gruplarına bağlanır ve bu sayede marka altında tüm gruplar ve ürünler organize edilir.
   - Kontrol Alanları:
     - Markanın `applicable_options` ilişkisi ile hangi seçeneklere uygun olduğunu belirleyin.
     - Marka bazlı sorular ve varyantlar `applicable_brands` alanı ile tanımlanmalıdır.

---

 2. Ürün Grupları Tanımlaması (ProductGroup)
   - Amacı: Marka altında gruplandırılmış ürün kategorilerini yönetir.
   - İşlem Adımları:
     - Her ürün grubu bir markaya bağlanmalıdır (`brand` alanı zorunludur).
     - Gruplar, altındaki kategorilerin genel özelliklerini organize eder.
   - Kontrol Alanları:
     - Ürün grubunun `applicable_options` ilişkisi ile seçeneklere uygunluğu tanımlanır.
     - Gruplara özel sorular, `applicable_groups` alanında tanımlanmalıdır.

---

 3. Kategori Tanımlaması (Category)
   - Amacı: Ürünleri bir marka ve grup içinde sınıflandırır.
   - İşlem Adımları:
     - Bir kategori bir marka ve ürün grubuna bağlı olmalıdır.
     - Kategoriler, ürün modellerinin hangi marka ve grupta yer aldığını gösterir.
   - Kontrol Alanları:
     - Kategori bazlı sorular `applicable_categories` ile ilişkilendirilir.
     - Kategorinin seçenekler ile bağlantısı `applicable_categories` alanında belirtilmelidir.

---

 4. Ürün Modeli Tanımlaması (ProductModel)
   - Amacı: Kategoriye bağlı, spesifik özelliklere sahip ürün modellerini temsil eder.
   - İşlem Adımları:
     - Ürün modeli bir kategoriye bağlanmalıdır.
     - Minimum ve maksimum fiyat aralığı gibi fiyatlandırma bilgileri belirtilmelidir.
   - Kontrol Alanları:
     - Ürün modeli bazlı sorular ve seçenekler `applicable_product_models` alanında ilişkilendirilmelidir.

---

 5. Sorular ve Seçenekler İlişkisi (Question-Option)
   - Amacı: Sorular ve seçenekler ile kullanıcıların seçimlerini yönlendirmek.
   - İşlem Adımları:
     - Sorular, ilgili marka, grup, kategori ve ürün modeline bağlanabilir.
     - Her soru için geçerli seçenekler `QuestionOptionRelation` modeli ile ilişkilendirilmelidir.
   - Kontrol Alanları:
     - Soruların `dependent_rules` ve `conditional_options` ile bağımlılıkları kontrol edilmelidir.
     - Soruların `is_visible` ve `is_applicable_for_variant` metotları ile uygunluğu belirlenmelidir.

---

 6. Bağımlı Soru Kuralları (DependentRule)
   - Amacı: Bir sorunun cevabına göre diğer soruları göstermek veya gizlemek.
   - İşlem Adımları:
     - Bağımlı soru kuralları `DependentRule` modeli ile tanımlanır.
     - Kural türü (`show_on_option` veya `hide_on_option`) seçilmelidir.
   - Kontrol Alanları:
     - Kuralın tetikleyici seçeneği (`trigger_option`) ve bağımlı sorular (`dependent_questions`) ilişkilendirilmelidir.
     - Her kuralın `evaluate` metodu ile uygunluğu test edilmelidir.

---

 7. Koşullu Seçenekler (ConditionalOption)
   - Amacı: Belirli seçeneklerin seçimlerine göre diğer seçenekleri tetiklemek.
   - İşlem Adımları:
     - Koşullu seçeneklerin `trigger_option_1` ve `trigger_option_2` alanları doldurulmalıdır.
     - `display_mode` (OVERRIDE veya APPEND) ve `logical_operator` (AND veya OR) seçilmelidir.
   - Kontrol Alanları:
     - `get_options` metodu ile hangi seçeneklerin görüntüleneceği belirlenir.

---

 8. Fiyat Çarpan Kuralları (PriceMultiplierRule)
   - Amacı: Belirli seçenek kombinasyonları için fiyat çarpanı belirlemek.
   - İşlem Adımları:
     - Tetikleyici seçenekler (`trigger_options`) ve hedef seçenekler (`target_options`) ilişkilendirilmelidir.
     - Çarpan faktörü (`multiplier_factor`) ve minimum tetikleyici sayısı tanımlanmalıdır.
   - Kontrol Alanları:
     - Çarpan kurallarının `evaluate` metodu ile geçerliliği test edilmelidir.

---

 9. Varyantlar ve Eski Bileşen Kodları
   - Amacı: Kullanıcının seçtiği seçeneklere göre varyant kodları ve tanımları oluşturmak.
   - İşlem Adımları:
     - Varyantlar oluşturulurken `Variant` modelindeki `text_answers` üzerinden eski bileşen kodları üretilmelidir.
     - `OldComponentCode` modelinin `generate_code` metodu ile kod üretimi yapılır.
   - Kontrol Alanları:
     - Tüm varyant ilişkileri `applicable_brands`, `applicable_categories` ve `applicable_product_models` alanları ile kontrol edilmelidir.

---

 10. İşlem Durum Takibi
   - Amacı: Tüm ilişkilerin tamamlanma durumunu izlemek.
   - İşlem Adımları:
     - `ProcessStatus` modeli ile ilişkilerin tamamlama yüzdesi hesaplanmalıdır.
     - `update_status` metodu ile tüm ilişkiler dinamik olarak kontrol edilmelidir.



