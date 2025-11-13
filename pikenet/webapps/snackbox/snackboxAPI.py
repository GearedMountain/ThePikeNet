import subprocess
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import os

BASE_URL = "https://www.universalyums.com/"
OUTPUT_DIR = "pikenet/webapps/snackbox/dynamic"

def fetchHtmlWithCurl(url):
    try:
        result = subprocess.run(
            ['curl', '-sL', url],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Curl failed:", e.stderr)
        return None

def sanitizeFilename(name):
    name = name.strip().lower()
    name = re.sub(r'\s*image\s*$', '', name)
    name = re.sub(r"[^\w\-_.']+", '_', name)
    name = name.replace("'", "")
    return name

def getCurrentCountry():
    currentCountry = os.environ.get("CURRENT_COUNTRY")
    if not currentCountry or currentCountry == "Unkown Country":
        print("Country hasnt been set or is unkown")
        html = fetchHtmlWithCurl(BASE_URL)
        soup = BeautifulSoup(html, 'html.parser')

        recent_boxes_div = soup.find('section', class_='recent-boxes')
        if not recent_boxes_div:
            print("Could not find div with class 'recent-boxes'")
            result = "Unknown Country"
        else:
            mostRecent = recent_boxes_div.find('div', class_="item")
            h4 = mostRecent.find('h4')
            if not h4:
                print("couldnt find country h4")
                result = "Unknown Country"
            else:
                result = ''.join(h4.find_all(text=True, recursive=False)).strip()
        os.environ["CURRENT_COUNTRY"] = result
        if result == "Unknown Country":
            print("Couldnt find the country name after attempt")
        return result
    else:
        return currentCountry


def parseSnacksAndCountry(html):
    soup = BeautifulSoup(html, 'html.parser')
    container_div = soup.find('div', class_='slider-wrap')
    if not container_div:
        print("Could not find div with class 'slider-wrap'")
        return None, []

    parent_div = container_div.parent
    if not parent_div:
        print("Could not find parent container of slider-wrap")
        return None, []
    
    country = getCurrentCountry()
             
    snacks = []
    for img in container_div.find_all('img'):
        alt = img.get('alt', '').strip()
        src = img.get('src')
        if not src or len(alt) < 2:
            continue

        alt_lower = alt.lower()
        if any(x in alt_lower for x in ['logo', 'universal yums', 'facebook', 'instagram', 'box']):
            continue

        clean_name = re.sub(r'\s*image\s*$', '', alt, flags=re.I).strip()
        full_url = urljoin(BASE_URL, src)
        snacks.append({'name': clean_name, 'image_url': full_url})

    return country, snacks


def saveImages(snacks, country, base_folder=OUTPUT_DIR):
    safe_country = country.strip().replace(" ", "_").lower()
    folder = os.path.join(base_folder, safe_country)
    os.makedirs(folder, exist_ok=True)

    for snack in snacks:
        name = snack['name']
        img_url = snack['image_url']
        filename = sanitizeFilename(name)

        ext = os.path.splitext(img_url)[1].split('?')[0]
        if not ext or len(ext) > 5:
            ext = '.jpg'

        filepath = os.path.join(folder, filename + ext)

        if os.path.exists(filepath):
            print(f"Image already exists, skipping: {filepath}")
            continue
        try:
            response = requests.get(img_url, stream=True, timeout=10)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            print(f"Saved image: {filepath}")
        except Exception as e:
            print(f"Failed to download image for {name}: {e}")

def runSnackboxAPI():
    html = fetchHtmlWithCurl(BASE_URL)
    if not html:
        print("Failed to fetch HTML.")
        return {}

    country, snacks = parseSnacksAndCountry(html)
    if not snacks:
        print("No snacks found.")
        return {}

    print(f"\nThis months country: {country}")
    print(f"Found {len(snacks)} snacks. Downloading images...")
    saveImages(snacks, country)

    # 🔹 Return dictionary: { country: [snack names] }
    return {country: [snack['name'] for snack in snacks]}