import pytest

from triage.schema import split_sentences


@pytest.mark.parametrize("text, expected", [
    ("Tyre gone. Waiting for recovery!", ["Tyre gone.", "Waiting for recovery!"]),
    ("Is it leaking? Yes, I think so.", ["Is it leaking?", "Yes, I think so."]),
    # abbreviations and numbers do not end a sentence
    ("Arrived approx. 14.30 at St. Helens depot. Box at 4.5 C.",
     ["Arrived approx. 14.30 at St. Helens depot.", "Box at 4.5 C."]),
    ("Pallets e.g. tiles were cracked. Driver ok.",
     ["Pallets e.g. tiles were cracked.", "Driver ok."]),
    # a lower-case continuation is not a new sentence
    ("Running late... probably 2 hours. Sorry.", ["Running late... probably 2 hours.", "Sorry."]),
    # line breaks always split (transcripts, email sign-offs); blank lines vanish
    ("Driver: lorry's stuck\n\nDepot: where are you\nDriver: A14", [
        "Driver: lorry's stuck", "Depot: where are you", "Driver: A14"]),
    ("  no punctuation at all  ", ["no punctuation at all"]),
    ("", []),
])
def test_split_sentences(text, expected):
    assert split_sentences(text) == expected


def test_every_sentence_is_a_verbatim_substring():
    text = 'He said "it\'s fine." Then the drum leaked. Call me ASAP!!'
    parts = split_sentences(text)
    assert parts == ['He said "it\'s fine."', "Then the drum leaked.", "Call me ASAP!!"]
    assert all(p in text for p in parts)
