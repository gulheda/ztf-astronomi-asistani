"""Sentetik, elle hesaplanmış kayıtlar; gerçek katılımcı verisi değildir."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from astro_assistant import calisma_analizi as c

BASLIK = "katilimci,sira,kosul,gorev,dogru,sure_sn,islem_sayisi,hata_sayisi,geri_bildirim\n"
# p1..p4 × G1,G2; A süreleri 100,200 / 120,240 / 90,180 / 110,220; B süreleri 40,90 / 50,100 / 45,80 / 60,110.
A_SURE = {"p1": (100, 200), "p2": (120, 240), "p3": (90, 180), "p4": (110, 220)}
B_SURE = {"p1": (40, 90), "p2": (50, 100), "p3": (45, 80), "p4": (60, 110)}


def sentetik_csv(a_dogru_p3_g2=0):
    satirlar = []
    for kimlik, sira in (("p1", "AB"), ("p2", "BA"), ("p3", "AB"), ("p4", "BA")):
        for i, gorev in enumerate(("G1", "G2")):
            dogru_a = a_dogru_p3_g2 if (kimlik, gorev) == ("p3", "G2") else 1
            satirlar.append(f"{kimlik},{sira},A,{gorev},{dogru_a},{A_SURE[kimlik][i]},10,1,")
            satirlar.append(f"{kimlik},{sira},B,{gorev},1,{B_SURE[kimlik][i]},4,0,")
    return BASLIK + "\n".join(satirlar) + "\n"


class Dosyali(unittest.TestCase):
    def yaz(self, metin):
        klasor = tempfile.TemporaryDirectory()
        self.addCleanup(klasor.cleanup)
        yol = Path(klasor.name) / "kayit.csv"
        yol.write_text(metin, encoding="utf-8")
        return yol


class OzetTests(Dosyali):
    def test_ozet_elle_hesaplanan_degerler(self):
        ozet = c.ozet(c.oku(self.yaz(sentetik_csv())))
        a, b = ozet["A"], ozet["B"]
        self.assertEqual((a["gorev_sayisi"], a["katilimci_sayisi"]), (8, 4))
        self.assertEqual((a["basari"], b["basari"]), ((7, 8), (8, 8)))
        # A süreleri sıralı: 90,100,110,120,180,200,220,240 -> medyan 150, Q1 107.5, Q3 205.
        self.assertEqual((a["sure_sn_tum_gorevler"]["medyan"], a["sure_sn_tum_gorevler"]["q1"],
                          a["sure_sn_tum_gorevler"]["q3"]), (150.0, 107.5, 205.0))
        # B süreleri sıralı: 40,45,50,60,80,90,100,110 -> medyan 70.
        self.assertEqual(b["sure_sn_tum_gorevler"]["medyan"], 70.0)
        # Yanlış tamamlanan p3/G2 (180 sn) 'yalnız doğru' dağılımından çıkar: 7 gözlem, medyan 120.
        self.assertEqual((a["sure_sn_yalniz_dogru"]["n"], a["sure_sn_yalniz_dogru"]["medyan"]), (7, 120.0))
        self.assertEqual((a["islem_sayisi"]["medyan"], b["islem_sayisi"]["medyan"]), (10, 4))
        self.assertEqual((a["hata_sayisi_toplam"], b["hata_sayisi_toplam"]), (8, 0))

    def test_tek_gozlemde_ceyrek_yok(self):
        satirlar = c.oku(self.yaz(BASLIK + "p1,AB,A,G1,1,50,3,0,\n"))
        dagilim = c.ozet(satirlar)["A"]["sure_sn_tum_gorevler"]
        self.assertEqual((dagilim["n"], dagilim["medyan"], dagilim["q1"]), (1, 50.0, None))
        self.assertEqual(c.ozet(satirlar)["B"]["sure_sn_tum_gorevler"]["n"], 0)


class FarkTests(Dosyali):
    def test_eslesmis_farklar(self):
        farklar = c.eslesmis_farklar(c.oku(self.yaz(sentetik_csv())))
        self.assertEqual(farklar["p1"], [("G1", 60.0, 6, 0), ("G2", 110.0, 6, 0)])
        self.assertEqual(farklar["p3"][1], ("G2", 100.0, 6, -1))

    def test_medyan_fark_ve_aralik(self):
        ozet = c.fark_ozeti(c.oku(self.yaz(sentetik_csv())), tekrar=2000)
        # Farklar sıralı: 45,50,60,70,100,110,110,140 -> medyan 85. Hepsi pozitif => aralık 0'ı içermez.
        sure = ozet["sure_sn_A_eksi_B"]
        self.assertEqual(sure["medyan"], 85.0)
        self.assertGreater(sure["aralik_95"][0], 0)
        self.assertLessEqual(sure["aralik_95"][0], 85.0)
        self.assertGreaterEqual(sure["aralik_95"][1], 85.0)
        self.assertEqual(ozet["islem_A_eksi_B"]["medyan"], 6)
        self.assertEqual((ozet["katilimci_sayisi"], ozet["cift_sayisi"]), (4, 8))

    def test_tekrarlanabilir(self):
        satirlar = c.oku(self.yaz(sentetik_csv()))
        self.assertEqual(c.fark_ozeti(satirlar, tekrar=500, tohum=7), c.fark_ozeti(satirlar, tekrar=500, tohum=7))

    def test_tek_katilimci_belirsizlik_vermez(self):
        yol = self.yaz(BASLIK + "p1,AB,A,G1,1,100,10,0,\np1,AB,B,G1,1,40,4,0,\n")
        with self.assertRaises(ValueError):
            c.fark_ozeti(c.oku(yol))
        self.assertIn("uyari", c.analiz(yol)["farklar"])

    def test_eslesmeyen_gorev_atlanir(self):
        yol = self.yaz(sentetik_csv() + "p1,AB,A,G3,1,70,5,0,\n")
        self.assertEqual(len(c.eslesmis_farklar(c.oku(yol))["p1"]), 2)


class DogrulamaTests(Dosyali):
    def hata(self, satir, parca):
        with self.assertRaises(ValueError) as baglam:
            c.oku(self.yaz(BASLIK + satir + "\n"))
        self.assertIn(parca, str(baglam.exception))

    def test_gecersiz_satirlar(self):
        self.hata("p1,AB,C,G1,1,10,1,0,", "kosul")
        self.hata("p1,XX,A,G1,1,10,1,0,", "sira")
        self.hata("p1,AB,A,G1,2,10,1,0,", "dogru")
        self.hata("p1,AB,A,G1,1,-5,1,0,", "sure_sn")
        self.hata("p1,AB,A,G1,1,nan,1,0,", "sure_sn")
        self.hata("p1,AB,A,G1,1,abc,1,0,", "sure_sn")
        self.hata("p1,AB,A,G1,1,10,-1,0,", "islem_sayisi")
        self.hata("p1,AB,A,G1,1,10,1.5,0,", "islem_sayisi")
        self.hata("p1,AB,A,G1,1,10,1,x,", "hata_sayisi")
        self.hata(",AB,A,G1,1,10,1,0,", "katilimci")

    def test_satir_numarasi_bildirilir(self):
        with self.assertRaises(ValueError) as baglam:
            c.oku(self.yaz(BASLIK + "p1,AB,A,G1,1,10,1,0,\np1,AB,A,G2,5,10,1,0,\n"))
        self.assertIn("Satır 3", str(baglam.exception))

    def test_yinelenen_kayit(self):
        with self.assertRaises(ValueError):
            c.oku(self.yaz(BASLIK + "p1,AB,A,G1,1,10,1,0,\np1,AB,A,G1,1,12,1,0,\n"))

    def test_sutunlar_ve_bos_dosya(self):
        with self.assertRaises(ValueError):
            c.oku(self.yaz("katilimci,kosul\np1,A\n"))
        with self.assertRaises(ValueError):
            c.oku(self.yaz(BASLIK))


class KomutSatiriTests(Dosyali):
    def test_cikti_json(self):
        import json
        yol = self.yaz(sentetik_csv())
        cikti = io.StringIO()
        with contextlib.redirect_stdout(cikti):
            import sys
            eski = sys.argv
            sys.argv = ["calisma_analizi", str(yol), "--tekrar", "200"]
            try:
                c.main()
            finally:
                sys.argv = eski
        rapor = json.loads(cikti.getvalue())
        self.assertEqual(rapor["farklar"]["sure_sn_A_eksi_B"]["medyan"], 85.0)
        self.assertIn("genelleme", rapor["not"])

    def test_hatali_dosya_cikis_kodu(self):
        import sys
        eski = sys.argv
        sys.argv = ["calisma_analizi", str(self.yaz("bozuk\n"))]
        try:
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as baglam:
                c.main()
        finally:
            sys.argv = eski
        self.assertEqual(baglam.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
