# Günlük ilerleme

## 2026-11-06
Çözümleyici sayısız "son hafta/gün/saat" biçimini 1 birim olarak tanıyor ("son hafta olaylar" = 168 saat); değerlendirme seti 160'tan 165 sorguya çıkarıldı (beklenen davranış önce elle yazıldı, dört sorgu önceki gramerde reddediliyordu; "son ay" reddedilmeye devam ediyor). README ve SORGU_DEGERLENDIRMESI.md sayıları güncellendi.

## 2026-11-05
Çözümleyici isimleşmiş "olanlar/gelenler/gözlenenler" dolgu sözcüklerini tanıyor ("son 6 saatte olanlar"); değerlendirme seti 154'ten 160 sorguya çıkarıldı (beklenen davranış önce elle yazıldı, dört sorgu önceki gramerde reddediliyordu; olumsuz "gözlenmeyenler" reddedilmeye devam ediyor). README ve SORGU_DEGERLENDIRMESI.md sayıları güncellendi.

## 2026-11-04
Desteklenmeyen zaman birimleri (dakika, saniye, ay, yıl) artık yanıltıcı "Desteklenmeyen ifade: son" yerine birimi adlandıran açık bir hata veriyor ("Saat, gün veya hafta kullanın"); gramer kapsamı değişmedi. Değerlendirme seti 151'den 154 sorguya çıkarıldı (U52–U54, hepsi reddedilen), hata iletisi için birim testi eklendi; README ve SORGU_DEGERLENDIRMESI.md sayıları güncellendi.

## 2026-11-03
Çözümleyici tür sözcüklerinin tamlayan ekini ("supernovaların", "asteroidlerin") ve "gözlenmiş/gelmiş" dolgu sıfat-fiillerini tanıyor; değerlendirme seti 145'ten 151 sorguya çıkarıldı (beklenen davranış önce elle yazıldı, dört sorgu önceki gramerde reddediliyordu; "gözlenmemiş" reddedilmeye devam ediyor). SORGU_DEGERLENDIRMESI.md'deki eskimiş n sayıları (88/49) ölçüm çıktısına göre düzeltildi.

## 2026-11-02
Çözümleyici sorgu ortasındaki noktalamayı ("son 24 saat? olaylar", "son 3 gün. g bandındaki olaylar") ayırıcı sayıyor; önceden boş belirteçli "Desteklenmeyen ifade: ." hatası veriyordu. Değerlendirme seti 141'den 145 sorguya çıkarıldı (beklenen davranış önce elle yazıldı, üç sorgu önceki gramerde reddediliyordu); README ve SORGU_DEGERLENDIRMESI.md sayıları güncellendi.

## 2026-11-01
Çözümleyici "olan", "neler" ve "nelerdir" dolgu sözcüklerini tanıyor ("son 24 saatteki olaylar nelerdir"); değerlendirme seti 137'den 141 sorguya çıkarıldı (beklenen davranış önce elle yazıldı). "en parlak 5 olay" (ilk olmadan sayı) belgelenmiş karar gereği reddedilmeye devam ediyor. README ve SORGU_DEGERLENDIRMESI.md sayıları güncellendi.

## 2026-10-31
Çözümleyici anlamı değiştirmeyen "için" dolgu sözcüğünü tanıyor ("son 24 saat için g bandındaki olaylar"); değerlendirme seti 129'dan 137 sorguya çıkarıldı (beklenen davranış önce elle yazıldı, altı sorgu önceki gramerde reddediliyordu). README ve SORGU_DEGERLENDIRMESI.md'deki yanlış sayılar (127, n=47) ölçüm çıktısına göre düzeltildi.

