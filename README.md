# spacyconllu

Parse text with Spacy and write output in CoNLL-U format;
cf. http://universaldependencies.org/docs/format.html

## Requirements

* Python 3.4+
* spaCy (https://spacy.io/usage/#installation)

## Usage

Parse text with Spacy and write output in CoNLL-U format:

	$ spacyconllu.py [inputfile] [outputfile] [--model=<name>]

By default: read stdin, write to stdout, model=en_core_web_sm
Expects input to contain one document/paragraph/sentence per line.
Cf. https://spacy.io/ and http://universaldependencies.org/format.html

## Example

```
$ echo "Why did the chicken cross the road?" | python3 spacyconllu.py
# sent_id = 1
# text = Why did the chicken cross the road?
1       Why     why     ADV     WRB     PronType=int/rel        5       advmod  _       _
2       did     do      VERB    VBD     VerbForm=fin|Tense=past 5       aux     _       _
3       the     the     DET     DT      _       4       det     _       _
4       chicken chicken NOUN    NN      Number=sing     5       nsubj   _       _
5       cross   cross   VERB    VB      VerbForm=inf    5       root    _       _
6       the     the     DET     DT      _       7       det     _       _
7       road    road    NOUN    NN      Number=sing     5       dobj    _       _
8       ?       ?       PUNCT   .       PunctType=peri  5       punct   _       _

```

## Credits

Based on code by @rgalhama
