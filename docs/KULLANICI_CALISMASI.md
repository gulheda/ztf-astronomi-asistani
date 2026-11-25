# Kullanıcı çalışması protokolü (taslak)

Hazırlık tarihi 25 Kasım 2026. **Henüz çalıştırılmadı.** Araştırma sorusu ([PROJE_PLANI.md](PROJE_PLANI.md)): sınırlı Türkçe sorgu arayüzü, uzman olmayan öğrencilerin aynı görevleri doğru tamamlama süresini ve teknik işlem sayısını azaltıyor mu? Bu protokol danışman onayından önce taslaktır; katılım ve etik süreç kurumun kurallarına göre netleştirilmelidir.

## Koşullar

Aynı veri, aynı sorgu motoru, iki arayüz. Uygulamada kenar çubuğundaki **Sorgu arayüzü** seçicisiyle değişir:

- **A, Geleneksel filtre:** süre (saat), bant, tür, sıralama ve sonuç sayısı seçicileri, "Filtrele" düğmesi.
- **B, Türkçe sorgu:** metin kutusu ve "Sorgula" düğmesi.

Her katılımcı iki koşulu da kullanır; yarısı AB, yarısı BA sırasıyla (`sira` alanı). Eşdeğer ama farklı görev kümeleri kullanılır, öğrenme etkisi ayrıca raporlanır.

## Görev kalıpları

Son görev metinleri, veri kaynağı kesinleştikten sonra (issue #1) yazılır; aşağıdakiler kalıplardır.

| Kod | Görev kalıbı | Beklenen davranış |
|---|---|---|
| G1 | Belirli zaman aralığındaki adayları bul | Süre penceresi doğru, sayı eşleşir |
| G2 | Bir bantta en parlak üç uyarıyı belirle | Bant belirtilmeden sıralama yapılamadığını fark etmek |
| G3 | Kaynağı belirtilmiş bir türdeki adayları listele | Tür etiketinin kaynağı okunur |
| G4 | Boş sonuç veren bir sorguyu yorumla | "Hata" ile "kayıt yok" ayırt edilir |
| G5 | Desteklenmeyen bir isteği (ör. "son 2 ay") yerine getir | Hata iletisinden yeniden ifade eder |

## Ölçülen alanlar

[kayit_sablonu.csv](kullanici_calismasi/kayit_sablonu.csv) sütunları: `katilimci` (anonim kod, ad/e-posta yok), `sira` (AB/BA), `kosul` (A/B), `gorev`, `dogru` (0/1), `sure_sn`, `islem_sayisi`, `hata_sayisi`, `geri_bildirim`.

**İşlem sayısı tanımı (pilottan önce sabitlenmeli):** her seçici/alan değişikliği 1, her gönder düğmesi tıklaması 1, aynı görev için yeniden yazma ya da yeniden seçme yeniden sayılır. **Dikkat:** bu tanım yapısal olarak B'yi avantajlı gösterir (tek metin kutusu ≈ 2 işlem, filtre ≈ 6-7 işlem). Bu yüzden işlem sayısı tek başına kanıt sayılmaz; süre, doğruluk ve hata sayısıyla birlikte raporlanır.

## Analiz

```bash
python -m astro_assistant.calisma_analizi kayit.csv
```

Betik kayıtları doğrular (hatalı satırı satır numarasıyla bildirir), koşula göre başarı oranı, süre ve işlem medyan/IQR değerlerini, katılımcı-görev eşleştirilmiş A−B farklarını ve katılımcı düzeyinde bootstrap %95 aralığını verir. Başarısız görevler süre analizine dahildir. Test verisi sentetiktir ve elle hesaplanmıştır; gerçek katılımcı verisi değildir.

## Sınırlar

- Önerideki hedef 15–20 lisans öğrencisi; bu örneklemde aralıklar geniş olacaktır, evrensel genelleme yapılmaz.
- 3 kişilik pilot sonuçları nihai örneklemle birleştirilmez; pilot kayıtları ayrı dosyada tutulur.
- Gramer, çalışmadan önce dondurulur; çalışma sırasında değiştirilmez. Katılımcıların yazdığı ifadeler çalışma sonunda tanınma oranı için ayrıca kaydedilir.
- Uygulamanın veri kaynağı (sentetik demo ya da 2 kayıtlı gerçek arşiv) bu çalışma için yetersizdir; gerçek bir gözlem kümesi bağlanmadan görevler anlamlı olmaz.
