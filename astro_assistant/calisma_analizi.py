"""Kullanıcı çalışması kayıtlarının analizi: başarı, süre, işlem sayısı ve eşleştirilmiş farklar.

Koşul A: geleneksel filtreli tablo, koşul B: Türkçe asistan. Başarısız görevler süre ve işlem
analizine dahildir (DENEY_PLANI.md); başarı oranı ayrıca raporlanır. Belirsizlik, katılımcı düzeyinde
yeniden örnekleme (küme bootstrap) ile verilir, çünkü aynı katılımcının görevleri bağımsız değildir.
Çalıştır: python -m astro_assistant.calisma_analizi kayit.csv
"""
import argparse
import csv
import json
import math
import random
import statistics
from pathlib import Path

ALANLAR = ("katilimci", "sira", "kosul", "gorev", "dogru", "sure_sn", "islem_sayisi", "hata_sayisi", "geri_bildirim")
KOSULLAR = ("A", "B")
SIRALAR = ("AB", "BA")


def _tam_sayi(deger, ad, satir, en_az=0):
    try:
        sayi = int(deger)
    except (TypeError, ValueError):
        raise ValueError(f"Satır {satir}: {ad} tam sayı olmalı: {deger!r}")
    if str(sayi) != str(deger).strip() or sayi < en_az:
        raise ValueError(f"Satır {satir}: {ad} tam sayı ve en az {en_az} olmalı: {deger!r}")
    return sayi


def oku(yol):
    """CSV'yi doğrulayarak okur; hatalı satırda satır numarasıyla ValueError verir."""
    with Path(yol).open(encoding="utf-8-sig", newline="") as dosya:
        okuyucu = csv.DictReader(dosya)
        if tuple(okuyucu.fieldnames or ()) != ALANLAR:
            raise ValueError("Sütunlar şu sırayla olmalı: " + ",".join(ALANLAR))
        satirlar, gorulen = [], set()
        for numara, ham in enumerate(okuyucu, start=2):
            kosul, katilimci, gorev = ham["kosul"].strip(), ham["katilimci"].strip(), ham["gorev"].strip()
            if not katilimci or not gorev:
                raise ValueError(f"Satır {numara}: katilimci ve gorev boş olamaz.")
            if kosul not in KOSULLAR:
                raise ValueError(f"Satır {numara}: kosul A veya B olmalı: {kosul!r}")
            if ham["sira"].strip() not in SIRALAR:
                raise ValueError(f"Satır {numara}: sira AB veya BA olmalı: {ham['sira']!r}")
            dogru = _tam_sayi(ham["dogru"], "dogru", numara)
            if dogru not in (0, 1):
                raise ValueError(f"Satır {numara}: dogru 0 veya 1 olmalı.")
            try:
                sure = float(ham["sure_sn"])
            except ValueError:
                raise ValueError(f"Satır {numara}: sure_sn sayı olmalı: {ham['sure_sn']!r}")
            if not math.isfinite(sure) or sure <= 0:
                raise ValueError(f"Satır {numara}: sure_sn pozitif ve sonlu olmalı.")
            anahtar = (katilimci, kosul, gorev)
            if anahtar in gorulen:
                raise ValueError(f"Satır {numara}: yinelenen kayıt {anahtar}")
            gorulen.add(anahtar)
            satirlar.append(dict(katilimci=katilimci, sira=ham["sira"].strip(), kosul=kosul, gorev=gorev,
                                 dogru=dogru, sure_sn=sure,
                                 islem_sayisi=_tam_sayi(ham["islem_sayisi"], "islem_sayisi", numara),
                                 hata_sayisi=_tam_sayi(ham["hata_sayisi"], "hata_sayisi", numara),
                                 geri_bildirim=ham["geri_bildirim"].strip()))
    if not satirlar:
        raise ValueError("Kayıt dosyasında veri satırı yok.")
    return satirlar


def _dagilim(degerler):
    """Medyan ve çeyrekler (inclusive yöntem); tek gözlemde çeyrek tanımsızdır."""
    if not degerler:
        return dict(n=0, medyan=None, q1=None, q3=None)
    if len(degerler) == 1:
        return dict(n=1, medyan=degerler[0], q1=None, q3=None)
    q1, _, q3 = statistics.quantiles(degerler, n=4, method="inclusive")
    return dict(n=len(degerler), medyan=statistics.median(degerler), q1=q1, q3=q3)


