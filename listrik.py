import streamlit as st
import sqlite3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os

SECRET_KEY = b"inirahasiabangetseriuslo"  # 16, 24, atau 32 byte
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===== Database =====
def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS tagihan (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 sekolah TEXT, bulan TEXT, tahun INTEGER, nominal INTEGER,
                 filename TEXT)""")
    conn.commit()
    c.execute("PRAGMA table_info(tagihan)")
    columns = [col[1] for col in c.fetchall()]
    if "sekolah" not in columns:
        c.execute("ALTER TABLE tagihan ADD COLUMN sekolah TEXT")
        conn.commit()
    conn.close()

# ===== Enkripsi =====
def encrypt_file(file_data):
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(file_data, AES.block_size))
    return cipher.iv + ciphertext

# ===== Dekripsi =====
def decrypt_file(encrypted_data):
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext), AES.block_size)

# ===== Simpan ke DB =====
def save_data(sekolah, bulan, tahun, nominal, filename):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO tagihan (sekolah, bulan, tahun, nominal, filename) VALUES (?, ?, ?, ?, ?)",
              (sekolah, bulan, tahun, nominal, filename))
    conn.commit()
    conn.close()

# ===== Main Program =====
init_db()
menu = st.sidebar.selectbox("Menu", ["Tambah Data", "Lihat Data"])

if menu == "Tambah Data":
    st.header("Data Tagihan Listrik")
    sekolah = st.text_input("Nama Sekolah")
    bulan = st.selectbox("Bulan", ["Januari","Februari","Maret","April","Mei","Juni",
                                   "Juli","Agustus","September","Oktober","November","Desember"])
    tahun = st.number_input("Tahun", min_value=0, value=None, format="%d")
    nominal = st.number_input("Nominal Tagihan (Rp)", min_value=0.0, value=None, format="%.3f")
    file = st.file_uploader("Upload Struk (PDF/JPG/PNG)", type=["pdf","jpg","png"])

    if st.button("Simpan") and file and sekolah.strip():
        encrypted_data = encrypt_file(file.read())
        filename = f"{sekolah}_{bulan}_{tahun}_{file.name}.enc"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, "wb") as f:
            f.write(encrypted_data)
        save_data(sekolah, bulan, tahun, nominal, filename)
        st.success("Data tagihan berhasil disimpan terenkripsi!")

elif menu == "Lihat Data":
    st.header("Daftar Tagihan")
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT id, sekolah, bulan, tahun, nominal, filename FROM tagihan")
    rows = c.fetchall()
    conn.close()

    for row in rows:
        st.write(f"**{row[1]}** - {row[2]} {row[3]} - Rp{row[4]}")
        filepath = os.path.join(UPLOAD_FOLDER, row[5])
        with open(filepath, "rb") as f:
            encrypted_data = f.read()
        st.download_button(f"Download Asli - ID {row[0]}",
                           data=decrypt_file(encrypted_data),
                           file_name=row[5].replace(".enc", ""),
                           mime="application/octet-stream")
