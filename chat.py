import os
import csv
import datetime
import dataclasses
from collections import defaultdict
from re import A
from typing import Optional, List


FILE = 'jabber_chat_2021_2022_translated.csv'


class Chat:

    @dataclasses.dataclass
    class Message:

        timestamp: datetime.datetime
        sender: str
        receiver: str
        body_original: str
        body_translated: str
        language: Optional[str]

    def __init__(self, source_file):
        self.idx = -1
        self.messages = []
        with open(source_file) as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                self.messages.append(self.Message(
                    timestamp=datetime.datetime.fromisoformat(row['ts']),
                    sender=row['sender'],
                    receiver=row['to'],
                    body_original=row['body'],
                    body_translated=row['body_en'],
                    language=row['body_language'] or None,
                ))

    def __iter__(self):
        return iter(self.messages)

    def get_full(self, translation: bool = True):
        if translation:
            return '\n'.join(f' {m.body_translated} ' for m in self)
        return '\n'.join(f' {m.body_original} ' for m in self)


def get_bad_words() -> List[str]:
    with open('swearwords.txt') as fp:
        swearwords = [x for x in fp.read().split('\n') if x and not x.startswith('#')]
    return swearwords


def get_movie_titles() -> List[str]:
    with open('imdb_top_1000.csv') as fp:
        reader = csv.DictReader(fp)
        movies = [x['Series_Title'] for x in reader]
    return movies


def get_words() -> List[str]:
    with open('words.txt') as fp:
        words = [x for x in fp.read().split('\n') if x and not x.startswith('#')]
    return words


chat = Chat(FILE)

# (1) How many bad words are in the messages?
bad_words = {w: 0 for w in get_bad_words()}
for message in chat:
    for word in bad_words:
        bad_words[word] += len(message.body_translated.lower().split(word.lower())) - 1
usage = sorted([(b, a) for a, b in bad_words.items()], reverse=True)
print(f'Top 10 bad words:\n{os.linesep.join(f"{b} - {a} times" for a, b in usage[0:10])}\n')

## (2) In what time zones do the hackers probably live?
hours_per_sender = defaultdict(list)
for message in chat:
    hours_per_sender[message.sender].append(message.timestamp.hour)
averages = {sender: sum(hours) // len(hours) for sender, hours in hours_per_sender.items()}
average_counts = {a: 0 for a in averages.values()}
for hour in averages.values():
    average_counts[hour] += 1
usage = sorted([(b, a) for a, b in average_counts.items()], reverse=True)
print(f'Top 5 UTC offsets:\n{os.linesep.join(f"{b - 12}h - {a} users" for a, b in usage[0:5])}\n')

## (4) What are the most commonly used words not present in a dictionary?
common_words = get_words()
uncommon_words = defaultdict(int)
for message in chat:
    for word in message.body_translated.lower().split(' '):
        if word not in common_words and word.isalpha():
            uncommon_words[word] += 1
usage = sorted([(b, a) for a, b in uncommon_words.items()], reverse=True)
print(f'Top 20 unusual words:\n{os.linesep.join(f"{b} - {a} times" for a, b in usage[0:30])}\n')

# (7) What are titles of some movies or songs they reference?
movies = {m: 0 for m in get_movie_titles()}
chat_full = chat.get_full().lower()
for movie in movies:
    movies[movie] += len(chat_full.split(f' {movie.lower()} ')) - 1
usage = sorted([(b, a) for a, b in movies.items()], reverse=True)
print(f'Top 30 referenced movies:\n{os.linesep.join(f"{b} - {a} times" for a, b in usage[0:30])}\n')

# ( ) What smileys do the hackers use?
smileys = {
    ':D': 0,
    ':P': 0,
    ':)': 0,
    '>:': 0,
}
chat_full = chat.get_full(translation=False).lower()  # use untranslated full chat
for smiley in smileys.keys():
    smileys[smiley] += len(chat_full.split(smiley.lower())) - 1
usage = sorted([(b, a) for a, b in smileys.items()], reverse=True)
print(f'Smiley usage:\n{os.linesep.join(f"{b} - {a} times" for a, b in usage)}\n')
