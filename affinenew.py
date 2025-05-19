import streamlit as st

# Fungsi mencari invers modulo dari a (mod 26)
def mod_inverse(a):
    for i in range(1, 26):
        if (a * i) % 26 == 1:
            return i
    return None

# Fungsi enkripsi
def encrypt(text, a, b):
    hasil = ""
    for huruf in text:
        if huruf.isalpha():
            x = ord(huruf.lower()) - 97
            y = (a * x + b) % 26
            hasil += chr(y + 97)
        else:
            hasil += huruf
    return hasil

# Fungsi dekripsi
def decrypt(text, a, b):
    a_inv = mod_inverse(a)
    if a_inv is None:
        return "Tidak ada invers dari a untuk modulo 26."
    hasil = ""
    for huruf in text:
        if huruf.isalpha():
            y = ord(huruf.lower()) - 97
            x = (a_inv * (y - b)) % 26
            hasil += chr(x + 97)
        else:
            hasil += huruf
    return hasil

# Streamlit interface
st.title("Affine Cipher: Enkripsi & Dekripsi")

mode = st.radio("Pilih Mode:", ("Enkripsi", "Dekripsi"))
text = st.text_input("Masukkan teks:")
a = st.number_input("Nilai a:", min_value=1, max_value=25, step=1)
b = st.number_input("Nilai b:", min_value=0, max_value=25, step=1)

# Validasi nilai a harus coprime dengan 26
import math
if math.gcd(a, 26) != 1:
    st.warning("Nilai 'a' harus relatif prima terhadap 26 agar cipher bekerja dengan benar.")
else:
    if st.button("Proses"):
        if mode == "Enkripsi":
            st.success("Hasil Enkripsi:")
            st.code(encrypt(text, a, b))
        else:
            st.success("Hasil Dekripsi:")
            st.code(decrypt(text, a, b))
