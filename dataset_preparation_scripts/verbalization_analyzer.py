import spacy
from typing import Optional
import re

# Load English tokenizer, tagger, parser and NER
nlp = spacy.load("en_core_web_sm")


class Analyzer:
    def __init__(self):
        self.placeholders = {'c', 'op', 'i', 'dp', 'dt'}
        # these random verbs are used to materialize properties,
        # so that correct dependency trees can be constructed
        self.some_verbs = ['uses', 'knows', 'thinks', 'helps', 'proves',
                           'shows', 'makes', 'confirms', 'contains', 'converts']

    def process(self, text):
        # ACE materializes equivalences into 2 liners
        is_equivalence = True if len(text.split("\n")) > 1 else False
        text = text.split("\n")[0]

        materialized_axiom, idx2verb = self.materialize_properties(text)
        materialized_verbs_doc = nlp(materialized_axiom)
        return self.analyze_shape(materialized_verbs_doc, idx2verb,
                                  materialized_axiom, is_equivalence)


    def materialize_properties(self, text):
        properties_types = {elem for elem in self.placeholders if elem.endswith('p')}
        idx2verb = dict()

        for property_type in properties_types:
            for match in re.finditer(rf'\b{property_type}[0-9]+\b', text):
                found_idx = match.group()
                if found_idx not in idx2verb:
                    idx2verb[found_idx] = self.some_verbs[len(idx2verb)]

        for idx, verb in idx2verb.items():
            text = re.sub(rf'\b{idx}\b', verb, text)
        return text, idx2verb

    def dematerialize_properties(self, text, idx2verb):
        '''
            Verbalizations of axioms (e.g. Every c1 op1 c2) are temporally transformed to replace properties with verbs -- that allows us to build proper dependency trees.
            This function reverses this process -- we search for verbs used to substitute property placeholders and replace them with the original ids
            Every c1 knows c2; with (knows = op1) -> Every c1 op1 c2

        Args:
            text: a verbalization of the axiom shape
            replacements: a map describing how given verbs are linked to artificial property ids.
        '''
        for idx, verb in idx2verb.items():
            text = re.sub(rf'\b{verb}\b', idx, text)
        return text

    def analyze_shape(self, doc, idx2verb, text, is_equivalence):
        ''' Analyze the axiom shape to extract features used to generate CQs '''
        root_verb = self.get_root_verb(doc) # what is the root verb (after_replacement)
        root_id = self.get_root_id(doc, idx2verb)

        class_axiom_domain_span = [self.get_subtree_span(token) for token in doc if token.head == root_verb and token.dep_ in ['nsubj']][0]
        class_axiom_range_span = [self.get_subtree_span(token) for token in doc if token.head == root_verb and token.dep_ in ['attr', 'dobj', 'prep', 'conj']]
        class_axiom_range_span = self.merge_conjunctions_spans(text, class_axiom_range_span)[0]

        class_axiom_domain = text[class_axiom_domain_span[0]:class_axiom_domain_span[1]]
        class_axiom_range = text[class_axiom_range_span[0]:class_axiom_range_span[1]]

        class_axiom_domain = \
            self.dematerialize_properties(class_axiom_domain, idx2verb)
        class_axiom_range = \
            self.dematerialize_properties(class_axiom_range, idx2verb)

        is_complex_domain, domain_elems = \
            self.is_complex_description(class_axiom_domain)
        is_complex_range, range_elems = \
            self.is_complex_description(class_axiom_range)

        class_axiom_domain = re.sub(r'\ba ', ' ', class_axiom_domain)  # reject "a" before class id
        class_axiom_range = re.sub(r'\ba ', '', class_axiom_range) # reject "a" before class id

        return {
            'root_verb': root_verb,
            'complex_domain': is_complex_domain,
            'complex_range': is_complex_range,
            'domain_elems': domain_elems,
            'range_elems': range_elems,
            'is_equivalence': is_equivalence,
            'VERB': root_id,
            'CAD': class_axiom_domain,
            'CAR': class_axiom_range,
        }
    def get_root_verb(self, doc):
            ''' Get a root of dependency parse tree; the main verb. Return token.

            Args:
                doc: SpaCy document
            Returns:
                root: SpaCy token with root verb
            '''
            root = [token for token in doc if token.dep_ == 'ROOT'][0]
            return root

    def get_root_id(self, doc, idx2verb) -> Optional[str]:
        ''' Get a root of dependency parse tree; the main verb. Return placeholder idx (e.g. op1).

        Args:
            doc: SpaCy document
            idx2verb: a mapping from indexes to verbs (op1 -> uses);
            to obtain a proper dependency parse tree, we need to substitute artificial property ids (e.g. op1)
            that are by default interpreted as proper nouns and transform them into verbs.
            Otherwise, verbalizations such as "Every c1 op1 c2" won't produce dependency tree, because there will be no verb
            (c1 op1 c2 will be interpreted as a sequence of proper nouns).
            ACE internally assumes that these properties (op/dp) are verbs.

        Returns:
            id of the placeholder assigned with the main verb. If the main verb is simply "is", we return None.
        '''
        root = [token for token in doc if token.dep_ == 'ROOT'][0]
        for idx, verb in idx2verb.items():
            if verb == root.text:
                return idx
        return None

    def get_subtree_span(self, token):
        ''' Get range of offsets of a dependency-parse subtree of a given token.

        Args:
            token to be processed

        Returns:
            span (begin_idx, end_idx) representing positions of the beginning and end of the subtree in text.
        '''
        start_ids = [t.idx for t in token.subtree if t.text if t.text.lower() != 'every']
        end_ids = [t.idx + len(t) for t in token.subtree if t.text if t.text not in ['!', '.']]

        start = min(start_ids) if len(start_ids) > 0 else -1
        end = max(end_ids) if len(end_ids) > 0 else -1
        return (start, end)

    def merge_conjunctions_spans(self, text, spans):
        ''' If two spans are separated with simple ' and ' we would like to merge them.

        Args:
            text: text to check if 'and' separates two given spans
            spans: spans to be checked

        Returns:
            merged spans, or if 'and' does not separate them -- return the spans as is
        '''
        if len(spans) == 2:
            if text[spans[0][1]:spans[1][0]].strip() == 'and':
                return [(spans[0][0], spans[1][1])]
        return spans

    def is_complex_description(self, description):
        ''' Check if an argument, being a sequence of words coming from verbalized axiom shpape defines a complex class.
            If more than one entity is mentioned -- then some compositions of them are defining the class description.
            Similarly, we treat 'at least/at most/exactly/no' modifiers preceding class names as additional modifiers creating complex classes.

        Args:
            description: a sequence of words to be tested

        Returns:
            boolean value deciding if there is a single named class/property in the argument (then return False) or if there is a complex class description.
        '''

        args = set()
        for match in re.finditer(r'\b(Everything|no|at least|at most|exactly|c[0-9]|dt[0-9]|i[0-9]|dp[0-9]|op[0-9])\b', description):
            args.add(match.group())

        return len(args) > 1, args
