# Türkçe sorgu değerlendirmesi ve kullanıcı çalışması taslağı

22 Ekim 2026 (ilk ölçüm 21 Ekim). [DENEY_PLANI.md](DENEY_PLANI.md) içindeki sorgu değerlendirmesinin ilk ölçümü ve kullanıcı pilotunun görev taslağı.

## Ölçüm

Küme: [tests/query_eval_set.json](../tests/query_eval_set.json), 65 sorgu (37 desteklenen, 2 bant belirtilmeden parlaklık sıralaması, 26 desteklenmeyen). Beklenen koşullar gramerden elle yazıldı. Beklenen sonuç kimlikleri, `parse_query` ve SQL kullanılmadan ayrı bir Python süzgeciyle hesaplandı. Çalıştırma: `python -m tests.query_eval`. Veri sentetik demo kayıtlarıdır; bu bir model veya bilimsel doğruluk ölçümü değildir.

| Ölçüt | Sonuç |
|---|---:|
| Koşul çözümleme (desteklenen, n=37) | 37/37 |
| Sonuç kümesi tam eşleşmesi (desteklenen, n=37) | 37/37 |
| Desteklenmeyen sorgunun açıkça reddi (n=28) | 28/28 |
| Boş sonuçlu doğru sorgu | 4 |
| Yerel p50 / p95 (ayrıştırma + SQLite) | ≈0,05 ms / ≈0,14 ms |

Plan hedefleri (≥%90 tam eşleşme, sessiz filtre kaybı yok) bu kümede karşılandı. Bunlar proje kararıdır, bilimsel eşik değildir.

**Düzeltilen açıklar:** İlk ölçümde tek hata S21 idi: "adaylar" çoğulu tanınmıyordu. 22 Ekim'de beklenen davranış önce elle yazıldı (S31–S37, U25–U26 eklendi), ardından gramer genişletildi: "adaylar", "süpernovaları" ve "asteroidleri" biçimleri tanınıyor. S21 ve eklenen S31, S33, S35, S36 önceki gramerde reddediliyordu. Önceki oran (29/30) bu düzeltmeden önceki ölçümdür; yeni 37/37 daha geniş ve bu açıklara bakılarak genişletilmiş bir kümedir, bu yüzden daha da iyimsel okunmalıdır. Küme yazarı sorguları grameri bilerek yazdığından oran iyimserdir: kullanıcıların kendi cümleleri pilotta toplanana kadar gerçek tanıma oranı bilinmiyor. Desteklenmeyen sorgu örnekleri (hafta/ay, mutlak tarih, koordinat, olumsuzlama, "ve") bilinçli olarak reddediliyor.

## Kullanıcı pilotu için görev taslağı

Henüz çalıştırılmadı. Veri kaynağı (issue #1) kesinleşmeden son görevler yazılamaz; aşağıdakiler kalıp görevlerdir. Her görev iki eşdeğer sürümde hazırlanır (A: geleneksel filtreli tablo, B: Türkçe asistan), sıra yarı yarıya dönüşümlü.

| Kod | Görev kalıbı | Beklenen davranış |
|---|---|---|
| G1 | Belirli zaman aralığındaki adayları bul | Süre penceresi doğru, sayı eşleşir |
| G2 | Bir bantta en parlak üç uyarıyı belirle | Bant belirtilmeden sıralama yapılamadığını fark etmek |
| G3 | Kaynağı belirtilmiş bir türdeki adayları listele | Tür etiketinin kaynağı okunur |
| G4 | Boş sonuç veren bir sorguyu yorumla | "Hata" ile "kayıt yok" ayırt edilir |
| G5 | Desteklenmeyen bir isteği (ör. "son 1 hafta") yerine getir | Hata iletisinden yeniden ifade eder |

Kayıt alanları: anonim katılımcı kodu, koşul, görev kodu, doğru tamamlama (0/1), süre (sn), kullanıcı işlemi sayısı, hata sayısı, kısa geri bildirim. Ayrı not edilecekler: işlem sayısının neyi kapsadığı pilot öncesi yazılı tanımlanmalı; pilot (3 kişi) sonuçları nihai örneklemle karıştırılmaz; kurumun gerekli gördüğü etik/katılım süreci danışmanla netleştirilmeli.
