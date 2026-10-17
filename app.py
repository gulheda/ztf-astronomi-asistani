"""Çalıştır: .venv/bin/python -m streamlit run app.py"""
from datetime import datetime, timezone
import time
import streamlit as st
from astro_assistant.core import connect, seed_demo, parse_query, query_alerts, explain

st.set_page_config(page_title="Astronomi Asistanı", page_icon="🔭", layout="wide")
st.title("🔭 Astronomi Asistanı")
st.caption("TÜBİTAK 2209-A • ZTF Real/Bogus + Türkçe sorgulama • Başlangıç prototipi")
st.warning("DEMO: Tüm kayıtlar ve skorlar sentetiktir. CNN henüz eğitilmedi; canlı ZTF bağlantısı yoktur.")
if "reference_time" not in st.session_state:
    st.session_state.reference_time = datetime.now(timezone.utc)
now = st.session_state.reference_time
st.sidebar.header("Sorgu ayarları")
threshold = st.sidebar.slider("Real/Bogus skor eşiği", 0.0, 1.0, 0.5, 0.05)
st.sidebar.caption("Skor, gerçek olay olma olasılığı olarak kalibre edilmemiştir.")
st.sidebar.write("Demo referans zamanı (UTC)", now.isoformat(timespec="seconds"))
st.sidebar.info("Real/Bogus, olay türünü belirlemez. Demo türleri ayrıca üretilmiş örnek etiketlerdir.")
with st.form("query_form"):
    question = st.text_input("Astronomik olayları Türkçe sorgulayın", "Son 24 saatteki g bandında en parlak olaylar")
    st.form_submit_button("Sorgula")
st.caption("Örnekler: Son 3 gündeki süpernovalar • Son 48 saatteki asteroidler • En yeni ilk 5 olay")
db = connect()
try:
    seed_demo(db, now)
    started = time.perf_counter()
    query = parse_query(question)
    rows = query_alerts(db, query, now, threshold, demo=True)
    elapsed = (time.perf_counter() - started) * 1000
    left, right = st.columns(2)
    left.metric("Listelenen uyarı", len(rows))
    right.metric("Yerel sorgu süresi", "%.2f ms" % elapsed)
    st.caption("Süre yalnızca sorgu yorumlama ve veritabanı erişimini kapsar; model çıkarımı içermez.")
    with st.expander("Uygulanan filtreler"):
        st.json(explain(query, now, threshold))
    if rows:
        import pandas as pd
        frame = pd.DataFrame(rows)
        st.dataframe(frame, hide_index=True)
        st.subheader("Gökyüzü koordinatları")
        st.scatter_chart(frame, x="ra", y="dec", color="band")
        st.caption("RA ve Dec derece cinsindedir. Grafik koordinat dağılımıdır; eş alanlı gökyüzü haritası değildir.")
        st.download_button("Demo sonuçlarını CSV indir", frame.to_csv(index=False).encode("utf-8-sig"),
                           "demo_sorgu_sonuclari.csv", "text/csv")
    else:
        st.info("Bu filtrelerle kayıt bulunamadı. Zaman aralığını veya skor eşiğini değiştirebilirsiniz.")
except ValueError as error:
    st.error(str(error))
finally:
    db.close()
