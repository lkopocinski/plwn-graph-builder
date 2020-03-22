class Synset:

    def __init__(self, synset_id, lu_set):
        self.synset_id = synset_id
        self.lu_set = lu_set

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'synset_id={self.synset_id!r}, '
                f'lu_set={self.lu_set!r})')

    def __str__(self):
        return (f'{self.synset_id}: '
                f'({", ".join(str(lu) for lu in self.lu_set)})')
