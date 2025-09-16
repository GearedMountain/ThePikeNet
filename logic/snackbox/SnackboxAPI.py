import subprocess
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests

BASE_URL = "https://www.universalyums.com/"
OUTPUT_DIR = "dynamic/snack_images"

def fetch_html_with_curl(url):
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

def sanitize_filename(name):
    name = name.strip().lower()
    name = re.sub(r'\s*image\s*$', '', name)
    name = re.sub(r"[^\w\-_.']+", '_', name)
    name = name.replace("'", "")
    return name

def parse_snacks_and_country(html):
    soup = BeautifulSoup(html, 'html.parser')
    container_div = soup.find('div', class_='slider-wrap')
    if not container_div:
        print("Could not find div with class 'slider-wrap'")
        return None, []

    parent_div = container_div.parent
    if not parent_div:
        print("Could not find parent container of slider-wrap")
        return None, []

    h4 = parent_div.find('h4')
    if not h4:
        country = "Unknown Country"
    else:
        h4_text = h4.get_text(strip=True)
        match = re.search(r"inside the (.+?) box", h4_text, re.I)
        country = match.group(1) if match else "Unknown Country"

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


def save_images(snacks, country, base_folder=OUTPUT_DIR):
    safe_country = country.strip().replace(" ", "_").lower()
    folder = os.path.join(base_folder, safe_country)
    os.makedirs(folder, exist_ok=True)

    for snack in snacks:
        name = snack['name']
        img_url = snack['image_url']
        filename = sanitize_filename(name)

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
    html = fetch_html_with_curl(BASE_URL)
    if not html:
        print("Failed to fetch HTML.")
        return {}

    country, snacks = parse_snacks_and_country(html)
    if not snacks:
        print("No snacks found.")
        return {}

    print(f"\nThis months country: {country}")
    print(f"Found {len(snacks)} snacks. Downloading images...")
    save_images(snacks, country)

    # 🔹 Return dictionary: { country: [snack names] }
    return {country: [snack['name'] for snack in snacks]}
