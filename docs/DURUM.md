# Başlangıç teslimi - 17 Ekim 2026

## Güncel ilerleme: gerçek çıkarım ve incelemeler

Üç paralel inceleme güvenlik, doğruluk ve testleri ele aldı. Zaman hassasiyeti, parser koşul tanıma ve byte kimlik sorunları düzeltildi. Bağımsız insan etiketi beyanı eğitim kabulüne eklendi.

Yayımlanmış braai modeliyle iki gerçek ZTF uyarısı işlendi; gerçek kayıtlar SQLite'a yazılıp Türkçe sorgu yerelde de doğrulandı. [Deney raporu ve kalıcı çıktılar](experiments/braai-2026-10-17/README.md). Kendi CNN eğitimimiz ve bağımsız bilimsel doğrulama henüz yapılmadı.

Son CI: genel ortamda 35 test geçti, 3 FITS testi ayrı ortamda çalıştırıldı; çıkarım ortamındaki 5 kaynak/FITS testi başarılı. Uygulama ve çıkarım bağımlılık taramaları bilinen açık bulmadı. Önceki setuptools bulgusu yükseltmeyle giderildi. Haftalık Dependabot takibi yapılandırıldı.

Eski GCS eğitim dosyaları bugün HTTP404. [Kaynak araştırması](ARASTIRMA_NOTLARI_2026-10-17.md) ve [SNAD alternatif veri değerlendirmesi](SNAD_VERI_DEGERLENDIRMESI.md) eklendi. Sonraki iş: bilimsel hedefe uygun bağımsız etiketli eğitim kaynağını kesinleştirmek; SNAD pilotu seçilirse ayrı nominal/artefakt deneyi olarak yürütmek.

Aşağıdaki bölümler ilk teslimin tarihsel kaydıdır; güncel durum yukarıdadır.

## GitHub üzerinden çalışma

Public repo: https://github.com/gulheda/ztf-astronomi-asistani

İlk üç commit: prototip, araştırma dokümantasyonu ve GitHub test/iş takip düzeni. Sonraki adımlar [#1 veri kaynağı](https://github.com/gulheda/ztf-astronomi-asistani/issues/1), [#2 veri hazırlığı](https://github.com/gulheda/ztf-astronomi-asistani/issues/2), [#3 CNN](https://github.com/gulheda/ztf-astronomi-asistani/issues/3), [#4 entegrasyon](https://github.com/gulheda/ztf-astronomi-asistani/issues/4), [#5 kullanıcı değerlendirmesi](https://github.com/gulheda/ztf-astronomi-asistani/issues/5) olarak açıldı.

[İlk GitHub Actions çalışması](https://github.com/gulheda/ztf-astronomi-asistani/actions/runs/39023720562) başarılı: Python 3.11 ortamında 10 test geçti (8 çekirdek + 2 Streamlit çalışma testi), sözdizimi kontrolü ve terminal demosu tamamlandı. Streamlit testleri sonuç tablosunun oluşmasını ve desteklenmeyen sorgunun hata vermesini doğrular; görsel tarayıcı incelemesi değildir.

## Tamamlandı

- Proje önerisinin 10 sayfasının metni incelendi; yöntem, mock-up ve takvim sayfaları görsel olarak kontrol edildi.
- Türkçe sorgu, SQLite şeması, sentetik demo ve bağımlılıksız CLI oluşturuldu.
- 8 otomatik test başarılı: Türkçe/zaman, bant/parlaklık, bilinmeyen koşul ve SQL benzeri girdi, demo ayrımı, eşik/tür, gelecek zaman, geçersiz kayıt, nesne bazlı bölme.
- CLI demo komutu çalıştırıldı ve sentetik kayıtlarla doğru sıralı çıktı alındı.
- Python dosyalarının sözdizimi derlemesi başarılı. Eğitim CLI yardım komutu çalışıyor.
- Araştırma planı, veri sözleşmesi, deney planı ve kaynak kaydı oluşturuldu.
- Braai not defterinde gerçek veri dosyaları için aday indirme bağlantıları bulundu.

## Hazır kod, henüz çalışma doğrulaması yok

- Streamlit arayüzü: yerel paket indirmesi tamamlanamadı. Daha sonra GitHub Actions ortamında çalışma testleri başarıyla yapıldı; yerel kurulum ve tarayıcıda görsel inceleme bekliyor.
- TensorFlow eğitimi: kod yazıldı, sözdizimi kontrol edildi; TensorFlow kurulmadı ve model eğitilmedi.
- NumPy görüntü doğrulama/normalizasyon: kod mevcut; gerçek veya sentetik görüntü dizisi üzerinde henüz çalıştırılmadı. Nesne bazlı bölme fonksiyonu bağımsız test edildi.

## Sıradaki somut iş

CSV ve NPY veri kaynaklarının erişimini kontrol etmek; lisansı ve etiket üretimini incelemek; küçük bir alt kümeyle görüntü/meta veri eşleşmesini doğrulamak. Ardından NPZ dönüştürücüsü ve ilk CNN deneyi. Güncel teslim tarihi kullanıcıdan henüz alınmadı.
