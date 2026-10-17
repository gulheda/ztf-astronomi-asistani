# Veri sözleşmesi ve yöntem kararları

## Bilimsel düzeltmeler

Real/Bogus, görüntüdeki tespitin güvenilirliğiyle ilgili ikili sınıflandırmadır. “Real” olması olayın süpernova/asteroid olduğunu veya bilimsel olarak yeni bir anomali olduğunu kanıtlamaz. Tür bilgisi ayrı, kaynaklı bir alan olmalıdır. Bu ayrım kodda `kind_source` ile izlenir.

Öneride braai ile Carrasco-Davis (2021) ilişkilendirilmiş; braai için doğruladığımız esas kaynak Duev ve arkadaşları (2019). Diğer kaynakların yazar, başlık, DOI ve hangi iddiayı desteklediği ayrıca denetlenmeli. “Astronomiye hiç uygulanmadı” ve “ilk” gibi özgünlük iddiaları sistematik tarama yapılmadan kullanılmamalı.

## Kaynak kabul kontrolü

- Doğrudan dosya URL'si ve veri üreticisi belli olmalı. IRSA görüntü kataloğunun varlığı, aynı yerde hazır insan etiketli Real/Bogus paketi bulunduğu anlamına gelmez.
- Etiketin kaynağı açık olmalı. Hazır modelin `rb`/`drb` skorunu eşikleyip bağımsız insan doğrusu gibi kullanmak geçerli başarı ölçümü değildir.
- Lisans/kullanım koşulları, indirme zamanı, sürüm ve SHA256 saklanmalı.
- Nesne kimliği bulunmuyorsa nesne bazlı bağımsız test garanti edilemez. Bölme stratejisi değiştirilmeden sonuç raporlanmaz.
- Görüntü veri setinde konum/zaman meta verisi yoksa arayüz için ayrıca eşleşebilir kaynak gerekir; bunlar uydurulmaz.

## Eğitim dosyası

Yerel dönüştürücünün hedefi `ztf.npz`; bu, kaynak arşivin doğal formatı olduğu iddiası değildir.

| Alan | Tip/şekil | Anlam |
|---|---|---|
| images | float, N×63×63×3 | Sırasıyla science, reference, difference; RGB fotoğraf değil |
| labels | int, N | 0=bogus, 1=real; kaynağın gerçek etiket eşlemesi kontrol edilir |
| object_ids | Unicode, N | Aynı fiziksel nesnenin ortak kimliği |
| alert_ids | Unicode, N | Her uyarı için tekil kimlik |

63×63×3, braai çalışmasından alınan başlangıç sözleşmesidir. Daha küçük kesitlerde padding/mask ve daha büyüklerde kırpma kararı gerçek veri incelemesinden sonra dönüştürücüye eklenecek. Mevcut okuyucu yanlış şekli veya NaN/Inf'i sessizce düzeltmez.

Örnek `provenance.json` şablonu (boş alanları doldurmadan eğitim başlamaz):

```json
{
  "source_url": "",
  "retrieved_at": "",
  "label_definition": "",
  "label_source": "",
  "license": "",
  "sha256": "",
  "label_kind": "human_reviewed",
  "labels_independent_of_model": true,
  "label_review_reference": "",
  "is_demo": false
}
```

`sha256` dönüştürülmüş NPZ'nin özetidir. Kaynak ham dosyaların özetleri ayrıca saklanmalı. Formu doldurmak bilimsel kaynak doğrulamasının yerine geçmez.
Eğitim komutu insan tarafından incelenmiş, modelden bağımsız etiket beyanını zorunlu tutar. Bu beyanın doğruluğu ayrıca kaynak incelemesiyle denetlenir; otomatik şema kontrolü etiketi kanıtlamaz.

## Ön işleme ve bölme

Her kanala ayrı L2 normalizasyonu uygulanır; işaretli difference pikselleri korunur. Birebir tekrarlar durdurulur; yakın kopyalar görsel/benzerlik incelemesi gerektirir. Grup kimliklerinin yaklaşık %70/%15/%15'i eğitim/doğrulama/teste gider; örnek oranları grup boyutları nedeniyle değişebilir. Tohum 42; her bölümde iki sınıfın da bulunması şarttır. Veri azlığı bu şartı bozarsa test sonucuna bakarak tekrar tohum aramak yerine bölme tasarımı önceden düzeltilir.

Artırma yalnız eğitimde yatay/dikey çevirme ile uygulanır. Geometrik dönüşüm tüm kanallara birlikte uygulanır. Rastgele parlaklık değişimi ilk deneyde yoktur. Gruplu ayırmaya ek olarak farklı gecelerde alınmış zamansal dış test sonraki deneydir.

## Uyarı veritabanı

`alert_id`, `object_id`, `observed_at` (UTC ISO), `ra` [0,360), `dec` [-90,90], `magnitude` (boş olabilir), `band` (g/r/i), `real_score` [0,1], `model_version`, `source`, opsiyonel `kind`/`kind_source`, `is_demo`.

CNN çıktısının doğrulanmış gerçek etiket olmadığı açık tutulur. Tüm skorlar saklanır; sorguda eşik uygulanır. Başlangıç eşiği 0.5; kullanıcıya gösterilen skor kalibre edilmiş olasılık değildir. Parlaklık sıralaması yalnız aynı bantta yapılır. Çıktı birimi uyarıdır; aynı nesnenin farklı zamanlardaki uyarıları otomatik birleştirilmez.

## Henüz yapılmayanlar

Ham ZTF/FITS/Avro dönüştürücüsü, gerçek veri indirme, eğitim çalıştırması, modelden skor üretme komutu, görüntülerin arayüzde gösterilmesi, gerçek tür kataloğu eşlemesi ve canlı akış bağlantısı. Bunlar veri kaynağı kesinleştikten sonra geliştirilecek.
