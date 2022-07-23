# Jidou-Hikki-Django
Jidou-Hikki Django Implementation

# Project Description
Jidou Hikki (自動 筆記, lit. "Automatic Writing") is a web-based Japanese-Language learning tool for automatically taking notes of vocabularies found in a text.

# Usage
1. Install dependencies using `poetry install -vvv` or `pip install -e .`. If you got a ModuleNotFoundError for _lzma when installing jamdict, read this [thread](https://github.com/ultralytics/yolov5/issues/1298) for the fix.
2. Run `python manage.py makemigrations`.
3. Run `python manage.py migrate`.
4. Run `python manage.py runserver localhost:8000`.
5. Open `localhost:8000` in the browser to start using the app.
6. Optionally, you can run the server on your WIFI interface instead and open the app from your phone's or table's browser. You need to add the IP address in the `ALLOWED_HOSTS` variable inside `jh_server/settings.py`

# Features
1. Automatic furigana generation.
2. Automatically take notes of vocabulary from across text to flash card collection (Currently only stores vocabs with kanji).
3. (wip) Spaced repetition review.
4. (wip) Get translation and more detailed information from a word.
5. (wip) Simple, nice, and intuitive UI/UX.
