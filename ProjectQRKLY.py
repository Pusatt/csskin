import requests
import time
from plyer import notification
from datetime import datetime

### Kullanıcı ayarları
min_discount = 25           # Minimum indirim oranı
min_price = 50              # Minimum fiyat (sadece indirim oranı için)
min_otherprice = 0          # Minimum fiyat (diğer filtreler için)
max_price = 1000            # Maksimum fiyat (tüm filtreler için)
max_float = 0.005           # Maksimum float değeri (float filtresini kapatmak için 0.00)

# Daha önce görülen ürünlerin listesi
seen_products_discount = set()
seen_products_float = set()
seen_products_stickers = set()

# Yeni ürünleri kontrol eden fonksiyon
def check_for_new_discount_products(products):
    for product in products:
        product_name = product.get('name', 'Bilinmeyen Ürün')
        discount_percentage = product.get('discountRate', 0)
        product_price = product.get('price', 0)
        float_value = float(product.get('info', {}).get('float', 1))
        product_ID = product.get('listingNo', 'ID Numarası')

        if min_price <= product_price <= max_price and discount_percentage >= min_discount and product_ID not in seen_products_discount:
            seen_products_discount.add(product_ID)
            current_time = datetime.now().strftime("%H:%M:%S")
            
            notification.notify(
                title=f"İndirimli Ürün!",
                message=f"{product_name}\nFloat: {float_value}\nFiyat: {product_price:.2f}TL\n%{discount_percentage} indirim\n"
            )
            
            print(f"{current_time} - Indirim \n{product_name}\nFloat: {float_value}\nFiyat: {product_price:.2f}TL\n%{discount_percentage} indirim\n")

def check_for_new_float_products(products):
    for product in products:
        product_name = product.get('name', 'Bilinmeyen Ürün')
        discount_percentage = product.get('discountRate', 0)
        product_price = product.get('price', 0)
        float_value = float(product.get('info', {}).get('float', 1))
        product_ID = product.get('listingNo', 'ID Numarası')

        if min_otherprice <= product_price <= max_price and -1 < float_value < max_float and product_ID not in seen_products_float:
            seen_products_float.add(product_ID)
            current_time = datetime.now().strftime("%H:%M:%S")
            
            notification.notify(
                title=f"Float Değeri Düşük Ürün!",
                message=f"{product_name}\nFloat: {float_value}\nFiyat: {product_price:.2f}TL\n%{discount_percentage} indirim\n"
            )
            
            print(f"{current_time} - Float \n{product_name}\nFloat: {float_value}\nFiyat: {product_price:.2f}TL\n%{discount_percentage} indirim\n")

def check_for_sticker_products(products):
    for product in products:
        product_name = product.get('name', 'Bilinmeyen Ürün')
        discount_percentage = product.get('discountRate', 0)
        product_price = product.get('price', 0)
        product_ID = product.get('listingNo', 'ID Numarası')

        # Sticker isimlerini al ve "Sticker | " kısmını kaldır
        stickers = product.get('info', {}).get('stickerNames', 'Sticker Yok')
        if stickers != 'Sticker Yok':
            stickers = stickers.replace("Sticker | ", "")

        # "souvenir" içermeyen ürün isimleri ve değerli sticker kriterini sağlayanlar
        if ('2014' in stickers or '2015' in stickers) and product_ID not in seen_products_stickers and 'souvenir' not in product_name.lower():
            if min_otherprice <= product_price <= max_price:
                seen_products_stickers.add(product_ID)
                current_time = datetime.now().strftime("%H:%M:%S")
                
                notification.notify(
                    title=f"Değerli Stickeri Olan Ürün!",
                    message=f"{product_name}\nStickerlar: {stickers}\nFiyat: {product_price:.2f}TL\n%{discount_percentage} indirim\n"
                )
                
                print(f"{current_time} - Sticker \n{product_name}\nStickerlar: {stickers}\nFiyat: {product_price:.2f}TL\n%{discount_percentage} indirim\n")

# Program döngüsü: 10 saniyede bir sayfayı kontrol et
while True:
    try:
        url = "https://listing.bynogame.net/api/listings/cs2?page=0&limit=1000"
        response = requests.get(url)
        data = response.json()
        
        products = data.get('payload', [])
        
        check_for_new_discount_products(products)
        check_for_new_float_products(products)
        check_for_sticker_products(products)

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        
    time.sleep(10)

# mrb ben Pusat