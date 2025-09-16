import subprocess
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests

BASE_URL = "https://www.universalyums.com/"
OUTPUT_DIR = "logic/snackbox/snack_images"

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
    
    # Find the div that contains slider-wrap
    container_div = soup.find('div', class_='slider-wrap')
    if not container_div:
        print("Could not find div with class 'slider-wrap'")
        return None, []

    # Let's check its parent div for the <h4> element with the country name
    parent_div = container_div.parent
    if not parent_div:
        print("Could not find parent container of slider-wrap")
        return None, []

    # Find the h4 inside the parent container
    h4 = parent_div.find('h4')
    if not h4:
        print("Could not find <h4> containing country name")
        country = "Unknown Country"
        
    else:
        h4_text = h4.get_text(strip=True)
        # Extract country name from text like: "What's inside the Mexico box?"
        match = re.search(r"inside the (.+?) box", h4_text, re.I)
        if match:
            country = match.group(1)
        else:
            country = "Unknown Country"

    # Extract snack images inside slider-wrap
    snacks = []
    for img in container_div.find_all('img'):
        alt = img.get('alt', '').strip()
        src = img.get('src')
        if not src or len(alt) < 2:
            continue

        alt_lower = alt.lower()
        if any(x in alt_lower for x in ['logo', 'universal yums', 'facebook', 'instagram', 'box']):
            continue

        full_url = urljoin(BASE_URL, src)
        snacks.append({'name': alt, 'image_url': full_url})
    return country, snacks

def save_images(snacks, country, base_folder="snack_images"):
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
        return

    country, snacks = parse_snacks_and_country(html)
    if not snacks:
        print("No snacks found.")
        return

    print(f"\nThis months country: {country}")
    print(f"Found {len(snacks)} snacks. Downloading images...")
    save_images(snacks, country)
    return "success"
