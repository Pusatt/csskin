import requests
import time
from urllib.parse import quote
from plyer import notification
from datetime import datetime

### Kullanıcı ayarları
min_discount = 25           # Minimum indirim oranı
min_price = 50              # Minimum fiyat (sadece indirim oranı için)
min_otherprice = 0          # Minimum fiyat (diğer filtreler için)
max_price = 1000            # Maksimum fiyat (tüm filtreler için)
max_float = 0.010           # Maksimum float değeri (float filtresini kapatmak için 0.00)
min_sticker = 500           # Sticker toplam değeri bildirim eşiği
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

# Sticker fiyatını almak için fonksiyon
def fetch_sticker_price(sticker_name):
    # Sticker adını URL dostu hale getir
    encoded_name = quote(sticker_name)
    
    # Sticker fiyatı için URL
    urll = f"https://gw.bynogame.com/steam-products/v2/products?page=1&limit=36&sort=SalesCountLastSevenDays:-1&filters=Category:Sticker;Keywords:{encoded_name};AppId:730"
    #print(f"Sticker fiyatı çekiliyor: {urll}")  # Kontrol için URL'i yazdırın
    
    try:
        # URL'e istek gönder
        response = requests.get(urll)
        response.raise_for_status()  # Hatalı istekleri yakala
        dataa = response.json()
        
        if "data" in dataa and "result" in dataa["data"] and len(dataa["data"]["result"]) > 0:
            priceTRY = dataa["data"]["result"][0].get("priceTRY", 0)
            #print(f"Sticker fiyatı: {priceTRY} TL")  # Kontrol için fiyatı yazdırın
            return priceTRY
        else: 
            return 0  # Fiyat bulunamazsa 0 döndür

    except Exception as e:
        print(f"Sticker fiyatını çekerken hata oluştu: {e}")
        return 0  # Fiyat bulunamazsa 0 döndür

# Stickerları değerlendirip toplam fiyatı kontrol eden fonksiyon
def check_for_valuable_sticker_products(products):
    for product in products:
        product_name = product.get('name', 'Bilinmeyen Ürün')
        product_price = product.get('price', 0)
        discount_percentage = product.get('discountRate', 0)
        product_ID = product.get('listingNo', 'ID Numarası')

        # Sticker isimlerini al ve "Sticker | " kısmını kaldır
        stickers = product.get('info', {}).get('stickerNames', 'Sticker Yok')
        if stickers != 'Sticker Yok':
            sticker_list = stickers.split(', Sticker | ')  # Her sticker'ı ayır

            # Her sticker'ın fiyatını topla
            total_sticker_value = 0
            for sticker in sticker_list:
                sticker_price = fetch_sticker_price(sticker.strip())
                total_sticker_value += sticker_price
            
            # Eğer toplam fiyat belirlenen fiyatı aşıyorsa bildir
            if total_sticker_value >= min_sticker and product_ID not in seen_products_stickers and min_otherprice <= product_price <= max_price and 'souvenir' not in product_name.lower():
                seen_products_stickers.add(product_ID)
                current_time = datetime.now().strftime("%H:%M:%S")
                
                sticker_price_text = f"{total_sticker_value:.2f} TL"
                
                notification.notify(
                    title="Değerli Stickeri Olan Ürün!",
                    message=f"{product_name}\nToplam: {sticker_price_text} / {sticker_list}\nFiyat: {product_price:.2f}TL\n%{discount_percentage} indirim\n"
                )
                
                print(f"{current_time} - Sticker \n{product_name}\nToplam Sticker Degeri: {sticker_price_text}\n{sticker_list}\nFiyat: {product_price:.2f}TL\n%{discount_percentage} indirim\n")


# Program döngüsü: 10 saniyede bir sayfayı kontrol et
while True:
    try:
        url = "https://listing.bynogame.net/api/listings/cs2?page=0&limit=1000"
        response = requests.get(url)
        data = response.json()
        
        products = data.get('payload', [])
        
        check_for_new_discount_products(products)
        check_for_new_float_products(products)
        check_for_valuable_sticker_products(products)

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        
    time.sleep(10)

# Katkılarından dolayı Salih'e teşekkürler..
#                                  -Pusat