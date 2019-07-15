#!/usr/bin/env python2
from __future__ import print_function
from builtins import dict

from configargparse import ArgumentParser, RawTextHelpFormatter as RawText

from collections import defaultdict
import os.path

from plwn_comments import Comment
from basicutils.simple import POS_num_to_str as pos_str
from basicutils.text_lemmatizer import TextLemmatizer
from corpus_ccl.cclutils import write_ccl, get_tagset
from corpus_ccl.corpus_object_utils import iter_tokens, get_coarse_lexeme_pair
from npsemrel.carrot.db import db


def get_synset_comments(connection, on_unknown_tag=Comment.ACTION_SKIP):
    synset_units = _get_synset_units(connection)
    unit_comments = get_unit_comments(connection, on_unknown_tag)
    synset_comments = defaultdict(set)
    for (synset, units) in synset_units.items():
        for unit in units:
            if unit not in unit_comments:
                continue
            synset_comments[synset] |= {unit_comments[unit]}
    return dict(synset_comments)


def _get_synset_units(connection):
    query = "SELECT syn_id, lex_id FROM unitandsynset"
    synset_units = defaultdict(set)
    with connection.cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            (synset, unit) = row
            synset_units[synset] |= {unit}
    return dict(synset_units)


def get_unit_comments(connection, on_unknown_tag=Comment.ACTION_ACCEPT):
    query = "SELECT ID, comment FROM lexicalunit"
    comments = {}
    with connection.cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            (id_, comment_str) = row
            if not comment_str:
                continue
            comment = Comment.parse(row[1], on_unknown_tag=on_unknown_tag)
            if not comment:
                continue
            comments[id_] = comment
    return comments


def get_lemmas(connection):
    query = "SELECT ID, pos, lemma FROM lexicalunit"
    with connection.cursor() as cursor:
        cursor.execute(query)
        return {id_: (pos_str(pos), lemma)
                for (id_, pos, lemma) in cursor.fetchall()}


def get_comment_text(comments, tags="DWP", emotive_examples=False):
    if isinstance(comments, Comment):
        comments = {comments}
    texts = _get_comment_text_aux(comments, tags)
    if emotive_examples:
        emotive_texts = _get_comment_text_aux(comments, {"A1", "A2"})
        texts |= {text.split("[")[1][:-1]
                  for text in emotive_texts
                  if "[" in text}
    return texts


def _get_comment_text_aux(comments, tags="DWP"):
    return {text
            for comment in comments
            for (tag, examples) in comment.items()
            if tag in tags
            for text in examples}


def create_corpus_from_comments(lemmatizer, comments, tags="DWP",
                                emotive_examples=False, path=None, read=False):
    text = "\n".join(get_comment_text(comments, tags, emotive_examples))
    if not sum(letter.isalpha() for letter in text):
        return None
    return lemmatizer.create_corpus_from_text(text, path, read)


def tag_lemmas_in_corpus(corpus, tagset, synset, lexeme_pairs):
    for token in iter_tokens(corpus):
        if get_coarse_lexeme_pair(token, tagset, True) in lexeme_pairs:
            if not token.has_metadata():
                token.create_metadata()
            metadata = token.get_metadata()
            metadata.set_attribute("sense:ukb:syns_id", str(synset))


def _main():
    args = _get_args()
    if args.units:
        raise NotImplementedError()

    connection = db.DB().connect(args.connection)
    tagger_config = os.path.expanduser(args.tagger_config)
    tagger_model = os.path.expanduser(args.tagger_model or "")
    lemmatizer = TextLemmatizer(tagger_config, tagger_model)
    tagset = get_tagset(args.tagset)

    comments = get_synset_comments(connection, args.on_unknown_tag)
    units = _get_synset_units(connection)
    lemmas = get_lemmas(connection)

    for synset in comments:
        path = os.path.join(args.outdir, str(synset) + ".ccl")
        if os.path.exists(path):
            continue
        corpus = create_corpus_from_comments(lemmatizer, comments[synset],
                                             args.tags, args.emotive_examples,
                                             None, True)
        if not corpus:
            continue
        synset_lemmas = {lemmas[unit] for unit in units[synset]}
        tag_lemmas_in_corpus(corpus, tagset, synset, synset_lemmas)
        write_ccl(corpus, path)


def _get_args():
    parser = ArgumentParser(description=__doc__, formatter_class=RawText)
    parser.add_argument("-c", "--config", is_config_file=True)
    parser.add_argument("--connection", required=True)
    parser.add_argument("--units", action="store_true")
    parser.add_argument("--tags", default="DWP")
    parser.add_argument("--emotive-examples", action="store_true")
    parser.add_argument("--tagger-config", required=True)
    parser.add_argument("--tagger-model")
    parser.add_argument("--tagset", default="nkjp")
    parser.add_argument("--on-unknown-tag", default="accept",
                        choices=["skip", "accept", "error"])
    parser.add_argument("-o", "--outdir", default=".")
    return parser.parse_args()


if __name__ == "__main__":
    _main()
