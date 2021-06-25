# Jidou-Hikki-Django
Jidou-Hikki Django Implementation

# Project Description
Jidou Hikki (自動 筆記, lit. "Automatic Writing") is a web-based Japanese-Language learning tool.
It is aimed for students that want to acquire vocabularies by reading japanese text, articles, etc. (preferably after acquiring most of the essential grammars).

# Usage
1. Install dependencies using `poetry install -vvv` or `pip install -e .`.
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

# Motivation
Personally speaking, memorizing vocabularies and kanjis grouped in JLPT-level or common occurrence is not practical enough when I want to actually read actual Japanese article outside of text-book.
Some apps already provide some form of aid by providing Japanese text with furigana attached and vocabulary lists.
However, most of the time it's from online news article that I don't really have much interest in (I want to read LN or WN!)

There are also some browser-plugins that provide on-the-fly japanese dictionaries which will be shown when we hover over Japanese words.
This tremendously helped in making reading raw Japanese less of a hassle.
But what if I want to review the new words that I encountered?
The only option would be to take notes of them manually and, if time permits, input them into flashcard decks like Anki.

This project aims to help with the last bit of the learning process. User can input pieces of text to be processed by the application.
The process includes analyzing and separating the words inside the text (specifically the kanjis).
These words will be stored into the User's flashcard collection.
After reading the text (or not at all), user can review all the words that showed up later.
