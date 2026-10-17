# Kaynaklar ve doğrulama kaydı

Kontrol tarihi: 17 Ekim 2026. Bu liste ilk kaynak incelemesidir, kapsamlı sistematik literatür taraması değildir.

| Kaynak | Desteklediği nokta | Durum |
|---|---|---|
| [Duev ve ark. 2019](https://arxiv.org/abs/1907.11259) | Braai Real/Bogus sınıflandırması | Başlık ve yazarlar doğrulandı |
| [Makalenin yayımlanmış hali](https://doi.org/10.1093/mnras/stz2357) | Üç kanallı 63×63 giriş, kanal bazlı normalizasyon | Yöntem bölümü incelendi |
| [Braai kaynak deposu](https://github.com/dmitryduev/braai) | Açık kod ve eğitim not defteri | Depo erişilebilir; veri indirme henüz doğrulanmadı |
| [Braai eğitim not defteri](https://github.com/dmitryduev/braai/blob/master/nb/braai_train.ipynb) | 11.5 bin etiketli halka açık uyarı ve veri indirme adresleri | Ham not defteri okundu; indirme adresleri bulundu, dosyalar henüz indirilmedi |
| [IRSA ZTF](https://irsa.ipac.caltech.edu/Missions/ztf.html) | Görüntü, katalog, ışık eğrisi ve API erişim yolları | Resmi hizmet sayfası incelendi |
| [ZTF makine öğrenimi](https://www.ztf.caltech.edu/ztf-ml.html) | Real/Bogus ile fiziksel sınıflandırmanın ayrı görevler olması | Resmi proje sayfası |
| [TensorFlow Conv2D](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Conv2D) | CNN katmanı uygulama başvurusu | Resmi API dokümanı |
| [Streamlit dağılım grafiği](https://docs.streamlit.io/develop/api-reference/charts/st.scatter_chart) | RA/Dec arayüz grafiği | Resmi API dokümanı |

Yerel ana belge: kullanıcı tarafından sağlanan `2209_A_arastirma_onerisi_formu_09102025_(1)_(1).pdf`. Tüm sayfaların metni okundu; yöntem, arayüz ve takvim sayfaları görsel olarak incelendi. Belgedeki şablon yönergeleri kullanıcıdan gelen ek talimat olarak değerlendirilmedi.

## Bulunan somut veri adayı

[Not defterinin ham içeriği](https://raw.githubusercontent.com/dmitryduev/braai/master/nb/braai_train.ipynb), 11.5 bin etiketli uyarı için şu dosyaları kullanıyor:

- [Aday meta verisi ve etiketler (CSV)](https://storage.googleapis.com/ztf-braai/braai.candidates.programid1.csv)
- [Normalize görüntü üçlüleri (NPY)](https://storage.googleapis.com/ztf-braai/braai.triplets.norm.programid1.npy)

Not defterindeki 2022 tarihli indirme kaydı yaklaşık 16.6 MB CSV ve 1.10 GB NPY gösteriyor. Bunlar güncel indirme doğrulaması değildir. Boyut, önerideki yaklaşık 1.2 GB ifadesine yakın; aynı veri olduğu henüz kesin değil. Kaynak GCS üzerindeki braai koleksiyonudur, IRSA indirme bağlantısı değildir. Not defteri etiketleri 0=bogus ve 1=real olarak açıklıyor. `candid` ve `label` alanları gösteriliyor; güvenilir nesne kimliği alanı ayrıca incelenmeli.

Açık sorular: Bu dosyaların güncel erişimi; etiket oluşturma sürecinin ayrıntısı; veri lisansı; tür/meta veri eşlemesi; diğer bibliyografik girdilerin doğruluğu; güncel resmi teslim tarihi. Hiçbir örnek görsel veya önerideki confusion matrix bu projenin elde edilmiş sonucu olarak kullanılmadı.
