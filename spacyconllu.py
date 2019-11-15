"""Parse text with Spacy and write output in CoNLL-U format.

Usage: spacyconllu.py [inputfile] [outputfile] [--model=<name>]

By default: read stdin, write to stdout, model=en_core_web_sm
Expects input to contain one document/paragraph/sentence per line of
*untokenized* text. No line breaks within sentences!
The input is parsed in batches of 1000 lines at a time.
Cf. https://spacy.io/ and http://universaldependencies.org/format.html"""
import os
import sys
import getopt
import spacy

# Constants for field numbers:
ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC = range(10)
# https://universaldependencies.org/format.html
# ID: Word index, integer starting at 1 for each new sentence; may be a range
#     for multiword tokens; may be a decimal number for empty nodes (decimal
#     numbers can be lower than 1 but must be greater than 0).
# FORM: Word form or punctuation symbol.
# LEMMA: Lemma or stem of word form.
# UPOS: Universal part-of-speech tag.
# XPOS: Language-specific part-of-speech tag; underscore if not available.
# FEATS: List of morphological features from the universal feature inventory or
#        from a defined language-specific extension; underscore if not
#        available.
# HEAD: Head of the current word, which is either a value of ID or zero (0).
# DEPREL: Universal dependency relation to the HEAD (root iff HEAD = 0) or a
#         defined language-specific subtype of one.
# DEPS: Enhanced dependency graph in the form of a list of head-deprel pairs.
# MISC: Any other annotation.


def getlemma(word):
    """Fix Spacy's non-standard lemmatization of pronouns."""
    if word.lemma_ == '-PRON-':
        return word.text if word.text == 'I' else word.text.lower()
    return word.lemma_


def getmorphology(word, tagmap):
    """Get morphological features FEATS for a given word."""
    if tagmap and word.tag_ in tagmap:
        # NB: replace '|' to fix invalid value 'PronType=int|rel' in which
        # 'rel' is not in the required 'attribute=value' format for FEATS.
        # val may be an int: Person=3
        feats = ['%s=%s' % (prop, str(val).replace('|', '/'))
                for prop, val in tagmap[word.tag_].items()
                if isinstance(prop, str)]
        if feats:
            return '|'.join(feats)
    return '_'


def renumber(conllusent):
    """Fix non-contiguous IDs because of multiword tokens or removed tokens"""
    mapping = {line[ID]: n for n, line in enumerate(conllusent, 1)}
    mapping[0] = 0
    for line in conllusent:
        line[ID] = mapping[line[ID]]
        line[HEAD] = mapping[line[HEAD]]
    return conllusent


def writeconllu(doc, out, sentid, tagmap, prefix=''):
    """Prints parsed sentences in CONLL-U format
    (as used in Universal Dependencies).
    Cf. http://universaldependencies.org/docs/format.html
    """
    for sent in doc.sents:
        print('# sent_id = %s' % (prefix + str(sentid)), file=out)
        print('# text = %s' % str(sent.sent).strip(), file=out)
        conllu = []
        for wordidx, word in enumerate(sent, 1):
            if word.text.isspace():  # skip non-tokens such as '\n'
                continue
            # Compute head index
            if word.dep_ == 'ROOT':
                headidx = 0
            else:
                headidx = word.head.i + 1 - sent[0].i
            conllu.append([
                    wordidx,                      # 1. ID
                    word.text or '_',             # 2. FORM
                    getlemma(word) or '_',        # 3. LEMMA
                    word.pos_ or '_',             # 4. UPOS
                    word.tag_ or '_',             # 5. XPOS
                    getmorphology(word, tagmap),  # 6. FEATS
                    headidx,                      # 7. HEAD
                    word.dep_.lower() or '_',     # 8. DEPREL
                    '_',                          # 9. DEPS
                    '_',                          # 10. MISC
                    ])
        for line in renumber(conllu):
            print(*line, sep='\t', file=out)
        print('', file=out)
        sentid += 1
    return sentid


def main():
    """CLI"""
    longopts = ['model=', 'help']
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], '', longopts)
    except getopt.GetoptError:
        print(__doc__)
        return
    opts = dict(opts)
    if '--help' in opts:
        print(__doc__)
        return
    input_file = args[0] if args else sys.stdin.fileno()
    if args and not os.path.exists(input_file):
        raise ValueError('%s does not exist!' % input_file)
    model = opts.get('--model', 'en_core_web_sm')

    nlp = spacy.load(model)
    tagmap = nlp.Defaults.tag_map
    sentid = 1
    out = open(args[1], 'w', encoding='utf8') if len(args) > 1 else None
    try:
        with open(input_file, encoding='utf8') as inp:
            for doc in nlp.pipe(inp, batch_size=1000, disable=['ner']):
                sentid = writeconllu(doc, out, sentid, tagmap, prefix='')
    finally:
        if out is not None:
            out.close()


if __name__ == "__main__":
    main()
