import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Telegram bot bilgileri
TELEGRAM_BOT_TOKEN = "7528502742:AAGghlsMdiNfZYV0LNG4Q70WtULL1VF03Z4"
TELEGRAM_CHAT_ID = "-4501107923"  # Buraya doğru chat ID'yi yapıştır

# Gönderilmiş ürünlerin takibi
sent_products = set()
message_count = 0  # Gönderilen mesaj sayısını takip et

# Ürün bilgilerini alacak fonksiyon
def get_product_info(soup):
    products = []
    product_cards = soup.find_all('li', class_='column')

    if not product_cards:
        print("No product cards found!")
        return products

    for card in product_cards:
        try:
            product_name = card.find('h3', class_='productName').text.strip()  # Ürün adı
        except AttributeError:
            print("Product name not found for a product card.")
            product_name = "No name available"

        try:
            new_price = card.find('span', class_='newPrice').text.strip()  # Yeni fiyat
            old_price = card.find('span', class_='oldPrice').text.strip()  # Eski fiyat
            price = f"{new_price} (Eski Fiyat: {old_price})"
        except AttributeError:
            print("Price not found for a product card.")
            price = "No price available"

        image_tag = card.find('img', class_='lazy cardImage')
        image_url = image_tag['data-original'] if image_tag else "No image available"

        product_link = card.find('a', class_='plink')
        if product_link:
            product_url = product_link['href']
        else:
            product_url = "No URL available"

        products.append({
            'name': product_name,
            'price': price,
            'image_url': image_url,
            'url': product_url
        })
    
    return products

# Sayfayı Selenium ile çekme
def fetch_with_selenium(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    page_source = driver.page_source
    driver.quit()
    return BeautifulSoup(page_source, 'html.parser')

# Telegram grubuna mesaj gönderme fonksiyonu
def send_telegram_message(message):
    global message_count
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"  # HTML formatında mesaj göndermek için
    }
    response = requests.post(url, data=data)
    
    # Rate limit kontrolü
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 10))  # Retry-After süresini al
        print(f"Rate limit reached. Retrying after {retry_after} seconds.")
        time.sleep(retry_after)
    elif response.status_code == 200:
        message_count += 1  # Başarıyla gönderilen mesajları takip et
        print(f"Message sent successfully. Total messages: {message_count}")

        if message_count % 10 == 0:
            # Her 10 mesajdan sonra 10 saniye bekle
            print("Waiting 10 seconds to avoid rate limit...")
            time.sleep(10)

    return response

# Ana fonksiyon
def main():
    global message_count
    url = "https://www.n11.com/super-firsatlar"  # Hedef URL
    
    # Tarayıcı işlemi tekrar başlatmak için döngü başlat
    for i in range(5):  # 5 defa sayfa yenileme işlemi yapılacak
        soup = fetch_with_selenium(url)
        product_info = get_product_info(soup)
        
        if not product_info:
            print("No product information found.")
        else:
            for product in product_info:
                # Eğer ürün URL'si daha önce gönderilmişse atla
                if product['url'] in sent_products:
                    print(f"Product already sent: {product['name']}")
                    continue
                
                # Ürün mesajı hazırlama
                message = (
                    f"<b>Product Name:</b> {product['name']}\n"
                    f"<b>Price:</b> {product['price']}\n"
                    f"<b>Image URL:</b> {product['image_url']}\n"
                    f"<b>Product URL:</b> <a href='{product['url']}'>Link</a>\n"
                    "---------------------------"
                )

                # Telegram'a gönder ve başarı durumunu kontrol et
                response = send_telegram_message(message)
                if response.status_code == 200:
                    # Ürün URL'sini gönderilenler listesine ekle
                    sent_products.add(product['url'])

                # İstekler arasında 1 saniye bekleme
                time.sleep(1)

        # Tarayıcıyı her defasında tekrar başlatmak için 5 saniye bekleme
        print(f"Restarting browser after iteration {i+1}...")
        time.sleep(5)

# Programı çalıştır
if __name__ == "__main__":
    main()
