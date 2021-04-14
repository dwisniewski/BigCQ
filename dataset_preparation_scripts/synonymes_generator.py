import re
from typing import List


class SynonymesGenerator:
    def __init__(self, patterns_to_use, synonymes):
        self.cq_patterns_to_use = patterns_to_use
        self.synonymes = synonymes

    @staticmethod
    def _contains_synset(cq: str) -> bool:
        """ Checks if phrases which should be replaced with synonymes are still
        in the CQ. All such phrases are enclosed in [] and should be keys
        coming from `synonymes` map """
        return re.search(r'\[.*\]', cq) is not None

    def _expand_synset(self, synset: str, cq: str) -> List[str]:
        """ Given a synset to be replaced with all synonymes, generate n cqs with all possible
        synset expansions.
        Eg. synset: [is] -> is, are
        transforms cq: [is] there X to [is there X, are there X] """
        expanded_variants = []
        if re.search(synset, cq) is None:
            # given synset does not occur in a CQ
            return [cq]  # nothing to expand
        else:
            for synonym in self.synonymes[synset]:
                expanded_variants.append(re.sub(re.escape(synset), synonym, cq))
        return expanded_variants

    def expand_cq_pattern(self, cq_pattern: str) -> List[str]:
        """ For a given cq pattern utilizing synsets (enclosed with []),
        generate all possible materializations. """
        expanded_variants = [cq_pattern]
        for synset in self.synonymes:
            # for each predefined [synset]
            for idx in range(len(expanded_variants)):
                # apply materialization to every from the current cq materializations
                expanded_variants[idx] = self._expand_synset(synset, expanded_variants[idx])
                # each single cq pattern becomes a list, thus flattening is required.
            expanded_variants = [p for sublist in expanded_variants for p in sublist]  #flatten

        return expanded_variants

    def get_all_expansions(self) -> List[str]:
        all_variants = []
        for cq_pattern in self.cq_patterns_to_use:
            all_variants += self.expand_cq_pattern(cq_pattern)
        return all_variants

    def get_random_expansions(self, limit: int) -> List[str]:
        return random.sample(self.get_all_expansions(), limit)