## 2026-10-30
Çözümleyici "gözlenen/gelen" sıfat-fiillerini, "listesi" ve "olayların/adayların/adaylarının" tamlayan biçimlerini tanıyor; değerlendirme seti 121'den 127 sorguya çıkarıldı (beklenen davranış önce elle yazıldı, altı sorgu önceki gramerde reddediliyordu; olumsuzlama ve sayım sorusu reddedilmeye devam ediyor). README ve SORGU_DEGERLENDIRMESI.md sayıları güncellendi.

## 2026-10-29
Çözümleyici "g bandı olayları", "r filtresi adayları", "i bandı için ..." yalın biçimlerini ve "son 24 saati göster" gibi belirtme halini tanıyor; değerlendirme seti 113'ten 121 sorguya çıkarıldı (beklenen davranış önce elle yazıldı, altı sorgu önceki gramerde reddediliyordu). SORGU_DEGERLENDIRMESI.md'deki eskimiş n sayıları ölçüm çıktısına göre düzeltildi.

## 2026-10-28
Çözümleyici "son/ilk" sonrasında bir–on yazıyla sayıları ("son üç gün", "ilk beş aday") ve "filtre" sözcüğünü ("r filtresindeki") tanıyor; değerlendirme seti 104'ten 113 sorguya çıkarıldı (beklenen davranış önce elle yazıldı, altı sorgu önceki gramerde reddediliyordu). Eski "son on gün" ret vakası bilinçli olarak "yirmi" ile değiştirildi; belgeler güncellendi.

## 2026-10-27
Çözümleyici "hafta" birimini (1 hafta = 168 saat), tamlayan ekini ("son 3 günün olayları") ve "adaylarını/olaylarını" biçimlerini tanıyor; değerlendirme seti 95'ten 104 sorguya çıkarıldı (beklenen davranış önce elle yazıldı, altı sorgu önceki gramerde reddediliyordu). Eski "son 1 hafta" ret vakası bilinçli olarak "yıl" ile değiştirildi; belgeler güncellendi.

## 2026-10-26
Çözümleyici "tane/adet/tüm/bütün" dolgu sözcüklerini ve "içerisinde/içerisindeki" zaman ekini tanıyor; değerlendirme seti 87'den 95 sorguya çıkarıldı (beklenen davranış önce elle yazıldı, altı sorgu önceki gramerde reddediliyordu). README ve SORGU_DEGERLENDIRMESI.md sayıları güncellendi.

## 2026-10-25
Çözümleyici virgül ayırıcıyı ("son 24 saat, olaylar" önceden boş belirteçli hata veriyordu), "olayı", "asteroit" yazımını ve "saatlik/günlük" ekini tanıyor; değerlendirme seti 79'dan 87 sorguya çıkarıldı (beklenen davranış önce elle yazıldı, altı sorgu önceki gramerde reddediliyordu). README ve SORGU_DEGERLENDIRMESI.md sayıları güncellendi.

## 2026-10-24
Çözümleyici "saat/gün içinde", "içindeki", "adayı", "getir" ve "bana" ifadelerini tanıyor; değerlendirme seti 71'den 79 sorguya çıkarıldı (beklenen davranış önce elle yazıldı, altı sorgu önceki gramerde reddediliyordu). SORGU_DEGERLENDIRMESI.md'deki yanlış n sayıları (37/28 yerine 39/32) düzeltildi.

## 2026-10-23
Çözümleyici "g bandındaki olaylar" biçimini tanıyor; değerlendirme seti 65'ten 71 sorguya çıkarıldı (bandındaki eki ve tekrarlanan zaman/sayı/bant/tür filtrelerinin reddi). Beklenen davranış önce elle yazıldı; README ve SORGU_DEGERLENDIRMESI.md sayıları güncellendi.

## 2026-10-22
Türkçe sorgu değerlendirme seti 56'dan 65 sorguya çıkarıldı (önce beklenen davranış elle yazıldı). Çözümleyici "adaylar", "süpernovaları" ve "asteroidleri" biçimlerini tanıyor; SORGU_DEGERLENDIRMESI.md ve README güncellendi.
