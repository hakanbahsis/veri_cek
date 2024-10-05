from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Ürün bilgilerini alacak fonksiyon
def get_product_info(soup):
    products = []
    product_cards = soup.find_all('li', class_='column')  # Ürün kartı için sınıf

    if not product_cards:
        print("No product cards found!")
        return products

    for card in product_cards:
        try:
            product_name = card.find('h3', class_='productName').text.strip()  # Ürün adı
        except AttributeError:
            print("Product name not found for a product card.")
            product_name = "No name available"

        # Fiyat bilgisini alma
        try:
            new_price = card.find('span', class_='newPrice').text.strip()  # Yeni fiyat
            old_price = card.find('span', class_='oldPrice').text.strip()  # Eski fiyat
            price = f"{new_price} (Eski Fiyat: {old_price})"
        except AttributeError:
            print("Price not found for a product card.")
            price = "No price available"

        # Resim URL'sini alma
        image_tag = card.find('img', class_='lazy cardImage')
        image_url = image_tag['data-original'] if image_tag else "No image available"  # Resim URL'si

        # Ürün URL'sini alma
        product_link = card.find('a', class_='plink')
        if product_link:
            product_url = product_link['href']
        else:
            product_url = "No URL available"

        products.append({
            'name': product_name,
            'price': price,
            'image_url': image_url,
            'url': product_url  # Ürün URL'sini ekledik
        })
    
    return products

# Sayfayı Selenium ile çekme
def fetch_with_selenium(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)

    # Sayfanın tam yüklenmesi için bekle
    time.sleep(5)

    # Daha fazla öğe yüklemek için sayfayı kaydır (opsiyonel, daha fazla ürün için)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)  # Yüklemenin tamamlanması için bekle

    page_source = driver.page_source
    driver.quit()
    
    return BeautifulSoup(page_source, 'html.parser')

# Ana fonksiyon
def main():
    url = "https://www.n11.com/super-firsatlar"  # Hedef URL

    # Sayfayı Selenium ile al
    soup = fetch_with_selenium(url)

    # Ürün bilgilerini al ve yazdır
    product_info = get_product_info(soup)
    
    if not product_info:
        print("No product information found.")
    else:
        for product in product_info:
            print(f"Product Name: {product['name']}")
            print(f"Price: {product['price']}")
            print(f"Image URL: {product['image_url']}")
            print(f"Product URL: {product['url']}")  # Ürün URL'sini yazdır
            print("-" * 40)

# Programı çalıştır
if __name__ == "__main__":
    main()
