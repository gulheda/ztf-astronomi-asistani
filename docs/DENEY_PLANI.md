# Deney ve kullanılabilirlik planı

Bu dosya ileriye dönük plandır; sonuç içermez.

## Model değerlendirmesi

1. Kaynak dosyaları, etiket eşlemesi, kalite raporu ve nesne bazlı bölme listelerini dondur.
2. Eğitim çoğunluk sınıfını tahmin eden baseline oluştur. Küçük CNN'i aynı bölmelerde eğit.
3. Model seçimini validation loss ile yap; erken durdurma kullan. Test verisine yalnız nihai karar sonrasında bak.
4. Sabit 0.5 eşiğinde accuracy, balanced accuracy, precision, recall, F1, ROC-AUC, average precision ve confusion matrix raporla. Average precision değerini trapezoidal PR-AUC ile aynı isim altında sunma.
5. Test sayısı ve sınıf dağılımını sonuçlarla birlikte ver. Accuracy ≥%85 hedefini baseline ile karşılaştır. Real recall düşükse kaybolan gerçek olayları ayrıca incele.
6. Yanlış pozitif/negatif örnekleri kanal bazında incele. Keskinlik, kenar, eksik piksel, parlak yıldız ve kalabalık alan etkilerini ancak gerçek görüntü kanıtıyla yorumla.
7. Sonraki değerlendirmede nesne bazlı bootstrap güven aralıkları ve zamansal dış test ekle. Mevcut eğitim iskeleti bunları henüz hesaplamıyor.

Eğitim çıktıları: `model.keras`, `metrics.json`, `history.json`, `split.json`, `provenance.json`, `test_predictions.npz`. Paket sürümleri için deney ortamında `pip freeze` çıktısını ve kullanılan kod sürümünü ayrıca sakla. Test seti üzerinde tekrar tekrar ayar yapılırsa yeni bağımsız test gereklidir.

## Türkçe sorgu değerlendirmesi

Önceden hazırlanmış en az 50 sorgu için beklenen koşulları ve sonuç kimliklerini insan tarafından belirle. Desteklenen eş anlamlılar, Türkçe büyük/küçük harf, boş sonuç, hatalı sayı, bilinmeyen koşul ve SQL benzeri girdi grupları bulunsun.

Ölçümler: koşul çözümleme doğruluğu, sonuç kümesi tam eşleşmesi, desteklenmeyen sorgunun açıkça reddedilmesi, p50/p95 yanıt süresi. İlk hedefler proje kararı olarak önerilir: desteklenen sorgularda ≥%90 tam eşleşme, bilinmeyen koşullarda sessiz filtre kaybı olmaması. Bunlar ölçülmüş değer değildir.

## Kullanıcı çalışması

Önerideki 15–20 lisans öğrencisi hedefi korunur. Önce 3 kişilik pilotla görevler ve anlaşılmayan ifadeler düzeltilir; pilot sonuçları nihai örneklemle karıştırılmaz. Katılım süreci ve kurumun gerekli gördüğü değerlendirmeler danışmanla netleştirilir.

Karşılaştırma: aynı veri üzerinde geleneksel filtreli tablo ile Türkçe asistan. Katılımcılar her iki yöntemi kullanır; sıra etkisini azaltmak için yarısında A→B, diğer yarısında B→A uygulanır. Eşdeğer ama farklı görev setleri kullanılır; öğrenme etkisi raporlanır.

Görev örnekleri: belirli zaman aralığındaki gerçek adayları bulma; g bandındaki en parlak üç uyarıyı belirleme; kaynağı belirtilmiş süpernova adaylarını listeleme; boş sonuç ve desteklenmeyen sorguyu yorumlama.

Her görev için anonim katılımcı kodu, koşul, görev kodu, doğru tamamlama, süre (saniye), kullanıcı işlemi sayısı, hata sayısı ve kısa geri bildirim kaydedilir. Teknik işlem sayısının hangi tıklama/komutu kapsadığı pilot öncesinde tanımlanır. İsim/e-posta gerekmiyor.

Analiz: eşleştirilmiş süre farkları, medyan/IQR, başarı oranı, işlem farkı ve belirsizlik. Küçük örneklem nedeniyle evrensel genelleme yapılmaz. Kullanıcı süresi, uygulama yanıt süresi ve CNN çıkarım süresi ayrı raporlanır. Etkinlik hipotezi yalnız doğru tamamlanan görevlerin hızıyla sınırlanmaz; başarısız görevler de sonuçlara dahil edilir.
