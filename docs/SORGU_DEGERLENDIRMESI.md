# Türkçe sorgu değerlendirmesi

Güncel ölçüm 27 Kasım 2026. [DENEY_PLANI.md](DENEY_PLANI.md) içindeki sorgu değerlendirmesinin uygulaması. Kullanıcı çalışması için bkz. [KULLANICI_CALISMASI.md](KULLANICI_CALISMASI.md). Günlük değişiklik ayrıntıları: [SORGU_DEGISIKLIK_GUNLUGU.md](SORGU_DEGISIKLIK_GUNLUGU.md).

## Nasıl ölçülür

Küme: [tests/query_eval_set.json](../tests/query_eval_set.json). Beklenen koşullar gramerden elle yazıldı. Beklenen sonuç kimlikleri `parse_query` ve SQL kullanılmadan, ayrı bir Python süzgeciyle hesaplandı. Veri sentetik demo kayıtlarıdır; bu bir model ya da bilimsel doğruluk ölçümü değildir.

```bash
python -m tests.query_eval      # güncel sayıları yazar; bu belgedeki sayıları elle güncellemeyin
```

## Güncel sonuç (27 Kasım 2026)

| Ölçüt | Sonuç |
|---|---:|
| Sorgu sayısı | 245 (150 desteklenen, 95 desteklenmeyen) |
| Koşul çözümleme ve sonuç kümesi tam eşleşmesi (desteklenen) | 150/150 |
| Desteklenmeyen sorgunun açıkça reddi | 95/95 |
| Boş sonuçlu doğru sorgu | 14 |
| Yerel p50 / p95 (ayrıştırma + SQLite) | ≈0,02 ms / ≈0,05 ms |

Plan hedefleri (≥%90 tam eşleşme, sessiz filtre kaybı yok) karşılandı. Bunlar proje kararıdır, bilimsel eşik değildir.

## Bu sayı nasıl okunmalı

- **İyimser bir ölçümdür.** Gramer ve küme aynı yazar tarafından, her yeni sorgu için önce beklenti yazılıp sonra gramer genişletilerek geliştirildi. Sorgular grameri bilerek yazıldı; gerçek kullanıcıların cümleleri toplanana kadar gerçek tanıma oranı bilinmiyor. İlk ölçümde (22 Ekim, 56 sorgu) 29/30 idi; küme her seferinde bulunan açıklara göre büyüdü.
- **Gramerin genişlemesi bir hedef değildir.** Dolgu sözcüğü eklemek sayıyı değiştirmez ama çözümleyiciyi karmaşıklaştırır. Yeni ifade yalnız kullanıcı çalışmasında gerçekten yazıldığı görülürse eklenmeli.
- **Reddetmek tasarım kararıdır.** Olumsuzlama, sayım sorusu, birleşik sorgu ("g ve r"), ay/yıl, mutlak tarih ve koordinat bilinçli olarak desteklenmez; her biri açık bir Türkçe hata iletisiyle reddedilir.

## Desteklenen kapsam (özet)

Zaman penceresi (saat, gün, hafta; bir–on yazıyla sayılar), tek tür (supernova, asteroid), tek bant (g, r, i), "en yeni" ve "en parlak" (bant gerektirir), "ilk N", eklerin ve dolgu sözcüklerinin ("olaylar", "adaylar", "göster", "listele" vb.) anlamı değiştirmeyen biçimleri. Ayrıntı ve sınırlar için [tests/query_eval_set.json](../tests/query_eval_set.json) ve `astro_assistant/core.py`.
