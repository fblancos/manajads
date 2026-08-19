import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AdSense & Ads Tracker", layout="wide")

# 1. Inisialisasi Database Sementara
if 'accounts' not in st.session_state:
    st.session_state.accounts = {}

# Fungsi untuk menghitung metrik turunan
def calculate_metrics(df):
    df_calc = df.copy()
    # Pastikan data numerik
    cols_to_numeric = ["FB Spent", "Tagihan FB", "Hasil Adsense", "Jumlah Trafik"]
    for col in cols_to_numeric:
        df_calc[col] = pd.to_numeric(df_calc[col], errors='coerce').fillna(0)
    
    # Kalkulasi dengan penghindaran error pembagian nol (Division by Zero)
    df_calc["ROI (FB Spent) %"] = np.where(df_calc["FB Spent"] > 0, ((df_calc["Hasil Adsense"] - df_calc["FB Spent"]) / df_calc["FB Spent"]) * 100, 0)
    df_calc["ROI (Tagihan FB) %"] = np.where(df_calc["Tagihan FB"] > 0, ((df_calc["Hasil Adsense"] - df_calc["Tagihan FB"]) / df_calc["Tagihan FB"]) * 100, 0)
    df_calc["CPC (Rp)"] = np.where(df_calc["Jumlah Trafik"] > 0, df_calc["FB Spent"] / df_calc["Jumlah Trafik"], 0)
    
    return df_calc

# 2. Sidebar: Pembuatan Akun Baru (Custom Name)
st.sidebar.header("⚙️ Manajemen Akun")
new_acc_name = st.sidebar.text_input("Buat Tabel Akun Baru:")
if st.sidebar.button("Tambah Akun"):
    if new_acc_name and new_acc_name not in st.session_state.accounts:
        # Buat tabel kosong dengan struktur standar
        empty_df = pd.DataFrame(columns=["Tanggal", "FB Spent", "Tagihan FB", "Hasil Adsense", "Jumlah Trafik"])
        st.session_state.accounts[new_acc_name] = empty_df
        st.sidebar.success(f"Akun '{new_acc_name}' berhasil dibuat!")
    elif new_acc_name in st.session_state.accounts:
        st.sidebar.warning("Nama akun sudah ada.")

st.sidebar.markdown("---")

# 3. Sidebar: Navigasi
menu_options = ["📊 MASTER SUMMARY"] + list(st.session_state.accounts.keys())
selected_menu = st.sidebar.radio("Navigasi Halaman:", menu_options)

# 4. Halaman: Master Summary (Terhubung Otomatis)
if selected_menu == "📊 MASTER SUMMARY":
    st.title("📊 Master Summary Global")
    
    if not st.session_state.accounts:
        st.info("Belum ada akun. Silakan buat akun baru di menu samping.")
    else:
        master_data = []
        
        for acc_name, df in st.session_state.accounts.items():
            if not df.empty:
                df_num = df[["FB Spent", "Tagihan FB", "Hasil Adsense", "Jumlah Trafik"]].apply(pd.to_numeric, errors='coerce').fillna(0)
                total_spent = df_num["FB Spent"].sum()
                total_tagihan = df_num["Tagihan FB"].sum()
                total_adsense = df_num["Hasil Adsense"].sum()
                total_trafik = df_num["Jumlah Trafik"].sum()
                
                master_data.append({
                    "Nama Akun": acc_name,
                    "Total FB Spent": total_spent,
                    "Total Tagihan FB": total_tagihan,
                    "Total Adsense": total_adsense,
                    "Total Trafik": total_trafik
                })
        
        if master_data:
            master_df = pd.DataFrame(master_data)
            
            # Kalkulasi Global Berdasarkan Akumulasi Total
            master_df["Global ROI (FB Spent) %"] = np.where(master_df["Total FB Spent"] > 0, ((master_df["Total Adsense"] - master_df["Total FB Spent"]) / master_df["Total FB Spent"]) * 100, 0)
            master_df["Global ROI (Tagihan) %"] = np.where(master_df["Total Tagihan FB"] > 0, ((master_df["Total Adsense"] - master_df["Total Tagihan FB"]) / master_df["Total Tagihan FB"]) * 100, 0)
            master_df["Global CPC (Rp)"] = np.where(master_df["Total Trafik"] > 0, master_df["Total FB Spent"] / master_df["Total Trafik"], 0)
            
            # Formatting Tampilan
            st.dataframe(master_df.style.format({
                "Total FB Spent": "Rp {:,.0f}",
                "Total Tagihan FB": "Rp {:,.0f}",
                "Total Adsense": "Rp {:,.0f}",
                "Total Trafik": "{:,.0f}",
                "Global ROI (FB Spent) %": "{:.2f}%",
                "Global ROI (Tagihan) %": "{:.2f}%",
                "Global CPC (Rp)": "Rp {:,.0f}"
            }), use_container_width=True)
            
            # Grand Total Semua Akun
            st.subheader("Total Keseluruhan (Semua Akun)")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Adsense", f"Rp {master_df['Total Adsense'].sum():,.0f}")
            col2.metric("Total Spent", f"Rp {master_df['Total FB Spent'].sum():,.0f}")
            col3.metric("Total Profit Margin", f"Rp {(master_df['Total Adsense'].sum() - master_df['Total FB Spent'].sum()):,.0f}")
        else:
            st.info("Akun sudah dibuat, tetapi belum ada data yang diinput.")

# 5. Halaman: Input Data Per Akun
else:
    st.title(f"📝 Data Harian: {selected_menu}")
    st.write("Tambahkan baris baru dengan klik pada tabel di bawah ini.")
    
    current_df = st.session_state.accounts[selected_menu]
    
    # Editor Interaktif (Vibe Coding UI)
    edited_df = st.data_editor(
        current_df,
        num_rows="dynamic", # Memungkinkan user menambah baris baru
        use_container_width=True,
        key=f"editor_{selected_menu}"
    )
    
    # Simpan perubahan kembali ke session state
    st.session_state.accounts[selected_menu] = edited_df
    
    # Tampilkan preview metrik yang dihitung otomatis
    st.subheader("Preview Kalkulasi Otomatis")
    if not edited_df.empty:
        calculated_df = calculate_metrics(edited_df)
        st.dataframe(calculated_df.style.format({
            "FB Spent": "Rp {:,.0f}",
            "Tagihan FB": "Rp {:,.0f}",
            "Hasil Adsense": "Rp {:,.0f}",
            "ROI (FB Spent) %": "{:.2f}%",
            "ROI (Tagihan FB) %": "{:.2f}%",
            "CPC (Rp)": "Rp {:,.0f}"
        }), use_container_width=True)
