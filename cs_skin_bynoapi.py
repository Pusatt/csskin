import requests
import time
from plyer import notification
from datetime import datetime

### Kullanıcı ayarları
min_discount = 25           # Minimum indirim oranı
min_price = 50              # Minimum fiyat (sadece indirim oranı için)
min_floatprice = 0          # Minimum fiyat (sadece float değeri için)
max_price = 500             # Maksimum fiyat (hem float hem indirim için)
max_float = 0.005            # Maksimum float değeri (float filtresini kapatmak için 0.00)

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
            
            if ((min_price <= product_price <= max_price and (discount_percentage >= min_discount) and product_name not in seen_products)
            or (min_floatprice <= product_price <= max_price and -1 < float_value < max_float
            and product_name not in seen_products)):
                seen_products.add(product_name)  # Ürünü kaydet
                
                # Şu anki zamanı al
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Bildirim gönder
                notification.notify(
                    title="Yeni Ürün Bulundu!\n",
                    message=f"{product_name}\nFloat: {float_value}\nFiyat: {product_price:.2f}TL\n%{discount_percentage} indirim\n")
                
                # Konsola yazdır (isim, indirim, fiyat, float değeri ve saat bilgisi)
                print(f"{current_time} - {product_name}\nFloat: {float_value}\nFiyat: {product_price:.2f}TL\n%{discount_percentage} indirim\n")
    
    except Exception as e:
        print(f"Bir hata oluştu: {e}")

# Program döngüsü: 10 saniyede bir sayfayı kontrol et
while True:
    check_for_new_products()
    time.sleep(10)  # 10 saniye bekle ve tekrar kontrol et
