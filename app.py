"""Çalıştır: .venv/bin/python -m streamlit run app.py"""
from datetime import datetime, timezone
import json
import time
import streamlit as st
from astro_assistant.archive import load_archive
from astro_assistant.core import connect, seed_demo, insert_alerts, parse_query, query_alerts, explain

st.set_page_config(page_title="Astronomi Asistanı", page_icon="🔭", layout="wide")
st.title("🔭 Astronomi Asistanı")
st.caption("TÜBİTAK 2209-A • ZTF Real/Bogus + Türkçe sorgulama • Başlangıç prototipi")
data_source = st.sidebar.selectbox("Veri kaynağı", ("Demo", "Gerçek ZTF arşivi"))
is_demo = data_source == "Demo"
if "reference_time" not in st.session_state:
    st.session_state.reference_time = datetime.now(timezone.utc)

archive = None
if is_demo:
    now = st.session_state.reference_time
    default_question = "Son 24 saatteki g bandında en parlak olaylar"
    st.warning("DEMO: Tüm kayıtlar ve skorlar sentetiktir; canlı ZTF bağlantısı yoktur.")
else:
    try:
        archive = load_archive()
        now = archive["reference_time"]
    except ValueError as error:
        st.error(str(error))
        st.stop()
    default_question = "Son 365 gündeki olaylar"
    st.info(
        "GERÇEK ZTF ARŞİVİ: Yayımlanmış modelle işlenmiş yalnızca 2 örnek içerir. "
        "Bağımsız doğruluk ölçümü değildir ve canlı ZTF akışı değildir."
    )

st.sidebar.header("Sorgu ayarları")
threshold = st.sidebar.slider("Real/Bogus skor eşiği", 0.0, 1.0, 0.5, 0.05)
st.sidebar.caption("Skor, gerçek olay olma olasılığı olarak kalibre edilmemiştir.")
reference_label = "Demo referans zamanı (UTC)" if is_demo else "Arşiv referans zamanı (UTC)"
st.sidebar.write(reference_label, now.isoformat(timespec="microseconds"))
if is_demo:
    st.sidebar.info("Real/Bogus, olay türünü belirlemez. Demo türleri ayrıca üretilmiş örnek etiketlerdir.")
elif archive:
    provenance = archive["provenance"]
    st.sidebar.caption("Model: " + ", ".join(provenance["model_versions"]))
    st.sidebar.caption("Upstream commit: " + provenance["upstream_commit"])
    with st.expander("Arşiv kaynağı ve model soyu"):
        st.json(provenance)

with st.form("query_form"):
    question = st.text_input(
        "Astronomik olayları Türkçe sorgulayın",
        default_question,
        key="demo_question" if is_demo else "archive_question",
    )
    st.form_submit_button("Sorgula")
if is_demo:
    st.caption("Örnekler: Son 3 gündeki süpernovalar • Son 48 saatteki asteroidler • En yeni ilk 5 olay")
else:
    st.caption("Örnekler: Son 365 gündeki olaylar • En yeni ilk 5 olay")
db = connect()
try:
    if is_demo:
        seed_demo(db, now)
    else:
        insert_alerts(db, archive["records"])
    started = time.perf_counter()
    query = parse_query(question)
    rows = query_alerts(db, query, now, threshold, demo=is_demo)
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
        if not is_demo:
            frame = frame.drop(columns=["kind", "kind_source"])
            metadata = {record["alert_id"]: record for record in archive["records"]}
            frame["upstream_rb"] = frame["alert_id"].map(
                lambda alert_id: metadata[alert_id]["upstream_rb"]
            )
            frame["preprocessing"] = frame["alert_id"].map(
                lambda alert_id: json.dumps(metadata[alert_id]["preprocessing"], ensure_ascii=False)
            )
        st.dataframe(frame, hide_index=True)
        st.subheader("Gökyüzü koordinatları")
        st.scatter_chart(frame, x="ra", y="dec", color="band")
        st.caption("RA ve Dec derece cinsindedir. Grafik koordinat dağılımıdır; eş alanlı gökyüzü haritası değildir.")
        download_label = "Demo sonuçlarını CSV indir" if is_demo else "Arşiv sonuçlarını CSV indir"
        filename = "demo_sorgu_sonuclari.csv" if is_demo else "ztf_arsiv_sorgu_sonuclari.csv"
        st.download_button(download_label, frame.to_csv(index=False).encode("utf-8-sig"),
                           filename, "text/csv")
    else:
        st.info("Bu filtrelerle kayıt bulunamadı. Zaman aralığını veya skor eşiğini değiştirebilirsiniz.")
except ValueError as error:
    st.error(str(error))
finally:
    db.close()
