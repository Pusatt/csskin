import requests
import time
from plyer import notification
from datetime import datetime

### Kullanıcı ayarları
min_discount = 25           # Minimum indirim oranı
min_price = 50              # Minimum fiyat (sadece indirim oranı için)
min_floatprice = 0          # Minimum fiyat (sadece float değeri için)
max_price = 1000            # Maksimum fiyat (hem float hem indirim için)
max_float = 0.005           # Maksimum float değeri (float filtresini kapatmak için 0.00)

# Daha önce görülen ürünlerin listesi
seen_products = set()

# Yeni ürünleri kontrol eden fonksiyon
def check_for_new_products():
    url = "https://listing.bynogame.net/api/listings/cs2?page=0&limit=1000"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # "payload" altında ürün verilerini al
        products = data.get('payload', [])

        # Her ürünü kontrol et
        for product in products:
            product_name = product.get('name', 'Bilinmeyen Ürün')
            discount_percentage = product.get('discountRate', 0)
            product_price = product.get('price', 0)  # Fiyatı TL olarak almak için
            float_value = float(product.get('info', {}).get('float', 1))  # Float değeri varsayılan olarak 1
            product_ID = product.get('listingNo', 'ID Numarası')
            
            # Sticker isimlerini alıp "Sticker | " kısmını kaldırın
            stickers = product.get('info', {}).get('stickerNames', 'Sticker Yok')
            if stickers != 'Sticker Yok':
                stickers = stickers.replace("Sticker | ", "")

            # Float değeri 0'ın altındaysa "Float bilgisi yok" olarak göster
            float_text = f"Float: {float_value}" if float_value >= 0 else "Float bilgisi yok"

            if ((min_price <= product_price <= max_price and discount_percentage >= min_discount and product_ID not in seen_products)
            or (min_floatprice <= product_price <= max_price and -1 < float_value < max_float and product_ID not in seen_products)):
                seen_products.add(product_ID)  # Ürünü kaydet
                # Şu anki zamanı al
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Bildirim gönder
                notification.notify(
                    # Mesaj başlığını aktif hale getirmek için alt satırı kullanın
                    # title="Yeni Ürün Bulundu!",
                    message=f"{product_name}\n{stickers}\n{float_text}\nFiyat: {product_price:.2f}TL\n%{discount_percentage} indirim\n"
                )
                
                # Konsola yazdır (isim, indirim, fiyat, float değeri ve saat bilgisi)
                print(f"{current_time} - {product_name}\n{stickers}\n{float_text}\nFiyat: {product_price:.2f}TL\n%{discount_percentage} indirim\n")
    
    except Exception as e:
        print(f"Bir hata oluştu: {e}")

# Program döngüsü: 10 saniyede bir sayfayı kontrol et
while True:
    check_for_new_products()
    time.sleep(10)  # 10 saniye bekle ve tekrar kontrol et
