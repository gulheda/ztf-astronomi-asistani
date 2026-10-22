# Türkçe sorgu değerlendirmesi ve kullanıcı çalışması taslağı

21 Ekim 2026. [DENEY_PLANI.md](DENEY_PLANI.md) içindeki sorgu değerlendirmesinin ilk ölçümü ve kullanıcı pilotunun görev taslağı.

## Ölçüm

Küme: [tests/query_eval_set.json](../tests/query_eval_set.json), 56 sorgu (30 desteklenen, 2 bant belirtilmeden parlaklık sıralaması, 24 desteklenmeyen). Beklenen koşullar gramerden elle yazıldı. Beklenen sonuç kimlikleri, `parse_query` ve SQL kullanılmadan ayrı bir Python süzgeciyle hesaplandı. Çalıştırma: `python -m tests.query_eval`. Veri sentetik demo kayıtlarıdır; bu bir model veya bilimsel doğruluk ölçümü değildir.

| Ölçüt | Sonuç |
|---|---:|
| Koşul çözümleme (desteklenen, n=30) | 29/30 |
| Sonuç kümesi tam eşleşmesi (desteklenen, n=30) | 29/30 |
| Desteklenmeyen sorgunun açıkça reddi (n=26) | 26/26 |
| Boş sonuçlu doğru sorgu | 4 |
| Yerel p50 / p95 (ayrıştırma + SQLite) | ≈0,03 ms / ≈0,07 ms |

Plan hedefleri (≥%90 tam eşleşme, sessiz filtre kaybı yok) bu kümede karşılandı. Bunlar proje kararıdır, bilimsel eşik değildir.

**Tek hata, S21:** "Son 72 saatteki **adaylar**" reddedildi. Gramer yalnız "aday" ve "adayları" sözcüklerini tanıyor, çoğul "adaylar" tanınmıyor. Beklenen davranış elle yazıldığı için hata olarak bırakıldı; çözümleyici teste uydurulmadı. Küme yazarı sorguları grameri bilerek yazdığından oran iyimserdir: kullanıcıların kendi cümleleri pilotta toplanana kadar gerçek tanıma oranı bilinmiyor. Desteklenmeyen sorgu örnekleri (hafta/ay, mutlak tarih, koordinat, olumsuzlama, "ve") bilinçli olarak reddediliyor.

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
