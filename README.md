# Yapay Zekâ Destekli Astronomi Asistanı

[![Tests](https://github.com/gulheda/ztf-astronomi-asistani/actions/workflows/tests.yml/badge.svg)](https://github.com/gulheda/ztf-astronomi-asistani/actions/workflows/tests.yml)

[Görevler](https://github.com/gulheda/ztf-astronomi-asistani/issues) · [Geliştirme akışı](CONTRIBUTING.md) · [Proje planı](docs/PROJE_PLANI.md)

ZTF görüntülerinde Real/Bogus sınıflandırması ile Türkçe sorgulamayı birleştiren 2209-A araştırmasının başlangıç deposu.

**Durum (17 Ekim 2026):** Türkçe sorgu + SQLite + demo arayüzü oluşturuldu. Gerçek ZTF verisi indirilmedi, CNN eğitilmedi, bilimsel başarı ölçülmedi. Demo kayıtları ve skorları tamamen sentetiktir.

## Hemen çalıştır

Proje klasöründe ek paket gerektirmeyen terminal demosu:

```bash
python3 -m astro_assistant --demo
python3 -m astro_assistant --demo "Son 3 gündeki süpernovalar"
python3 -m unittest discover -s tests -v
```

Streamlit arayüzü:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Tarayıcı adresi: http://localhost:8501. Yerel demo internetten veri çekmez; API anahtarı gerekmez.
Mevcut `.venv` varsa yeniden oluşturmanız gerekmez. Grafik arayüzü demo modundadır.
Yerel paket indirmesi tamamlanamadı. GitHub Actions üzerinde Python 3.11 ile 8 çekirdek ve 2 Streamlit çalışma testi başarıyla tamamlandı; tarayıcıda görsel inceleme henüz yapılmadı. Ayrıntılı doğrulama durumu `docs/DURUM.md` içindedir.

## Desteklenen sorgular

- `Son 24 saatteki olaylar`
- `Son 3 gündeki süpernovalar`
- `Son 48 saatteki asteroidler`
- `Son 7 gündeki g bandında en parlak ilk 10 olay`
- `En yeni ilk 5 olay`

Varsayılan: son 24 saat, en yeni 20 uyarı, skor ≥ 0.5. Zamanlar UTC'dir. “En parlak” için aynı fotometrik bant gerekir; küçük magnitüd daha parlaktır. Arayüzde referans zamanı açıkça gösterilir. Serbest sohbet, koordinat bölgesi, olumsuzlama, mutlak tarih ve sayısal parlaklık koşulları henüz desteklenmez; bilinmeyen ifadeler hata verir.

## Dosyalar

| Dosya | İşlev |
|---|---|
| `app.py` | Demo sorgu arayüzü, tablo, RA/Dec dağılımı, CSV indirme |
| `astro_assistant/core.py` | Türkçe çözümleme, doğrulama, parametreli SQL, demo üretimi |
| `astro_assistant/dataset.py` | NPZ kontrolü, normalizasyon, nesne bazlı bölme |
| `astro_assistant/train.py` | Gerçek veri bekleyen TensorFlow eğitim iskeleti |
| `tests/` | Sorgu, veri bütünlüğü ve sızıntı önleme testleri |
| `docs/PROJE_PLANI.md` | İş paketleri, kabul ölçütleri, öncelikler |
| `docs/VERI_VE_YONTEM.md` | Veri sözleşmesi ve bilimsel kararlar |
| `docs/DENEY_PLANI.md` | Model ve kullanıcı değerlendirmesi |
| `docs/KAYNAKLAR.md` | Doğrulanan kaynaklar ve açık sorular |

## Gerçek veriye geçiş

Önce `docs/VERI_VE_YONTEM.md` içindeki kaynak ve etiket kontrolünü tamamlayın. Eğitim için Colab üzerinde Python 3.11/3.12 ortamı hedeflenmiştir; bu bilgisayardaki Python 3.9 ortamında TensorFlow kurulumu doğrulanmadı.

```bash
python -m pip install -r requirements-ml.txt
python -m astro_assistant.train data/processed/ztf.npz --provenance data/processed/provenance.json --output models/run-001
```

Bu komut şu an veri dosyası olmadığı için çalıştırılamaz. `models/run-001` yeni bir klasör olmalıdır. Model eşik değeri başlangıç deneyi için 0.5'tir; yüzde 85 doğruluk bir hedef olup elde edilmiş sonuç değildir.

Gerçek skorların veritabanına alınması için `insert_alerts` fonksiyonu hazırdır; kaynak dosyası dönüştürücüsü, model çıkarımı ve canlı akış bağlantısı sonraki aşamadır. Gerçek veritabanı hazır olduğunda `python3 -m astro_assistant --db data/alerts.sqlite "Son 24 saatteki olaylar"` kullanılabilir. Demo kayıtları bu sorgulardan otomatik dışlanır.
