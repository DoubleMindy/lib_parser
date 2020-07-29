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
parser.add_argument('--end_page', default=2, type=int)
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
	book_response = requests.get(url, allow_redirects = False)
	if book_response.status_code != 200:
		return
	full_path = os.path.join(folder, sanitize_filename(filename))
	with open(full_path, "w") as book_file:
		book_file.write(book_response.text)
	return os.path.join(folder, filename)

def download_image(url, filename, folder=IMAGE_DIR):
	img_response = requests.get(url, allow_redirects = False)
	if img_response.status_code != 200:
		return
	full_path = os.path.join(folder, filename)
	with open(full_path, 'wb') as img_file:
		img_file.write(img_response.content)
	return os.path.join(folder, filename)

def find_books(page_index):
	full_request = urljoin(LIB_DOMAIN, FANTASTIC_PART.format(page_index))
	response = requests.get(full_request, allow_redirects = False)
	soup = BeautifulSoup(response.text, 'lxml')
	return soup.select('table.d_book')

def find_header(soup):
	only_headers = soup.select_one('h1').text
	only_headers = " ".join(only_headers.split()).split(" :: ")
	book_title, book_author = only_headers
	return book_title, book_author

def find_comments(soup):
	comments = soup.select('div.texts span')
	return [comment.text for comment in comments]

def find_genres(soup):
	genres = soup.select('span.d_book a')
	return [genre.text for genre in genres]

def process_one_book(book):
	book_url = urljoin(LIB_DOMAIN, book.select_one('a')['href'])
	soup = BeautifulSoup(requests.get(book_url, allow_redirects = False).text, 'lxml')
	book_title, book_author = find_header(soup)
	if not args.skip_txt:
		text_path = download_txt(book_url, book_title)
	if not args.skip_imgs:
		cover_refs = soup.select_one('div.bookimage a img')['src']
		image_url = urljoin(LIB_DOMAIN, cover_refs)
		image_name = urlparse(image_url)
		image_path = download_image(image_url, os.path.basename(image_name.path))
	book_info = {
	'title': book_title,
	'author': book_author,
	'img_src': image_path,
	'book_path': text_path,
	'comments': find_comments(soup),
	'genres': find_genres(soup)
	}
	return book_info

def main():
	book_counts = 0
	books_in_json = list()
	image_path = text_path = None

	for page_index in range(args.start_page, args.end_page+1):
		cards = find_books(page_index)
		for book in cards:
			books_in_json.append(process_one_book(book))

	if args.json_path != '':
		json_file_path = os.path.join(args.json_path, JSON_FILE)
	else:
		json_file_path = os.path.join(args.dest_folder, JSON_FILE)

	with open(json_file_path, "a") as file:
		json.dump(books_in_json, file, indent = 4, ensure_ascii=False)

if __name__ == "__main__":
	main()
