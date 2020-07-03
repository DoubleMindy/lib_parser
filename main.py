import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse
import os
import json
import argparse

LIB_DOMAIN = 'http://tululu.org/'
FANTASTIC_PART = 'l55/{}'
BOOK_DIR = "book_dir"
IMAGE_DIR = "images"
JSON_FILE = 'book_info.json'

if os.path.exists(JSON_FILE):
	os.remove(JSON_FILE)

parser = argparse.ArgumentParser()
parser.add_argument('--start_page', default=1, type=int)
parser.add_argument('--end_page', default=701, type=int)
parser.add_argument('--skip_imgs', action="store_true", default=False)
parser.add_argument('--skip_txt', action="store_true", default=False)
parser.add_argument('--dest_folder', default='', type=str)
parser.add_argument('--json_path', default='', type=str)
args = parser.parse_args()

BOOK_DIR = os.path.join(args.dest_folder, BOOK_DIR)
IMAGE_DIR = os.path.join(args.dest_folder, IMAGE_DIR)

Path(BOOK_DIR).mkdir(parents=True, exist_ok=True)
Path(IMAGE_DIR).mkdir(parents=True, exist_ok=True)
Path(args.json_path).mkdir(parents=True, exist_ok=True)

def download_txt(url, filename, folder=BOOK_DIR):
	book_text = requests.get(url, allow_redirects = False)
	if book_text.status_code != 200:
		return 400
	with open("{}/{}.txt".format(folder, sanitize_filename(filename)), "w") as book_file:
		book_file.write(book_text.text)
	return os.path.join(folder, filename)

def download_image(url, filename, folder=IMAGE_DIR):
	book_img = requests.get(url, allow_redirects = False)
	if book_img.status_code != 200:
		return 400
	with open(os.path.join(folder, filename), 'wb') as img_file:
		img_file.write(book_img.content)
	return os.path.join(folder, filename)

book_counts = 0
books_to_json = list()
image_path = text_path = None

for page_index in range(args.start_page, args.end_page+1):
	response = requests.get(urljoin(LIB_DOMAIN, FANTASTIC_PART.format(page_index)), allow_redirects = False)
	soup = BeautifulSoup(response.text, 'lxml')
	cards = soup.select('table.d_book')
	for book in cards:
		book_info = dict()
		book_url = urljoin(LIB_DOMAIN, book.select_one('a')['href'])
		soup = BeautifulSoup(requests.get(book_url, allow_redirects = False).text, 'lxml')
		only_headers = soup.select_one('h1').text
		only_headers = " ".join(only_headers.split()).split(" :: ")
		book_title, book_author = only_headers
		if not args.skip_txt:
			text_path = download_txt(book_url, book_title)
		if not args.skip_imgs:
			cover_refs = soup.select_one('div.bookimage a img')['src']
			image_url = urljoin(LIB_DOMAIN, cover_refs)
			image_name = urlparse(image_url)
			image_path = download_image(image_url, os.path.basename(image_name.path))
		comments = soup.select('div.texts span')
		comments = [comment.text for comment in comments]
		genres = soup.select('span.d_book a')
		genres = [genre.text for genre in genres]
		book_info['title'] = book_title
		book_info['author'] = book_author
		book_info['img_src'] = image_path
		book_info['book_path'] = text_path
		book_info['comments'] = comments
		book_info['genres'] = genres
		books_to_json.append(book_info)

if args.json_path != '':
	json_file_path = os.path.join(args.json_path, JSON_FILE)
else:
	json_file_path = os.path.join(args.dest_folder, JSON_FILE)
with open(json_file_path, "a") as file:
	json.dump(books_to_json, file, indent = 4, ensure_ascii=False)
