"""Parse text with Spacy and write output in CoNLL-U format.

Usage: spacyconllu.py [inputfile] [outputfile] [--model=<name>]

By default: read stdin, write to stdout, model=en_core_web_sm
Expects input to contain one document/paragraph/sentence per line.
Cf. https://spacy.io/ and http://universaldependencies.org/format.html"""
import os
import sys
import getopt
import spacy


def get_lemma(word):
    """Fix Spacy's non-standard lemmatization of pronouns."""
    if word.lemma_ == '-PRON-':
        return word.text if word.text == 'I' else word.text.lower()
    return word.lemma_


def get_morphology(tag, tagmap):
    """Get morphological features FEATS for a given XPOS tag."""
    if tagmap and tag in tagmap:
        # NB: replace '|' to fix invalid value 'PronType=int|rel' in which
        # 'rel' is not in the required 'attribute=value' format for FEATS.
        # val may be an int: Person=3
        feats = ['%s=%s' % (prop, str(val).replace('|', '/'))
                for prop, val in tagmap[tag].items()
                if isinstance(prop, str)]
        if feats:
            return '|'.join(feats)
    return '_'


def doc_to_conllu(doc, out, sent_id, tagmap, prefix=''):
    """Prints parsed sentences in CONLL-U format
    (as used in Universal Dependencies).
    Cf. http://universaldependencies.org/docs/format.html
    """
    for sent in doc.sents:
        print('# sent_id = %s' % (prefix + str(sent_id)), file=out)
        print('# text = %s' % str(sent.sent).strip(), file=out)

        for wordidx, word in enumerate(sent, 1):
            if word.text.isspace():  # skip non-tokens such as '\n'
                continue

            # Find head
            if word.dep_ == 'root':
                head_idx = 0
            else:
                head_idx = word.head.i + 1 - sent[0].i

            print(
                    # 1. ID: Word index.
                    str(wordidx),
                    # 2. FORM: Word form or punctuation symbol.
                    word.text or '_',
                    # 3. LEMMA: Lemma of word form.
                    get_lemma(word) or '_',
                    # 4. UPOSTAG: Universal part-of-speech tag drawn from
                    #    revised version of the Google universal POS tags.
                    word.pos_ or '_',
                    # 5. XPOSTAG: Language-specific part-of-speech tag;
                    #    underscore if not available.
                    word.tag_ or '_',
                    # 6. FEATS: List of morphological features from the
                    #    universal feature inventory or from a defined
                    #    language-specific extension; underscore if not
                    #    available.
                    get_morphology(word.tag_, tagmap),
                    # 7. HEAD: Head of the current token, which is either a
                    #    value of ID or zero (0).
                    str(head_idx),
                    # 8. DEPREL: Universal Stanford dependency relation to the
                    #    HEAD (root iff HEAD = 0) or a defined
                    #    language-specific subtype of one.
                    word.dep_.lower() or '_',
                    # 9. DEPS: List of secondary dependencies.
                    '_',
                    # 10. MISC: Any other annotation.
                    '_',
                    sep='\t',
                    file=out)
        sent_id += 1
        print('', file=out)
    return sent_id


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
    sent_id = 1
    out = open(args[1], 'w', encoding='utf8') if len(args) > 1 else None
    try:
        with open(input_file, encoding='utf8') as inp:
            for doc in nlp.pipe(inp, batch_size=1000, disable=['ner']):
                sent_id = doc_to_conllu(doc, out, sent_id, tagmap, prefix='')
    finally:
        if out is not None:
            out.close()


if __name__ == "__main__":
    main()
