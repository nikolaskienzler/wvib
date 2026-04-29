import os
import requests
import streamlit as st

st.set_page_config(page_title="KI Wartungsassistent", layout="wide")

st.title("🛠️ KI Wartungsassistent – Prototyp")
st.write("Spezifische Unterstützung bei Problemen an Rundschleifmaschinen")

def get_api_key():
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return os.getenv("OPENAI_API_KEY")

def frage_chatgpt(maschine, problem, versuche):
    api_key = get_api_key()

    if not api_key:
        return (
            "Kein API-Key gefunden. Bitte lege eine Datei "
            "`prototype/.streamlit/secrets.toml` an oder setze die Umgebungsvariable "
            "`OPENAI_API_KEY`."
        )

    prompt = f"""
Du bist ein erfahrener Fertigungs- und Instandhaltungsassistent für Rundschleifmaschinen.

Antworte praxisnah, vorsichtig und strukturiert.
Erfinde keine historischen Fälle.
Wenn Informationen fehlen, sage klar, welche fehlen.

Maschine:
{maschine}

Problem:
{problem}

Bereits versucht:
{versuche}

Gib aus:
1. Wahrscheinlichste Ursachen
2. Sofort-Checks
3. Empfohlene nächste Schritte
4. Sicherheits- oder Qualitätsrisiken
5. Welche Informationen noch fehlen
"""

    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4.1-mini",
            "input": prompt,
            "max_output_tokens": 700,
        },
        timeout=30,
    )

    if response.status_code != 200:
        return f"API-Fehler: {response.status_code} – {response.text}"

    data = response.json()

    try:
        return data["output"][0]["content"][0]["text"]
    except Exception:
        return str(data)

maschine = st.text_input("Maschine / Anlage", placeholder="z. B. Rundschleifmaschine 1")
problem = st.text_area(
    "Problem beschreiben",
    placeholder="z. B. Schleifbild schlecht, Maschine stoppt, Vibrationen..."
)
versuche = st.text_area(
    "Was wurde bereits versucht?",
    placeholder="z. B. Scheibe abgerichtet, Parameter geprüft..."
)

if st.button("Analyse mit ChatGPT starten"):
    if not problem.strip():
        st.warning("Bitte zuerst ein Problem beschreiben.")
    else:
        with st.spinner("Analyse läuft..."):
            antwort = frage_chatgpt(maschine, problem, versuche)

        st.subheader("🔍 Analyse")
        st.write(antwort)

        st.subheader("📊 Feedback")
        feedback = st.radio(
            "War die Antwort hilfreich?",
            ["Ja", "Teilweise", "Nein"],
            index=None
        )

        if feedback:
            st.success(f"Feedback gespeichert: {feedback}")