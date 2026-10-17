# Gerçek ZTF arşiv arayüzü

Uygulama varsayılan olarak sentetik demo kayıtlarını gösterir. Kenar çubuğundaki
veri kaynağı seçicisinden **Gerçek ZTF arşivi** seçilerek sabitlenmiş iki gerçek
ZTF alert örneği incelenebilir. Örnekler ve model çıktıları
`docs/experiments/braai-2026-10-17/inference.json` dosyasındadır; dışarıdan canlı
arşive erişim yapılmaz.

Başlangıç eşiği 0.5, referans zamanı 2019-06-13T05:10:55.004145Z ve sorgu
aralığı 365 gündür. Bu nedenle yalnızca `ZTF18acrkaks` listelenir. Eşik 0'a
indirildiğinde ikinci örnek `ZTF19aazgdzh` de görünür. Gerçek kayıtların gözlem
tarihleri 2018-12-16 ve 2019-06-13'tür; bu tarihler güncel gözlemler değildir.

Skorlar, sabitlenmiş `braai_d6_m9` model ağırlıklarından üretilmiştir. Bu iki
örnek bağımsız doğruluk verisi oluşturmaz. Bu iki örnekle yeniden model eğitimi
veya bağımsız doğruluk ölçümü yapılmaz; skorlar kalibre olasılık değildir.
Arayüzde gerçek olay türü etiketi yoktur.
SNAD veri kümesi ve sınıfları bu iki alert arşivinden ayrı tutulur.

Proje kökünde uygulamayı çalıştırın:

```sh
.venv/bin/python -m streamlit run app.py
```
