
#!/usr/bin/env python3
"""
Script untuk menjalankan scraper data perusahaan di Kabupaten Bekasi
"""

import asyncio
import sys
from bekasi_company_scraper import BekasiCompanyScraper

def main():
    print("🏢 MEMULAI SCRAPING DATA PERUSAHAAN BEKASI")
    print("=" * 60)
    print("Target Data:")
    print("✅ Nama Perusahaan")
    print("✅ Alamat Lengkap")
    print("✅ Email Kontak")
    print("✅ Nomor Telepon")
    print("✅ Nama HRD")
    print("=" * 60)
    
    try:
        # Jalankan scraper
        scraper = BekasiCompanyScraper()
        asyncio.run(scraper.run_scraper())
        
        print("\n🎉 SCRAPING SELESAI!")
        print("📁 Cek file hasil dengan nama: bekasi_companies_[timestamp].json")
        
    except KeyboardInterrupt:
        print("\n⏹️ Scraping dihentikan oleh user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
