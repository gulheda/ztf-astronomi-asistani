# SNAD nominal/artefakt verisinin değerlendirilmesi

**Sonraki doğrulama tamamlandı:** İki arşiv indirildi, boyut/MD5 eşleşti ve SHA256 kaydedildi. 4508 FITS dosyası sayıldı; 24 kesit ve başlığı incelendi. [Gerçek veri denetimi raporu](experiments/snad-data-2026-10-17/README.md). Aşağıdaki ilk değerlendirme, indirme öncesi araştırmanın tarihsel kaydıdır.

Doğrulama: **17 Ekim 2026, yaklaşık 13:14–13:15 Europe/Istanbul**. Zenodo kayıt API'si GET ile, arşiv erişimi yalnız HTTP HEAD ile kontrol edildi. Bu değerlendirme sırasında arşivler indirilmedi, FITS içerikleri incelenmedi ve model eğitilmedi.

## Kaynak ve erişim

- Makale: Sreejith ve arkadaşları, *Dataset of artefacts for machine learning applications in astronomy*, [arXiv:2504.08053v1](https://arxiv.org/html/2504.08053v1), 10 Nisan 2025.
- Veri: [Zenodo 15076426](https://zenodo.org/records/15076426), DOI [10.5281/zenodo.15076426](https://doi.org/10.5281/zenodo.15076426), yayın tarihi 24 Mart 2025.
- [Kayıt API'sinde](https://zenodo.org/api/records/15076426) `access_right=open` ve veri lisansı `cc-by-4.0` doğrulandı. Kaynak ve lisans atfı korunmalı; makale ile veri DOI'si deney kaydına eklenmeli.

| Dosya | Boyut (bayt) | Zenodo MD5 | HEAD sonucu |
|---|---:|---|---|
| Artefacts.zip | 33.051.444 | `66c2e35ad0a3284842b5374211043098` | HTTP 200 |
| Nominals.zip | 32.707.445 | `d4b993aa502d844d64f9734141b801ca` | HTTP 200 |

Toplam sıkıştırılmış boyut **65.758.889 bayt**. HTTP `Content-Length` değerleri kayıt metadatasıyla eşleşti. HEAD kontrolü tam indirme veya içerik bütünlüğü doğrulaması değildir; MD5 değerleri henüz yerel dosyalarla karşılaştırılmadı.

Doğrudan indirme adresleri:

- [Artefacts.zip](https://zenodo.org/api/records/15076426/files/Artefacts.zip/content)
- [Nominals.zip](https://zenodo.org/api/records/15076426/files/Nominals.zip/content)

## Etiketlerin bilimsel anlamı

Veri kaydı 1127 artefakt ve 1127 nominal nesne için 28×28 ve 63×63 FITS kesitleri bildiriyor. Etiketler merkez nesnenin fotometrisini etkileyen kusurları anlatır; hedefin önünden geçen gerçek asteroid de artefakt sayılabilir. Bu nedenle nominal/artefakt hedefi, geçici uyarıların gerçek/sahte ayrımıyla eşdeğer değildir. [Makale, §3–5](https://arxiv.org/html/2504.08053v1)

Yayımlanan veri sözleşmesi science/reference/difference üçlüsü sağlamıyor. Mevcut `(63,63,3)` CNN girdisine doğrudan uyum iddia edilemez. Bir görüntüyü üç kanala kopyalamak eksik gözlemleri sağlamaz. FITS HDU sayısı, boyutları ve piksel özellikleri indirme sonrası doğrulanmalı.

## Seçim yanlılığı ve genellenebilirlik

Örneklem DR3'ün 2018 gözlemlerinden, zr bandında en az 100 gözlem ve `catflags=0` koşuluyla seçilen 26 alana dayanıyor. Artefaktlar PineForest ile aktif seçilip dört uzman tarafından incelenmiş. Nominaller aynı alanlardan rastgele seçilmiş ve görüntü/ışık eğrisi incelemesiyle doğrulanmış artefaktsız örnekler. Yazarlar aktif seçimin yanlılık oluşturabileceğini açıkça belirtiyor. [Makale, §2, §4, §6.1](https://arxiv.org/html/2504.08053v1)

Proje açısından çıkarım: Dengeli ve temiz nominal örneklemdeki başarı, canlı uyarı akışının sınıf oranlarını veya zor vakalarını temsil etmez. Bu veriyle elde edilen skor “ZTF canlı Real/Bogus başarısı” olarak sunulmamalı.

## Önerilen ayrı pilot

Bu bölüm uygulama önerisidir; tamamlanmış çalışma değildir.

1. Deneyi `snad_nominal_artifact` adıyla ayır. İlk hedef `0=artifact`, `1=nominal` olsun; mevcut üç kanallı Braai deneyinin veri sözleşmesini değiştirme.
2. İndirme sonrası boyut ve MD5 kontrolü yap; ham dosyalar için SHA256 hesapla. Kaynak URL, DOI, lisans, indirme zamanı ve dönüşüm sürümünü sakla. Ham arşivleri Git deposuna ekleme.
3. FITS başlıklarını ve görüntüleri incele: OID, koordinat, alan, bant, gözlem zamanı, etiket, NaN/Inf ve boş kanal durumlarını raporla. Nominal başlıkların artefakt başlıklarıyla aynı alanları içerdiğini varsayma. Metadata eksikse uydurma.
4. Tek görüntü düzlemi doğrulanırsa `(63,63,1)` için ayrı okuyucu ve küçük CNN kullan. Aynı bölmelerde çoğunluk sınıfı ve basit görüntü özellikleri baseline'larını karşılaştır. Ön işleme yalnız eğitim verisiyle belirlenen kurallara dayanmalı; fiziksel piksel anlamı korunmalı.
5. Nesne bazlı ayır: aynı OID'nin tüm görüntüleri ve 28×28/63×63 sürümleri tek bölümde kalsın. Yakın koordinatlar ve tekrar görüntüler üzerinden alanlar arası aynı fiziksel nesne olasılığını da kontrol et; OID'nin tek başına evrensel fiziksel nesne kimliği olduğunu varsayma.
6. Alan bazlı dış test oluştur: seçilen test alanlarının tamamını eğitim ve doğrulamadan çıkar. Bölmeleri ve seçim kuralını sonuçlara bakmadan sabitle; her bölümde sınıf ve artefakt alt türü dağılımını raporla. Alanlar arası ortak nesne varsa bölümler arasında bırakma.
7. Accuracy yanında balanced accuracy, nominal recall, precision, F1, ROC-AUC, average precision ve confusion matrix raporla. Nesne bazlı güven aralıkları ve artefakt türüne göre hata incelemesi ekle. Alan dışı test ile rastgele nesne bölmesini ayrı sonuçlar olarak sun.

Üç kanallı uyarı Real/Bogus hedefi için uygun kaynak arayışı paralel sürmeli. Bu pilot, gerçek ZTF görüntüleri üzerinde veri işleme ve model değerlendirme altyapısını sınar; özgün hedefin tamamlandığı anlamına gelmez.
