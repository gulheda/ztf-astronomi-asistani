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

Çıktı klasörü yeni olmalı. Dosyalar: `inference.json`, `alerts.sqlite`, `real_alert_triplets.png`. GitHub Actions paket sürümlerini de kaydeder. [Başarılı çalışma ve kalıcı deney raporu](experiments/braai-2026-10-17/README.md) eklendi.

## Alternatif eğitim kaynağı

[SNAD değerlendirme notu](SNAD_VERI_DEGERLENDIRMESI.md) açık lisanslı 2025 veri kaynağını ele alıyor. Tek görüntüde nominal/artefakt pilotu için adaydır; üç kanallı uyarı modeliyle aynı deney sayılmamalı.

## Üç kanallı etiketli ZTF verisi araması (21 Ekim 2026)

Yalnız yayın metinleri ve GitHub meta verisi okundu; hiçbir veri indirilmedi, içerik ve etiketler doğrulanmadı.

| Aday | Bulunan | Projeye uygunluk |
|---|---|---|
| [RB-C1000](https://github.com/cherry0116/RB-C1000) / [arXiv:2412.02409](https://arxiv.org/abs/2412.02409) | Üç ZTF kümesi (g, r, karışık), her biri 13000 real ve 30000 bogus. Veri Google Drive bağlantısında; depo kodu MIT, veri için ayrı lisans belirtilmemiş, SHA256 yok. | Real etiketi TNS'de bildirilmiş süpernovalardan geliyor, tek tek insan incelemesi anlatılmıyor. Bogus, SExtractor ile rastgele seçilmiş ve "birkaç gerçek tespit içerebilir". Yazarlar kümeleri yalnız yöntem testi için uygun görüyor. `validate_provenance` insan incelemeli, modelden bağımsız etiket istediğinden bu haliyle eğitim kabulünü geçemez. |
| [arXiv:2606.15705](https://arxiv.org/abs/2606.15705) | ZTF için 6640 real ve 6041 bogus, 63×63×3, elle ayıklanmış. | Veri herkese açık yayımlanmamış, "makul istek üzerine". Yazarlara yazılabilir; lisans ve etiket tanımı yazılı alınmalı. |
| Braai (Duev ve ark. 2019) | 30 binden fazla örnek, etiketleme Zwickyverse'te. | Veri bağlantısı bulunamadı; eski GCS adresleri 404. |

Sonuç: Kabul ölçütümüze (kaynaklı, insan incelemeli, modelden bağımsız etiket) uyan, doğrudan indirilebilir üç kanallı küme henüz yok. Öneri sırası: (1) danışmanla, RB-C1000 gibi bir kümenin etiket sınırlamaları açıkça yazılarak ayrı bir deney olarak kullanılıp kullanılmayacağına karar vermek; (2) 2606.15705 yazarlarından veri ve lisans istemek; (3) gerekirse IRSA/ALeRCE damgalarından kendi etiketli alt kümemizi oluşturmak. Hiçbiri Real/Bogus %85 hedefini bağımsız doğrulanmış etiketle ölçmek için yeterli kanıt değildir.

## Araştırma odağı

[Fink portalı](https://doc.ztf.fink-broker.org/services/search/getting_started/) astronomik sorgulama/görselleştirme sağlıyor. Astro-COLIBRI geliştiricileri [2024'te GPT entegrasyonu duyurmuş](https://forum.astro-colibri.science/t/new-astro-colibri-release-v2-9-1/76). “Astronomide ilk doğal dil arayüzü” iddiası kullanılmamalı.

Projenin araştırma odağı olarak sınırlı Türkçe sorgu, öğrencilerin görev başarısı/süresi ve kaynak/model izlenebilirliğini öneriyoruz. Bu bir konumlandırma önerisidir; kapsamlı sistematik literatür taramasının tamamlandığı anlamına gelmez.

## İnceleme düzeltmeleri

- Zamanın saniyeye kesilmesi, pencerenin hemen dışındaki kayıtları içeri alıyordu. Mikrosaniye biçimi ve eski kayıt geçişi eklendi.
- Byte kimlikler boş değer kontrolünü ve JSON deney kaydını bozabiliyordu. NPZ sözleşmesi yalnız Unicode kabul ediyor.
- Tek başına zaman/sıralama/limit filtreleri reddediliyor, yalnız nezaket sözcüğü kabul ediliyordu. Koşul tanıma düzeltildi.
- Eğitim, modelden bağımsız insan etiketi beyanını gerektiriyor. Bu kontrol gerçek etiket denetiminin yerine geçmez.

Mevcut SQL parametreleri, pickle kapalı NPZ okuma, demo ayrımı ve CI yetkileri incelendi. Kritik açık doğrulanmadı. Yeni indirme kodunda sabit URL, dosya boyutu, SHA256 ve FITS açılım boyutu kontrolleri var.
