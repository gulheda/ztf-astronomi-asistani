# Birlikte geliştirme

Çalışmaları [Issues](https://github.com/gulheda/ztf-astronomi-asistani/issues) üzerinden takip ediyoruz.

1. Yapılacak işi ve kabul ölçütlerini bir issue'da tanımla.
2. Güncel `main` üzerinden `feat/issue-1-veri-kaynagi` gibi kısa bir dal aç.
3. Değişiklikleri küçük, anlamlı commit'lerle kaydet.
4. `python -m unittest discover -s tests -v` komutunu çalıştır. Streamlit kurulu değilse arayüz testleri atlanır; GitHub Actions bunları kurulu ortamda çalıştırır.
5. Pull request aç; ilgili issue'yu bağla, değişikliği ve doğrulama sonucunu yaz. İş tamamen bittiyse `Closes #1` kullan.
6. GitHub Actions sonucu ve değişiklikler incelendikten sonra `main` dalına birleştir.

## Araştırma kayıtları

Deneylerde veri kaynağı/sürümü, etiket tanımı, nesne bazlı bölme, rastgele tohum ve kullanılan kod commit'ini kaydet. Başarı ölçülmeden sonuç yazma. Demo ve gerçek veriyi açıkça ayır.

Büyük veri ve model ağırlıkları Git geçmişine eklenmez; kaynak adresi, SHA256 ve yeniden üretim komutu belgelenir. API anahtarları `.env` veya yerel secrets dosyasında tutulur. Proje önerisi gibi ekip bilgileri içeren kaynak belgeler yerine depodaki araştırma notları kullanılır.
