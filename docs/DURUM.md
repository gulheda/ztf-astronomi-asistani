# Başlangıç teslimi - 17 Ekim 2026

## Tamamlandı

- Proje önerisinin 10 sayfasının metni incelendi; yöntem, mock-up ve takvim sayfaları görsel olarak kontrol edildi.
- Türkçe sorgu, SQLite şeması, sentetik demo ve bağımlılıksız CLI oluşturuldu.
- 8 otomatik test başarılı: Türkçe/zaman, bant/parlaklık, bilinmeyen koşul ve SQL benzeri girdi, demo ayrımı, eşik/tür, gelecek zaman, geçersiz kayıt, nesne bazlı bölme.
- CLI demo komutu çalıştırıldı ve sentetik kayıtlarla doğru sıralı çıktı alındı.
- Python dosyalarının sözdizimi derlemesi başarılı. Eğitim CLI yardım komutu çalışıyor.
- Araştırma planı, veri sözleşmesi, deney planı ve kaynak kaydı oluşturuldu.
- Braai not defterinde gerçek veri dosyaları için aday indirme bağlantıları bulundu.

## Hazır kod, henüz çalışma doğrulaması yok

- Streamlit arayüzü: kod yazıldı; paket indirmesi ilk kısıtlı ağ denemesinde başarısız oldu. İzinli iki denemede indirme ilerlemediği için süreç tarafımızdan durduruldu. Arayüz çalıştırılmadı veya görsel olarak doğrulanmadı.
- TensorFlow eğitimi: kod yazıldı, sözdizimi kontrol edildi; TensorFlow kurulmadı ve model eğitilmedi.
- NumPy görüntü doğrulama/normalizasyon: kod mevcut; gerçek veya sentetik görüntü dizisi üzerinde henüz çalıştırılmadı. Nesne bazlı bölme fonksiyonu bağımsız test edildi.

## Sıradaki somut iş

CSV ve NPY veri kaynaklarının erişimini kontrol etmek; lisansı ve etiket üretimini incelemek; küçük bir alt kümeyle görüntü/meta veri eşleşmesini doğrulamak. Ardından NPZ dönüştürücüsü ve ilk CNN deneyi. Güncel teslim tarihi kullanıcıdan henüz alınmadı.
