# SNAD pilotu: sonuçlar görülmeden belirlenen tasarım

Bu deney, tek kanallı nominal/artefakt sınıflandırmasıdır; uyarı akışındaki Real/Bogus başarısının ölçümü değildir. Kaynak: [SNAD/Zenodo 15076426](https://doi.org/10.5281/zenodo.15076426), CC-BY-4.0. [Veri ve seçim yanlılığı incelemesi](SNAD_VERI_DEGERLENDIRMESI.md).

- Yalnız 63×63 FITS dosyaları okunacak. Eksik boyutlar dışlanıp OID, sınıf ve alanla raporlanacak. Sonlu olmayan pikseller, eksik metadata veya çelişen etiketler eğitimden önce durdurulacak.
- Görüntü başına median çıkarılacak, 1.4826×MAD ile ölçeklenecek; sıfır MAD için std kullanılacak. Ardından işareti koruyan asinh sıkıştırması uygulanacak. Küresel veri üzerinde öğrenilen ölçek kullanılmayacak.
- Aynı alan, aynı OID veya 1 yay saniyesi içinde bağlantılı koordinatlar tek grupta tutulacak. Alan bileşenleri sabit seed=42 ile yaklaşık %70/%15/%15 eğitim/doğrulama/teste ayrılacak. Her bölümde iki sınıf bulunmalı; uygun sonuç çıkana kadar seed denenmeyecek.
- Eğitim çoğunluk sınıfı ve standardize 15 görüntü özelliği üzerinden lojistik regresyon baseline'ları kullanılacak. StandardScaler yalnız eğitim verisinde fit edilecek.
- CNN: 8/16/32 filtreli üç Conv2D, iki max pooling, global average pooling, dropout=0.3, 16 birimli dense ve sigmoid. Adam, binary crossentropy, batch=64, en fazla 12 epoch. Yalnız eğitimde yatay/dikey çevirme ve sınıf ağırlığı.
- Model seçimi validation loss; patience=3 ve en iyi ağırlıkların geri alınması. Test eşiği önceden 0.5. Test verisi ayar için kullanılmayacak.
- Accuracy, balanced accuracy, nominal precision/recall, artifact recall, F1, ROC-AUC, average precision ve confusion matrix baseline'larla birlikte raporlanacak. Tek seed ve az sayıda test alanıyla sonuçların belirsizliği açık tutulacak; güven aralıkları bu ilk pilotta hesaplanmayacak.
- Veri kalite kaydı, bölme kimlikleri, test tahminleri, eğitim geçmişi, paket sürümleri ve model artifact olarak saklanacak. Ham veri ve model ağırlıkları Git deposuna eklenmeyecek.
