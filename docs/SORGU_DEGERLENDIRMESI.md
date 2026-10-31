# Türkçe sorgu değerlendirmesi ve kullanıcı çalışması taslağı

30 Ekim 2026 (ilk ölçüm 21 Ekim). [DENEY_PLANI.md](DENEY_PLANI.md) içindeki sorgu değerlendirmesinin ilk ölçümü ve kullanıcı pilotunun görev taslağı.

## Ölçüm

Küme: [tests/query_eval_set.json](../tests/query_eval_set.json), 137 sorgu (88 desteklenen, 49 desteklenmeyen; bunların 2'si bant belirtilmeden parlaklık sıralaması). Beklenen koşullar gramerden elle yazıldı. Beklenen sonuç kimlikleri, `parse_query` ve SQL kullanılmadan ayrı bir Python süzgeciyle hesaplandı. Çalıştırma: `python -m tests.query_eval`. Veri sentetik demo kayıtlarıdır; bu bir model veya bilimsel doğruluk ölçümü değildir.

| Ölçüt | Sonuç |
|---|---:|
| Koşul çözümleme (desteklenen, n=88) | 88/88 |
| Sonuç kümesi tam eşleşmesi (desteklenen, n=88) | 88/88 |
| Desteklenmeyen sorgunun açıkça reddi (bant belirtilmeden parlaklık sıralaması dahil, n=49) | 49/49 |
| Boş sonuçlu doğru sorgu | 7 |
| Yerel p50 / p95 (ayrıştırma + SQLite) | ≈0,05 ms / ≈0,14 ms |

Plan hedefleri (≥%90 tam eşleşme, sessiz filtre kaybı yok) bu kümede karşılandı. Bunlar proje kararıdır, bilimsel eşik değildir.

**Düzeltilen açıklar:** İlk ölçümde tek hata S21 idi: "adaylar" çoğulu tanınmıyordu. 22 Ekim'de beklenen davranış önce elle yazıldı (S31–S37, U25–U26 eklendi), ardından gramer genişletildi: "adaylar", "süpernovaları" ve "asteroidleri" biçimleri tanınıyor. S21 ve eklenen S31, S33, S35, S36 önceki gramerde reddediliyordu. Önceki oran (29/30) bu düzeltmeden önceki ölçümdür; yeni sonuç daha geniş ve bu açıklara bakılarak genişletilmiş bir kümedir, bu yüzden daha da iyimsel okunmalıdır. Küme yazarı sorguları grameri bilerek yazdığından oran iyimserdir: kullanıcıların kendi cümleleri pilotta toplanana kadar gerçek tanıma oranı bilinmiyor. **24 Ekim eklemesi:** Beklenen davranış önce elle yazıldı (S40–S45 desteklenen, U31–U32 reddedilen); altı desteklenen sorgu önceki gramerde reddediliyordu (ölçüm 39/45'e düşüyordu: koşul çözümleme %86,7). Gramer genişletildi: "saat/gün içinde" ve "içindeki" zaman ekleri, "adayı", "getir" ve "bana". "en parlak 5 olay" (ilk olmadan sayı) belirsiz olduğu için reddedilmeye devam ediyor. **25 Ekim eklemesi:** Beklenen davranış önce elle yazıldı (S46–S52 desteklenen, U33 reddedilen); altı desteklenen sorgu önceki gramerde reddediliyordu (ölçüm 46/52: %88,5). Gramer genişletildi: virgül ayırıcı ("son 24 saat, olaylar" önceden boş belirteçli "Desteklenmeyen ifade: ." hatası veriyordu), "olayı", Türkçe yazım "asteroit/asteroitler/asteroitleri" ve "saatlik/günlük" sıfat ekleri. "ve" virgülle de reddedilmeye devam ediyor. **26 Ekim eklemesi:** Beklenen davranış önce elle yazıldı (S53–S58 desteklenen, U34–U35 reddedilen); altı desteklenen sorgu önceki gramerde reddediliyordu (ölçüm 52/58: %89,7). Gramer genişletildi: "tane", "adet", "tüm", "bütün" dolgu sözcükleri (tek başına sorgu sayılmaz) ve "içerisinde/içerisindeki" zaman ekleri; sayı sınırları değişmedi ("ilk 0 tane olay" reddedilir). Önceki 37/37 ve 28/28 sayıları da yanlıştı: ölçüm çıktısı 39 desteklenen ve 32 reddedilen gösteriyordu. **27 Ekim eklemesi:** Beklenen davranış önce elle yazıldı (S59–S64 desteklenen, U36–U38 reddedilen); altı desteklenen sorgu önceki gramerde reddediliyordu (ölçüm 58/64: %90,6). Gramer genişletildi: "hafta" birimi (1 hafta = 168 saat; "haftadaki/haftalık"), tamlayan eki ("son 3 günün olayları") ve "adaylarını/olaylarını" belirtme biçimleri. Eski U10 ("son 1 hafta olaylar" reddi) bilinçli bir gramer kararıyla değişti: hafta artık desteklenir, aynı vaka "yıl" ile reddedilmeye devam eder; ay ve yıl desteklenmez. **28 Ekim eklemesi:** Beklenen davranış önce elle yazıldı (S65–S70 desteklenen, U39–U41 reddedilen); altı desteklenen sorgu önceki gramerde reddediliyordu (ölçüm 64/70: %91,4). Gramer genişletildi: "son/ilk" sonrasında bir–on yazıyla sayılar ("son üç gün", "ilk beş aday") ve "filtre" sözcüğü ("r filtresindeki"). Eski U21 ("son on gün olaylar" reddi) bilinçli bir gramer kararıyla "son yirmi gün olaylar" ile değişti: yalnız bir–on desteklenir; "bir buçuk saat" gibi kesirli süreler ve sıfır reddedilir.
**29 Ekim eklemesi:** Beklenen davranış önce elle yazıldı (S71–S76 desteklenen, U42–U43 reddedilen); altı desteklenen sorgu önceki gramerde reddediliyordu (ölçüm 70/76: %92,1). Gramer genişletildi: yalın tamlama biçimleri "g bandı olayları", "r filtresi adayları", "i bandı için ..." ve belirtme hali "son 24 saati göster", "son 2 günü listele". Tek harf bant ("g için olaylar") ve tekrarlanan bant ("g bandı r bandı") reddedilmeye devam ediyor. Önceki tablodaki n=64/n=40 sayıları eskimişti; ölçüm çıktısıyla (76 desteklenen, 45 desteklenmeyen) düzeltildi.
**30 Ekim eklemesi:** Beklenen davranış önce elle yazıldı (S77–S82 desteklenen, U44–U45 reddedilen); altı desteklenen sorgu önceki gramerde reddediliyordu (ölçüm 76/82: %92,7). Gramer genişletildi: anlamı değiştirmeyen "gözlenen/gelen" sıfat-fiilleri, "listesi" ve tamlayan ekli "olayların/adayların/adaylarının". Olumsuzlama ("gözlenmeyen") ve sayım sorusu ("kaç olay var") reddedilmeye devam ediyor. **31 Ekim eklemesi:** Beklenen davranış önce elle yazıldı (S83–S88 desteklenen, U46–U47 reddedilen); altı desteklenen sorgu önceki gramerde reddediliyordu (ölçüm 82/88: %93,2). Gramer genişletildi: anlamı değiştirmeyen "için" dolgu sözcüğü ("son 24 saat için g bandındaki olaylar"); tek başına "için" veya bilinmeyen sözcükle birlikte kullanımı ("son 24 saat için kaç olay") reddedilir. Elle yazılan ilk S85 beklentisi bant belirtmediği için yanlıştı (parlaklık sıralaması bant ister); beklenti düzeltildi. Önceki "127 sorgu" ifadesi de yanlıştı (gerçek: 129).

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
