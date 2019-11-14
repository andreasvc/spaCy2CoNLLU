# spacyconllu

Parse text with Spacy and write output in CoNLL-U format;
cf. http://universaldependencies.org/docs/format.html

## Requirements

* Python 3.4+
* spaCy (https://spacy.io/usage/#installation)

## Usage

Parse text with Spacy and write output in CoNLL-U format.

Usage: spacyconllu.py [inputfile] [outputfile] [--model=<name>]

By default: read stdin, write to stdout, model=en_core_web_sm
Expects input to contain one document/paragraph/sentence per line.
Cf. https://spacy.io/ and http://universaldependencies.org/format.html

## Credits

Based on code by @rgalhama
