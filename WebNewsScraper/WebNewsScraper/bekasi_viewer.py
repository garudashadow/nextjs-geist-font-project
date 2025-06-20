
#!/usr/bin/env python3
"""
Viewer untuk menampilkan hasil scraping data perusahaan Bekasi
dalam format yang mudah dibaca
"""

import json
import os
from datetime import datetime
from tabulate import tabulate

def find_latest_bekasi_file():
    """Cari file hasil scraping Bekasi terbaru"""
    files = [f for f in os.listdir('.') if f.startswith('bekasi_companies_') and f.endswith('.json')]
    if not files:
        return None
    
    # Urutkan berdasarkan timestamp dalam nama file
    files.sort(reverse=True)
    return files[0]

def load_and_display_data(filename):
    """Load dan tampilkan data dari file JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Ambil data companies dari struktur yang benar
        companies = data.get('companies', [])
        
        print("🏢" + "="*80)
        print("📊 HASIL SCRAPING DATA PERUSAHAAN KABUPATEN BEKASI")
        print("="*82)
        
        # Tampilkan info file
        print(f"📁 File: {filename}")
        print(f"📅 Total Perusahaan: {len(companies)}")
        print(f"⏰ Waktu Scraping: {datetime.now().strftime('%d %B %Y, %H:%M:%S')}")
        print("="*82)
        
        # Siapkan data untuk tabel
        table_data = []
        
        for i, company in enumerate(companies, 1):
            # Format alamat (maksimal 50 karakter)
            alamat = company.get('address', 'N/A')
            if len(alamat) > 50:
                alamat = alamat[:47] + "..."
            
            # Format email (gabungkan list jadi string)
            emails = company.get('emails', [])
            if isinstance(emails, list):
                email = ', '.join(emails[:2])  # Ambil maksimal 2 email
            else:
                email = str(emails) if emails else 'N/A'
            
            if len(email) > 35:
                email = email[:32] + "..."
            
            # Format telepon (gabungkan list jadi string)
            phones = company.get('phones', [])
            if isinstance(phones, list):
                telepon = ', '.join(phones[:2])  # Ambil maksimal 2 nomor
            else:
                telepon = str(phones) if phones else 'N/A'
            
            # Format HRD
            hrd = company.get('hrd_name', 'N/A')
            if len(hrd) > 25:
                hrd = hrd[:22] + "..."
            
            table_data.append([
                i,
                company.get('company_name', 'N/A'),
                alamat,
                email,
                telepon,
                hrd
            ])
        
        # Tampilkan tabel
        headers = ['No', 'Nama Perusahaan', 'Alamat', 'Email', 'Telepon', 'HRD']
        
        print("\n📋 DAFTAR PERUSAHAAN:")
        print(tabulate(table_data, headers=headers, tablefmt='grid', maxcolwidths=[3, 25, 50, 35, 15, 25]))
        
        # Tampilkan detail lengkap untuk 3 perusahaan pertama
        print("\n" + "="*82)
        print("📋 DETAIL 3 PERUSAHAAN PERTAMA:")
        print("="*82)
        
        for i, company in enumerate(companies[:3], 1):
            print(f"\n{i}. {company.get('company_name', 'N/A')}")
            print(f"   📍 Alamat: {company.get('address', 'N/A')}")
            
            # Tampilkan email
            emails = company.get('emails', [])
            if isinstance(emails, list) and emails:
                print(f"   📧 Email: {', '.join(emails)}")
            else:
                print(f"   📧 Email: N/A")
            
            # Tampilkan telepon
            phones = company.get('phones', [])
            if isinstance(phones, list) and phones:
                print(f"   📞 Telepon: {', '.join(phones)}")
            else:
                print(f"   📞 Telepon: N/A")
            
            print(f"   👤 HRD: {company.get('hrd_name', 'N/A')}")
            
            # Tampilkan industri jika ada
            if company.get('industry'):
                print(f"   🏭 Industri: {company.get('industry')}")
            
            print("-" * 80)
        
        # Tampilkan statistik
        print("\n📊 STATISTIK:")
        
        companies_with_email = len([c for c in companies if c.get('emails') and (
            (isinstance(c.get('emails'), list) and len(c.get('emails')) > 0) or
            (isinstance(c.get('emails'), str) and c.get('emails') != 'N/A')
        )])
        
        companies_with_phone = len([c for c in companies if c.get('phones') and (
            (isinstance(c.get('phones'), list) and len(c.get('phones')) > 0) or
            (isinstance(c.get('phones'), str) and c.get('phones') != 'N/A')
        )])
        
        companies_with_hrd = len([c for c in companies if c.get('hrd_name') and c.get('hrd_name') != 'N/A'])
        
        print(f"✅ Perusahaan dengan Email: {companies_with_email}")
        print(f"✅ Perusahaan dengan Telepon: {companies_with_phone}")
        print(f"✅ Perusahaan dengan Info HRD: {companies_with_hrd}")
        
        print("\n🎉 Tampilan selesai!")
        
    except Exception as e:
        print(f"❌ Error membaca file: {str(e)}")

def main():
    print("🔍 Mencari file hasil scraping...")
    
    # Cari file terbaru
    latest_file = find_latest_bekasi_file()
    
    if not latest_file:
        print("❌ Tidak ditemukan file hasil scraping.")
        print("💡 Pastikan Anda sudah menjalankan scraper terlebih dahulu.")
        return
    
    print(f"📁 File ditemukan: {latest_file}")
    
    # Tampilkan data
    load_and_display_data(latest_file)

if __name__ == "__main__":
    main()
