import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# KONFIGURASI APLIKASI STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Chatbot Ahli Masak",
    page_icon="🍳",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("🍳 Chatbot Ahli Masak")
st.write("Tanya saya resep masakan apa pun, dan saya akan berikan. Jika pertanyaan Anda bukan tentang masakan, saya tidak akan menjawab.")
st.write("---")

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================
# Mengambil API Key dari Streamlit Secrets.
# Pastikan Anda telah mengonfigurasinya di dashboard Streamlit Anda.
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("API Key Gemini tidak ditemukan! Silakan tambahkan 'GEMINI_API_KEY' ke Streamlit Secrets.")
    st.stop()
except Exception as e:
    st.error(f"Kesalahan konfigurasi API: {e}")
    st.stop()

# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# MANAJEMEN RIWAYAT CHAT
# ==============================================================================
# Inisialisasi riwayat chat jika belum ada.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "user",
            "parts": ["Saya adalah ahli masak. Saya akan memberikan berbagai macam jenis resep masakan yang anda inginkan. Jawaban singkat dan jelas. Tolak pertanyaan selain masakan."]
        },
        {
            "role": "model",
            "parts": ["Tentu! Saya akan berikan resep yang Anda inginkan. Silakan tanyakan."]
        }
    ]

# Tampilkan riwayat chat sebelumnya di antarmuka.
for message in st.session_state.messages:
    # Jangan tampilkan pesan dari role 'user' yang berisi instruksi awal
    if message["role"] != "user" or "Saya adalah ahli masak" not in message["parts"][0]:
        with st.chat_message(message["role"]):
            st.markdown(message["parts"][0])

# ==============================================================================
# INTERAKSI PENGGUNA DAN GENERASI RESPON
# ==============================================================================
# Input prompt dari pengguna
if prompt := st.chat_input("Tulis nama resep masakan di sini..."):
    # Tambahkan prompt pengguna ke riwayat chat.
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Inisialisasi model dan sesi chat
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )

    # Mulai sesi chat dengan riwayat yang ada
    chat_session = model.start_chat(history=st.session_state.messages)

    # Kirim pesan ke model dan dapatkan respons
    with st.chat_message("assistant"):
        with st.spinner("Sedang mencari resep..."):
            try:
                response = chat_session.send_message(prompt, request_options={"timeout": 60})
                
                # Cek respons yang valid sebelum ditampilkan
                if response and response.text:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "parts": [response.text]})
                else:
                    st.markdown("Maaf, terjadi kesalahan atau tidak ada respons.")

            except Exception as e:
                st.error(f"Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini: {e}")
                st.info("Kemungkinan: masalah koneksi, API key tidak valid, atau melebihi kuota.")
