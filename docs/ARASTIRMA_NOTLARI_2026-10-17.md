# Kaynak araştırması ve ilk gerçek çıkarım deneyi

## Veri erişimi

17 Ekim 2026'da eski braai eğitim not defterindeki CSV ve NPY GCS bağlantıları canlı HEAD isteğinde HTTP 404 döndü. Not defterindeki 2022 indirme çıktısı güncel erişim kanıtı değildir. Bu kaynakla model eğitilmedi. [Kaynak not defteri](https://github.com/dmitryduev/braai/blob/master/nb/braai_train.ipynb)

## Gerçek model çıkarımı

Braai deposunun `9fb2259542ec4b0a7dfa485012a23dc15a3f4ce8` commit'inde iki gerçek ZTF uyarısı ve `braai_d6_m9.weights.h5` bulunuyor. Üç dosya indirildi; boyutları ve SHA256 değerleri `astro_assistant/braai.py` içinde sabitlendi. Ham dosyalar ve ağırlıklar Git deposuna eklenmiyor.

`d6_m9` için science/reference/difference sırası, her kanala global L2 normu, NaN→0 ve sağ/alta 1e-9 padding uygulanıyor. Eski `d6_m7` satır bazlı normu bu ağırlıklarla kullanılmıyor. Mimari açıkça kurularak yalnız ağırlıklar yükleniyor. MIT lisansı `THIRD_PARTY_NOTICES.md` içinde korunuyor. [Kaynak kod](https://github.com/dmitryduev/braai), [çıkarım not defteri](https://github.com/dmitryduev/braai/blob/master/nb/braai_run.ipynb)

Bu örnekler için bağımsız gerçek etiketler mevcut kabul edilmiyor. Uyarıdaki `rb` önceki model skorudur. Deney, görüntü/model/veritabanı/sorgu zincirini kontrol eder; %85 doğruluk hedefini ölçmez. Sonuç bizim eğittiğimiz model olarak sunulamaz. Yöntem kaynağı: [Duev ve ark. 2019](https://doi.org/10.1093/mnras/stz2357).

Çalıştırma (Python 3.11):

```bash
python -m pip install -r requirements-inference.txt
python -m astro_assistant.braai --output output/real-inference
```

Çıktı klasörü yeni olmalı. Dosyalar: `inference.json`, `alerts.sqlite`, `real_alert_triplets.png`. GitHub Actions paket sürümlerini de kaydeder. İlk başarılı çalışma sonrası kalıcı deney raporu eklenecek.

## Alternatif eğitim kaynağı

[SNAD değerlendirme notu](SNAD_VERI_DEGERLENDIRMESI.md) açık lisanslı 2025 veri kaynağını ele alıyor. Tek görüntüde nominal/artefakt pilotu için adaydır; üç kanallı uyarı modeliyle aynı deney sayılmamalı.

## Araştırma odağı

[Fink portalı](https://doc.ztf.fink-broker.org/services/search/getting_started/) astronomik sorgulama/görselleştirme sağlıyor. Astro-COLIBRI geliştiricileri [2024'te GPT entegrasyonu duyurmuş](https://forum.astro-colibri.science/t/new-astro-colibri-release-v2-9-1/76). “Astronomide ilk doğal dil arayüzü” iddiası kullanılmamalı.

Projenin araştırma odağı olarak sınırlı Türkçe sorgu, öğrencilerin görev başarısı/süresi ve kaynak/model izlenebilirliğini öneriyoruz. Bu bir konumlandırma önerisidir; kapsamlı sistematik literatür taramasının tamamlandığı anlamına gelmez.

## İnceleme düzeltmeleri

- Zamanın saniyeye kesilmesi, pencerenin hemen dışındaki kayıtları içeri alıyordu. Mikrosaniye biçimi ve eski kayıt geçişi eklendi.
- Byte kimlikler boş değer kontrolünü ve JSON deney kaydını bozabiliyordu. NPZ sözleşmesi yalnız Unicode kabul ediyor.
- Tek başına zaman/sıralama/limit filtreleri reddediliyor, yalnız nezaket sözcüğü kabul ediliyordu. Koşul tanıma düzeltildi.
- Eğitim, modelden bağımsız insan etiketi beyanını gerektiriyor. Bu kontrol gerçek etiket denetiminin yerine geçmez.

Mevcut SQL parametreleri, pickle kapalı NPZ okuma, demo ayrımı ve CI yetkileri incelendi. Kritik açık doğrulanmadı. Yeni indirme kodunda sabit URL, dosya boyutu, SHA256 ve FITS açılım boyutu kontrolleri var.
