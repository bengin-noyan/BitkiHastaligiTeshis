# -*- coding: utf-8 -*-
"""
Bir kullanıcının şifresini belirlemek / sıfırlamak için küçük yardımcı.

Şifreler artık hash'li tutulduğu için veritabanına elle INSERT atmak işe
yaramıyor, hash'i bu script üretiyor.

kullanım:
    python sifre_ayarla.py admin          # şifreyi sorar, ekrana yazmaz
    python sifre_ayarla.py yeni_kullanici # kullanıcı yoksa oluşturur

Şifreyi komut satırında argüman olarak VERMIYORUZ, çünkü kabuk geçmişine
(PowerShell/bash history) düşüyor.
"""

import getpass
import os
import sqlite3
import sys
from datetime import datetime

from guvenlik import sifre_hashle

DB_YOLU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tarimsal_analiz.db")


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    kullanici_adi = sys.argv[1].strip().lower()
    if not kullanici_adi:
        print("Kullanici adi bos olamaz.")
        return 2

    sifre = getpass.getpass(f"'{kullanici_adi}' icin yeni sifre: ")
    if len(sifre) < 8:
        print("Sifre en az 8 karakter olmali.")
        return 1
    if sifre != getpass.getpass("Sifreyi tekrar girin: "):
        print("Sifreler uyusmuyor.")
        return 1

    conn = sqlite3.connect(DB_YOLU)
    imlec = conn.cursor()

    # tablo henüz yoksa (uygulama hiç açılmamışsa) burada da oluşturuyoruz
    imlec.execute(
        """
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT UNIQUE,
            sifre TEXT,
            kayit_tarihi TEXT
        )
        """
    )

    hash_degeri = sifre_hashle(sifre)
    imlec.execute(
        "SELECT id FROM kullanicilar WHERE kullanici_adi=?", (kullanici_adi,)
    )
    if imlec.fetchone():
        imlec.execute(
            "UPDATE kullanicilar SET sifre=? WHERE kullanici_adi=?",
            (hash_degeri, kullanici_adi),
        )
        print(f"'{kullanici_adi}' kullanicisinin sifresi guncellendi.")
    else:
        imlec.execute(
            "INSERT INTO kullanicilar (kullanici_adi, sifre, kayit_tarihi) "
            "VALUES (?, ?, ?)",
            (kullanici_adi, hash_degeri, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        print(f"'{kullanici_adi}' kullanicisi olusturuldu.")

    conn.commit()
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
