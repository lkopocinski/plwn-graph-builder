class LexicalUnit:
    POS_STR_DICT = {
        1: 'verb',
        2: 'noun',
        3: 'adverb',
        4: 'adjective',
        5: 'verb_en',
        6: 'noun_en',
        7: 'adverb_en',
        8: 'adjective_en'
    }

    def __init__(self, lu_id, lemma, pos, domain, variant, lexicon=None):
        self.lu_id = lu_id
        self.lemma = lemma
        self.pos = pos
        self.domain = domain
        self.variant = variant
        self.lexicon = lexicon

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'lu_id={self.lu_id}, '
                f'lemma={str(self.lemma)}, '
                f'pos={self.pos}, '
                f'domain={self.domain}, '
                f'variant={self.variant}, '
                f'lexicon={self.lexicon})')

    def __str__(self):
        return (f'{self.lemma}:'
                f'{self.POS_STR_DICT[self.pos]}:'
                f'{self.variant}')
