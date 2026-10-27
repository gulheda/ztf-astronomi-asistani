# Türkçe sorgu değerlendirmesi ve kullanıcı çalışması taslağı

26 Ekim 2026 (ilk ölçüm 21 Ekim). [DENEY_PLANI.md](DENEY_PLANI.md) içindeki sorgu değerlendirmesinin ilk ölçümü ve kullanıcı pilotunun görev taslağı.

## Ölçüm

Küme: [tests/query_eval_set.json](../tests/query_eval_set.json), 104 sorgu (64 desteklenen, 2 bant belirtilmeden parlaklık sıralaması, 38 desteklenmeyen). Beklenen koşullar gramerden elle yazıldı. Beklenen sonuç kimlikleri, `parse_query` ve SQL kullanılmadan ayrı bir Python süzgeciyle hesaplandı. Çalıştırma: `python -m tests.query_eval`. Veri sentetik demo kayıtlarıdır; bu bir model veya bilimsel doğruluk ölçümü değildir.

| Ölçüt | Sonuç |
|---|---:|
| Koşul çözümleme (desteklenen, n=64) | 64/64 |
| Sonuç kümesi tam eşleşmesi (desteklenen, n=64) | 64/64 |
| Desteklenmeyen sorgunun açıkça reddi (bant belirtilmeden parlaklık sıralaması dahil, n=40) | 40/40 |
| Boş sonuçlu doğru sorgu | 5 |
| Yerel p50 / p95 (ayrıştırma + SQLite) | ≈0,05 ms / ≈0,14 ms |

Plan hedefleri (≥%90 tam eşleşme, sessiz filtre kaybı yok) bu kümede karşılandı. Bunlar proje kararıdır, bilimsel eşik değildir.

**Düzeltilen açıklar:** İlk ölçümde tek hata S21 idi: "adaylar" çoğulu tanınmıyordu. 22 Ekim'de beklenen davranış önce elle yazıldı (S31–S37, U25–U26 eklendi), ardından gramer genişletildi: "adaylar", "süpernovaları" ve "asteroidleri" biçimleri tanınıyor. S21 ve eklenen S31, S33, S35, S36 önceki gramerde reddediliyordu. Önceki oran (29/30) bu düzeltmeden önceki ölçümdür; yeni sonuç daha geniş ve bu açıklara bakılarak genişletilmiş bir kümedir, bu yüzden daha da iyimsel okunmalıdır. Küme yazarı sorguları grameri bilerek yazdığından oran iyimserdir: kullanıcıların kendi cümleleri pilotta toplanana kadar gerçek tanıma oranı bilinmiyor. **24 Ekim eklemesi:** Beklenen davranış önce elle yazıldı (S40–S45 desteklenen, U31–U32 reddedilen); altı desteklenen sorgu önceki gramerde reddediliyordu (ölçüm 39/45'e düşüyordu: koşul çözümleme %86,7). Gramer genişletildi: "saat/gün içinde" ve "içindeki" zaman ekleri, "adayı", "getir" ve "bana". "en parlak 5 olay" (ilk olmadan sayı) belirsiz olduğu için reddedilmeye devam ediyor. **25 Ekim eklemesi:** Beklenen davranış önce elle yazıldı (S46–S52 desteklenen, U33 reddedilen); altı desteklenen sorgu önceki gramerde reddediliyordu (ölçüm 46/52: %88,5). Gramer genişletildi: virgül ayırıcı ("son 24 saat, olaylar" önceden boş belirteçli "Desteklenmeyen ifade: ." hatası veriyordu), "olayı", Türkçe yazım "asteroit/asteroitler/asteroitleri" ve "saatlik/günlük" sıfat ekleri. "ve" virgülle de reddedilmeye devam ediyor. **26 Ekim eklemesi:** Beklenen davranış önce elle yazıldı (S53–S58 desteklenen, U34–U35 reddedilen); altı desteklenen sorgu önceki gramerde reddediliyordu (ölçüm 52/58: %89,7). Gramer genişletildi: "tane", "adet", "tüm", "bütün" dolgu sözcükleri (tek başına sorgu sayılmaz) ve "içerisinde/içerisindeki" zaman ekleri; sayı sınırları değişmedi ("ilk 0 tane olay" reddedilir). Önceki 37/37 ve 28/28 sayıları da yanlıştı: ölçüm çıktısı 39 desteklenen ve 32 reddedilen gösteriyordu. **27 Ekim eklemesi:** Beklenen davranış önce elle yazıldı (S59–S64 desteklenen, U36–U38 reddedilen); altı desteklenen sorgu önceki gramerde reddediliyordu (ölçüm 58/64: %90,6). Gramer genişletildi: "hafta" birimi (1 hafta = 168 saat; "haftadaki/haftalık"), tamlayan eki ("son 3 günün olayları") ve "adaylarını/olaylarını" belirtme biçimleri. Eski U10 ("son 1 hafta olaylar" reddi) bilinçli bir gramer kararıyla değişti: hafta artık desteklenir, aynı vaka "yıl" ile reddedilmeye devam eder; ay ve yıl desteklenmez.

Desteklenmeyen sorgu örnekleri (ay/yıl, mutlak tarih, koordinat, olumsuzlama, "ve") bilinçli olarak reddediliyor.

## Kullanıcı pilotu için görev taslağı

Henüz çalıştırılmadı. Veri kaynağı (issue #1) kesinleşmeden son görevler yazılamaz; aşağıdakiler kalıp görevlerdir. Her görev iki eşdeğer sürümde hazırlanır (A: geleneksel filtreli tablo, B: Türkçe asistan), sıra yarı yarıya dönüşümlü.

| Kod | Görev kalıbı | Beklenen davranış |
|---|---|---|
| G1 | Belirli zaman aralığındaki adayları bul | Süre penceresi doğru, sayı eşleşir |
| G2 | Bir bantta en parlak üç uyarıyı belirle | Bant belirtilmeden sıralama yapılamadığını fark etmek |
| G3 | Kaynağı belirtilmiş bir türdeki adayları listele | Tür etiketinin kaynağı okunur |
| G4 | Boş sonuç veren bir sorguyu yorumla | "Hata" ile "kayıt yok" ayırt edilir |
| G5 | Desteklenmeyen bir isteği (ör. "son 2 ay") yerine getir | Hata iletisinden yeniden ifade eder |

Kayıt alanları: anonim katılımcı kodu, koşul, görev kodu, doğru tamamlama (0/1), süre (sn), kullanıcı işlemi sayısı, hata sayısı, kısa geri bildirim. Ayrı not edilecekler: işlem sayısının neyi kapsadığı pilot öncesi yazılı tanımlanmalı; pilot (3 kişi) sonuçları nihai örneklemle karıştırılmaz; kurumun gerekli gördüğü etik/katılım süreci danışmanla netleştirilmeli.
