# Yapay Zekâ Destekli Astronomi Asistanı

[![Tests](https://github.com/gulheda/ztf-astronomi-asistani/actions/workflows/tests.yml/badge.svg)](https://github.com/gulheda/ztf-astronomi-asistani/actions/workflows/tests.yml)

[Görevler](https://github.com/gulheda/ztf-astronomi-asistani/issues) · [Geliştirme akışı](CONTRIBUTING.md) · [Proje planı](docs/PROJE_PLANI.md)

ZTF görüntülerinde Real/Bogus sınıflandırması ile Türkçe sorgulamayı birleştiren 2209-A araştırmasının başlangıç deposu.

**Durum (17 Ekim 2026):** Türkçe sorgu, SQLite ve demo arayüzü hazır. Braai iki gerçek ZTF uyarısında çalıştırıldı. Ayrı SNAD nominal/artefakt pilotunda kendi CNN ve lojistik baseline modellerimiz eğitildi: 337 test görüntüsünde %83,09 ve %89,91 accuracy. Bunlar canlı uyarı Real/Bogus sonuçları değildir. Arayüz demo verisi sentetiktir.

[İlk gerçek pilot eğitim raporu](docs/experiments/snad-pilot-2026-10-17/README.md)

[Gerçek model deneyinin raporu](docs/experiments/braai-2026-10-17/README.md) · [Kaynak araştırması](docs/ARASTIRMA_NOTLARI_2026-10-17.md) · [Alternatif veri incelemesi](docs/SNAD_VERI_DEGERLENDIRMESI.md)

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

Tarayıcı adresi: http://localhost:8501. API anahtarı gerekmez. Kenar çubuğundaki **Veri kaynağı** ile sentetik **Demo** ve kaynaklı **Gerçek ZTF arşivi** arasında geçiş yapabilirsiniz. Gerçek arşivde 2018/2019 tarihli iki yayımlanmış örnek kullanılır; canlı veri çekilmez. [Arşiv modu kullanım notu](docs/GERCEK_ARSIV_ARAYUZU.md).
`.venv` yoksa veya paketler eksikse yukarıdaki iki kurulum komutunu çalıştırın. Önerilen sürüm Python 3.11'dir; 3.9 ile arayüz ve çekirdek testleri çalışır, Astropy/TensorFlow testleri atlanır.

Apple Silicon Mac'te, çıkarım ve eğitim paketleri için: `tensorflow-cpu==2.21.0` macOS arm64 wheel'i yayımlamıyor, yerelde aynı sürümün `tensorflow==2.21.0` paketini kurun (CI dosyalarını değiştirmeyin). `numpy==1.26.4` ile Streamlit birlikte kurulacaksa `pyarrow<21` gerekir; aksi halde yeni pyarrow NumPy 2 ister ve arayüz testleri hata verir. Ayrıntılı durum `docs/DURUM.md` içindedir.

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
| `app.py` | Demo/gerçek arşiv sorgusu, tablo, RA/Dec dağılımı, CSV indirme |
| `astro_assistant/archive.py` | Sabit gerçek arşiv kaynağı, model ve zaman doğrulaması |
| `astro_assistant/core.py` | Türkçe çözümleme, doğrulama, parametreli SQL, demo üretimi |
| `astro_assistant/dataset.py` | NPZ kontrolü, normalizasyon, nesne bazlı bölme |
| `astro_assistant/train.py` | Gerçek veri bekleyen TensorFlow eğitim iskeleti |
| `tests/` | Sorgu, veri bütünlüğü ve sızıntı önleme testleri; 71 sorgulu [değerlendirme seti](docs/SORGU_DEGERLENDIRMESI.md) |
| `docs/PROJE_PLANI.md` | İş paketleri, kabul ölçütleri, öncelikler |
| `docs/VERI_VE_YONTEM.md` | Veri sözleşmesi ve bilimsel kararlar |
| `docs/DENEY_PLANI.md` | Model ve kullanıcı değerlendirmesi |
| `docs/KAYNAKLAR.md` | Doğrulanan kaynaklar ve açık sorular |

## Gerçek veriye geçiş

Yayımlanmış modelle gerçek çıkarımı tekrar etmek için Python 3.11 ortamında:

```bash
python -m pip install -r requirements-inference.txt
python -m astro_assistant.braai --output output/real-inference
python -m astro_assistant --db output/real-inference/alerts.sqlite --at 2019-06-13T05:10:55.004145+00:00 "Son 365 gündeki olaylar"
```

İki örnek bağımsız doğrulama seti değildir; buradan accuracy hesaplanmaz. Çıkarım, sabit GitHub commit'inden SHA256 ile doğrulanan örnek/ağırlık dosyalarını kullanır. Eski GCS eğitim bağlantıları bugün 404 döndüğünden eğitim kaynağı araştırması sürüyor.

Önce `docs/VERI_VE_YONTEM.md` içindeki kaynak ve etiket kontrolünü tamamlayın. Eğitim için Colab üzerinde Python 3.11/3.12 ortamı hedeflenmiştir; bu bilgisayardaki Python 3.9 ortamında TensorFlow kurulumu doğrulanmadı.

```bash
python -m pip install -r requirements-ml.txt
python -m astro_assistant.train data/processed/ztf.npz --provenance data/processed/provenance.json --output models/run-001
```

Bu komut şu an veri dosyası olmadığı için çalıştırılamaz. `models/run-001` yeni bir klasör olmalıdır. Model eşik değeri başlangıç deneyi için 0.5'tir; yüzde 85 doğruluk bir hedef olup elde edilmiş sonuç değildir.

İki gerçek örneğin yayımlanmış model skorları hem terminalden hem arayüzdeki gerçek arşiv modundan sorgulanabilir. Yeni eğitim verisi, daha geniş arşiv içe aktarma ve canlı akış bağlantısı sonraki aşamalardır. Demo kayıtları gerçek arşiv sorgularından dışlanır.