def ozet(satirlar):
    """Koşula göre başarı oranı, süre ve işlem sayısı dağılımı."""
    sonuc = {}
    for kosul in KOSULLAR:
        grup = [s for s in satirlar if s["kosul"] == kosul]
        sonuc[kosul] = dict(
            gorev_sayisi=len(grup),
            katilimci_sayisi=len({s["katilimci"] for s in grup}),
            basari=(sum(s["dogru"] for s in grup), len(grup)),
            sure_sn_tum_gorevler=_dagilim([s["sure_sn"] for s in grup]),
            sure_sn_yalniz_dogru=_dagilim([s["sure_sn"] for s in grup if s["dogru"]]),
            islem_sayisi=_dagilim([s["islem_sayisi"] for s in grup]),
            hata_sayisi_toplam=sum(s["hata_sayisi"] for s in grup))
    return sonuc


def eslesmis_farklar(satirlar):
    """Aynı katılımcı ve görev için A − B farkları: {katilimci: [(gorev, sure, islem, dogru), ...]}.

    Pozitif süre/işlem farkı, B'nin (Türkçe asistan) daha hızlı/az işlemle bittiği anlamına gelir.
    """
    tablo = {}
    for s in satirlar:
        tablo.setdefault((s["katilimci"], s["gorev"]), {})[s["kosul"]] = s
    sonuc = {}
    for (katilimci, gorev), cift in sorted(tablo.items()):
        if "A" in cift and "B" in cift:
            a, b = cift["A"], cift["B"]
            sonuc.setdefault(katilimci, []).append(
                (gorev, a["sure_sn"] - b["sure_sn"], a["islem_sayisi"] - b["islem_sayisi"], a["dogru"] - b["dogru"]))
    return sonuc


def _kume_bootstrap(katilimci_farklari, indeks, tekrar, tohum):
    """Katılımcıları yerine koyarak çeker; her çekimde medyan fark. %95 yüzdelik aralığı döndürür."""
    rastgele = random.Random(tohum)
    kimlikler = sorted(katilimci_farklari)
    medyanlar = []
    for _ in range(tekrar):
        havuz = [fark[indeks] for kimlik in (rastgele.choice(kimlikler) for _ in kimlikler)
                 for fark in katilimci_farklari[kimlik]]
        medyanlar.append(statistics.median(havuz))
    medyanlar.sort()
    return medyanlar[int(0.025 * (tekrar - 1))], medyanlar[int(math.ceil(0.975 * (tekrar - 1)))]


def fark_ozeti(satirlar, tekrar=10000, tohum=42):
    """Eşleştirilmiş farkların medyanı ve katılımcı-düzeyi bootstrap %95 aralığı (en az 2 katılımcı)."""
    farklar = eslesmis_farklar(satirlar)
    if len(farklar) < 2:
        raise ValueError("Belirsizlik hesabı için her iki koşulu tamamlamış en az 2 katılımcı gerekir.")
    sonuc = dict(katilimci_sayisi=len(farklar), cift_sayisi=sum(len(v) for v in farklar.values()),
                 yontem=f"katılımcı düzeyinde bootstrap, {tekrar} tekrar, tohum {tohum}, %95 yüzdelik aralığı")
    for ad, indeks in (("sure_sn_A_eksi_B", 1), ("islem_A_eksi_B", 2), ("dogru_A_eksi_B", 3)):
        degerler = [fark[indeks] for liste in farklar.values() for fark in liste]
        alt, ust = _kume_bootstrap(farklar, indeks, tekrar, tohum)
        sonuc[ad] = dict(medyan=statistics.median(degerler), aralik_95=(alt, ust))
    return sonuc


def analiz(yol, tekrar=10000, tohum=42):
    satirlar = oku(yol)
    rapor = dict(ozet=ozet(satirlar))
    try:
        rapor["farklar"] = fark_ozeti(satirlar, tekrar, tohum)
    except ValueError as hata:
        rapor["farklar"] = {"uyari": str(hata)}
    rapor["not"] = ("Küçük örneklemde aralıklar geniştir ve genelleme yapılmaz. Pilot kayıtlarını nihai "
                    "örneklemle birleştirmeyin. Başarısız görevler süre analizine dahildir.")
    return rapor


def main():
    ayrac = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ayrac.add_argument("kayit", type=Path)
    ayrac.add_argument("--tekrar", type=int, default=10000)
    ayrac.add_argument("--tohum", type=int, default=42)
    args = ayrac.parse_args()
    if not 100 <= args.tekrar <= 200000:
        ayrac.error("tekrar 100 ile 200000 arasında olmalı.")
    try:
        rapor = analiz(args.kayit, args.tekrar, args.tohum)
    except (ValueError, OSError) as hata:
        ayrac.error(str(hata))
    print(json.dumps(rapor, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
