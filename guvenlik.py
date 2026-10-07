# -*- coding: utf-8 -*-
"""
Şifre hash'leme ve doğrulama.

app.py ile api_server.py aynı veritabanını kullandığı için bu iş tek yerde
duruyor. İki tarafta ayrı kopya tutsak biri güncellenip diğeri unutulur.

Hash formatı tek bir TEXT alanına sığıyor, tablo şeması değişmiyor:

    pbkdf2_sha256$<iterasyon>$<tuz_base64>$<hash_base64>
"""

import base64
import hashlib
import hmac
import os
import secrets

# .env varsa oradan da okusun. python-dotenv kurulu değilse sessizce geçiyor,
# o zaman sadece gerçek ortam değişkenleri geçerli olur.
try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except Exception:
    pass

ALGO = "pbkdf2_sha256"
# OWASP'ın PBKDF2-SHA256 için önerdiği alt sınır. Bu makinede ~130 ms sürüyor,
# girişte hissedilmiyor ama kaba kuvvet denemesini pahalı hale getiriyor.
ITERASYON = 600_000
TUZ_UZUNLUK = 16


def _b64(veri: bytes) -> str:
    return base64.b64encode(veri).decode("ascii")


def _b64_coz(metin: str) -> bytes:
    return base64.b64decode(metin.encode("ascii"))


def sifre_hashle(sifre: str, iterasyon: int = ITERASYON) -> str:
    """Düz metin şifreyi saklanabilir hash string'ine çeviriyor.

    Her çağrıda yeni tuz üretiliyor, yani aynı şifreyi kullanan iki kullanıcının
    kaydı birbirine benzemiyor. Hazır tablo (rainbow table) saldırısı bu yüzden
    işe yaramıyor.
    """
    if not isinstance(sifre, str) or not sifre:
        raise ValueError("Bos sifre hash'lenemez")
    tuz = secrets.token_bytes(TUZ_UZUNLUK)
    ham = hashlib.pbkdf2_hmac("sha256", sifre.encode("utf-8"), tuz, iterasyon)
    return f"{ALGO}${iterasyon}${_b64(tuz)}${_b64(ham)}"


def hash_mi(kayitli: str) -> bool:
    """Veritabanındaki değer hash mi, yoksa eski düz metin mi?"""
    return isinstance(kayitli, str) and kayitli.startswith(ALGO + "$")


def sifre_dogrula(sifre: str, kayitli: str) -> bool:
    """Girilen şifre veritabanındaki kayda uyuyor mu?

    Eski düz metin kayıtlar için de çalışıyor. Veritabanı kurulumunda hepsi
    hash'e çevriliyor ama elle eklenmiş bir satır kalırsa kullanıcı kapıda
    kalmasın diye bu yol açık bırakıldı.
    """
    if not isinstance(sifre, str) or not isinstance(kayitli, str) or not kayitli:
        return False

    if not hash_mi(kayitli):
        # düz metin karşılaştırması. == yerine compare_digest kullanıyorum,
        # yoksa cevap süresinden şifrenin kaç harfi tuttuğu anlaşılabiliyor.
        return hmac.compare_digest(sifre.encode("utf-8"), kayitli.encode("utf-8"))

    try:
        _, iterasyon, tuz_b64, hash_b64 = kayitli.split("$")
        ham = hashlib.pbkdf2_hmac(
            "sha256", sifre.encode("utf-8"), _b64_coz(tuz_b64), int(iterasyon)
        )
        return hmac.compare_digest(ham, _b64_coz(hash_b64))
    except Exception:
        # kayıt bozuksa girişi reddediyoruz, hata fırlatıp sayfayı patlatmıyoruz
        return False


def yukseltme_gerekli_mi(kayitli: str) -> bool:
    """Kayıt düz metin mi ya da bugünkü iterasyon sayısından düşük mü?

    Giriş başarılı olduğunda elimizde düz metin şifre var, o anda kaydı
    yeni formata yükseltebiliyoruz. Kullanıcı bir şey yapmıyor.
    """
    if not hash_mi(kayitli):
        return True
    try:
        return int(kayitli.split("$")[1]) < ITERASYON
    except Exception:
        return True


def admin_sifresi_al() -> str:
    """Varsayılan admin hesabının şifresini ortam değişkeninden okuyor.

    Boş dönerse çağıran taraf admin hesabını hiç oluşturmuyor. Şifreyi koda
    sabit yazmak depo public olduğu için sorun çıkarıyordu.
    """
    return (os.environ.get("ADMIN_PASSWORD") or "").strip()


def duz_metin_sifreleri_hashle(conn) -> int:
    """Tabloda düz metin kalmış şifreleri hash'e çeviriyor, kaç satır
    güncellendiğini döndürüyor.

    Elimizde düz metin olduğu için doğrudan hash'leyebiliyoruz, kullanıcıdan
    şifre sormaya gerek yok. Uygulama her açılışta bunu çağırıyor, bir kere
    çevrildikten sonra eşleşen satır kalmadığı için maliyeti sıfır.
    """
    imlec = conn.cursor()
    imlec.execute("SELECT id, sifre FROM kullanicilar")
    cevrilecek = [
        (satir_id, deger)
        for satir_id, deger in imlec.fetchall()
        if deger and not hash_mi(deger)
    ]
    for satir_id, duz in cevrilecek:
        imlec.execute(
            "UPDATE kullanicilar SET sifre=? WHERE id=?", (sifre_hashle(duz), satir_id)
        )
    if cevrilecek:
        conn.commit()
    return len(cevrilecek)
