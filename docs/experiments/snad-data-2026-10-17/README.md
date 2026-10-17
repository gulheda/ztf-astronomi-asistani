# SNAD gerçek veri biçimi denetimi

17 Ekim 2026 tarihinde iki gerçek arşiv indirildi; yayımlanan boyut ve MD5 değerleriyle eşleşti. SHA256 hesaplandı. [Başarılı çalışma](https://github.com/gulheda/ztf-astronomi-asistani/actions/runs/39026448789), [tam rapor](audit.json).

| Sınıf | 28×28 FITS | 63×63 FITS | İncelenen örnek |
|---|---:|---:|---:|
| Artefakt | 1127 | 1127 | 12 |
| Nominal | 1127 | 1127 | 12 |

Her dış arşiv, iki görüntü boyutu için ayrı iç `fits.zip` içeriyor. Toplam 4508 FITS dosyası sayıldı; aynı nesnenin iki boyutu bağımsız örnek sayılmamalı. Piksel ve başlık incelemesi yalnız deterministik seçilen 24 kesitte yapıldı. Tüm görüntülerin kalite kontrolü henüz yapılmadı.

Örneklerde tek 2D görüntü düzlemi ve float32 piksel verisi doğrulandı. `OID`, `OIDRA`, `OIDDEC`, `FIELDID`, `FILTER`, `FILTERID`, `OBSJD` ve `OBSMJD` başlıkları mevcut. Artefaktlarda `TAGS` var; incelenen nominal örneklerde yok. Bu, kaynak notundaki tek kanallı pilot ihtiyacını destekliyor; science/reference/difference üçlüsü sağlanmıyor.

Kaynak: [Zenodo 15076426](https://doi.org/10.5281/zenodo.15076426), CC-BY-4.0. Etiket ve seçim yanlılığı açıklaması: [veri değerlendirmesi](../../SNAD_VERI_DEGERLENDIRMESI.md). Ham veri repoya eklenmedi. Bu çalışmada model eğitilmedi.

## Sonraki eğitim sözleşmesi

- İlk pilot yalnız 63×63 tek kanallı görüntülerle yapılacak; 28×28 görüntüler aynı deneye eklenmeyecek.
- Etiketler `0=artefakt`, `1=nominal`; deney adı `snad_nominal_artifact` olacak.
- Tüm FITS başlıkları taranıp OID tekrarları, sınıflar arası çakışma, koordinat yakınlığı, NaN/Inf ve boş görüntüler denetlenecek.
- Nesne bazlı bölmeye ek olarak `FIELDID` bazlı dış test hazırlanacak. Bölmeler model sonucuna bakılmadan sabitlenecek.
- Çoğunluk baseline, basit görüntü özellikleri ve küçük tek kanallı CNN aynı bölmelerde karşılaştırılacak.
- Sonuçlar canlı ZTF uyarı Real/Bogus doğruluğu olarak sunulmayacak.

Tekrar üretim (NumPy ve Astropy kurulu ortamda):

```bash
python -m astro_assistant.snad_audit --output output/snad-audit
```

Arşivler sabit boyut/MD5 kontrolünden geçer; ZIP dosyaları diske çıkarılmaz. İç arşiv derinliği ve açılmış dosya boyutları sınırlandırılmıştır. Sentetik arşiv testleri başarıyla çalıştırıldı.
