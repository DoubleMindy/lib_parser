# Парсер онлайн-библиотеки tululu
Данный скрипт скачивает все тексты и картинки книг с сайта tululu.org в разделе "Научная фантастика". 
Также скачиваются комментарии к книге и дополнительная информация в JSON-файл.
### Как установить
* Скачайте код
* Запустите команду `pip install -r requirements.txt` для получения актуальной версии библиотек
* Запустите скрипт командой `python3 main.py`
Скрипт создаст папки `books` и `images`, хранящие тексты и обложки книг соответственно, а также файл `book_info.json`, хранящий подробное описание (с комментариями пользователей) каждой книги.
### Аргументы
Данный скрипт поддерживает следующий набор аргументов:
* `--start_page` позволяет скачивать книги, начиная с определенной страницы (по умолчанию с первой);
* `--end_page` позволяет скачивать книги до определенной страницы (по умолчанию 701);
* `--dest_folder` меняет директорию, где будут расположены папки и JSON-файл (по умолчанию все данные сохраняются в текущей папке);
* `--json_path` меняет директорию для JSON-файла (по умолчанию в текущей папке). 

<b>Важно: расположение файла при использовании этой опции приоритетнее, чем использование `dest_folder`!</b>

Пример: при одновременно заданном `--dest_folder a/b/c` и `--json_path d` папки `books` и `images` будут иметь путь `a/b/c/books` и `a/b/c/images`, но JSON-файл будет расположен в `d/book_info.json`
* `--skip_imgs` пропускает скачивание изображений (по умолчанию отключено);
* `--skip_txt` пропускает скачивание текста (по умолчанию отключено);

### Примеры запуска

* `python3 main.py --dest_folder a --skip_imgs --skip_txt` сохраняет JSON-файл в папку `a`, не скачивая ничего больше
* `python3 main.py --start_page 4 --json_path b` скачивает все данные, начиная с четвертой страницы в текущую директорию, а JSON-файл сохраняет в папку `b`
* `python3 main.py --end_page 2 --dest_folder b --json_path b/c` скачивает данные первух двух страниц в папку `b`, а для JSON-файла создает подпапку `b/c`

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
