from synonymes_generator import SynonymesGenerator
from typing import Any, Dict, List, Set
import json
import re


def load_json(path: str) -> Dict[str, Any]:
    with open(path) as json_file:
        return json.load(json_file)

class CQGenerator:
    def __init__(self, spo_templates_path: str,
                 spo_templates_equivalence_path: str,
                 subclass_templates_path: str,
                 equivalence_templates_path: str,
                 synonymes_path: str):
        self.spo_templates = load_json(spo_templates_path)
        self.subclass_templates = load_json(subclass_templates_path)
        self.spo_templates_equivalence = load_json(spo_templates_equivalence_path)
        self.equivalence_templates = load_json(equivalence_templates_path)
        self.synonymes = load_json(synonymes_path)

    def materialize_placeholders_with_phrases(self, analyzed_shape: Dict[str, Any], placeholders: Set[str],
        cqs: List[str],
        attach_verb_to_car: bool = False) -> List[str]:
        ''' Transform general CQ tempalets into actual CQ templates'''
        for placeholder in placeholders:
            replacement = analyzed_shape[placeholder].lower()
            if attach_verb_to_car:
                if placeholder == 'VERB':
                    continue
                if placeholder == 'CAR':
                    replacement = f'something that {analyzed_shape["VERB"]} {analyzed_shape["CAR"]}'
            cqs = [re.sub('{'+placeholder+'}', replacement, q) for q in cqs]
        return list(set(cqs))

    def materialize_to_both_spo_subclass(self, analyzed_shape: Dict[str, Any],
                                         placeholders: Set[str],
                                         question_type: str,
                                         is_equivalence: bool = False) -> List[str]:
        placeholders_with_verb = placeholders | {'VERB'}
        placeholders_without_verb = placeholders - {'VERB'}
        result = []

        if analyzed_shape['is_equivalence']:
            spo_templates = self.spo_templates_equivalence
            subclass_templates = self.equivalence_templates
        else:
            spo_templates = self.spo_templates
            subclass_templates = self.subclass_templates

        result += self.materialize_placeholders_with_phrases(
            analyzed_shape, placeholders_with_verb,
            SynonymesGenerator(
                spo_templates[question_type], self.synonymes).get_all_expansions())

        result += self.materialize_placeholders_with_phrases(
            analyzed_shape, placeholders_without_verb,
            SynonymesGenerator(
                subclass_templates[question_type], self.synonymes).get_all_expansions(),
                attach_verb_to_car=True)
        return list(set(result))

    def make_cqs(self, verbalization: str, analyzed_shape: Dict[str, Any]):
        queries = {
            "ASK": [],
            "SELECT_CAR": [],
            "SELECT_CAD": [],
            "SELECT_VERB": [],
            "SELECT_COUNT_CAR": [],
            "SELECT_COUNT_CAD": [],
            "SELECT_COUNT_VERB": [],
        }

        if analyzed_shape['is_equivalence']:
            spo_templates = self.spo_templates_equivalence
            subclass_templates = self.equivalence_templates
        else:
            spo_templates = self.spo_templates
            subclass_templates = self.subclass_templates

        # if main verb is different than 'is'
        if analyzed_shape['VERB'] is not None:
            # we generate ASK queries by taking possible formulations from patterns_simple_spo and replacing placeholders (CAR, VERB, CAD) with appropriate fragments extracted from verbalized axiom
            queries['ASK'] = self.materialize_to_both_spo_subclass(analyzed_shape, {'CAR', 'VERB', 'CAD'}, 'ASK', analyzed_shape['is_equivalence'])

            if not analyzed_shape['complex_domain'] and len(analyzed_shape['domain_elems']) > 0:
                for query_type in ['SELECT_CAD', 'SELECT_COUNT_CAD']:
                    queries[query_type] = self.materialize_to_both_spo_subclass(analyzed_shape, {'CAR', 'VERB'}, query_type, analyzed_shape['is_equivalence'])
            if not analyzed_shape['complex_range'] and len(analyzed_shape['range_elems']) > 0:
                for query_type in ['SELECT_CAR', 'SELECT_COUNT_CAR']:
                    queries[query_type] = self.materialize_placeholders_with_phrases(analyzed_shape, {'CAD', 'VERB'}, SynonymesGenerator(spo_templates[query_type], self.synonymes).get_all_expansions())

            for query_type in ['SELECT_VERB', 'SELECT_COUNT_VERB']:
                queries[query_type] = self.materialize_placeholders_with_phrases(analyzed_shape, {'CAD', 'CAR'}, SynonymesGenerator(spo_templates[query_type], self.synonymes).get_all_expansions())
        else:
            queries['ASK'] = self.materialize_placeholders_with_phrases(analyzed_shape, {'CAD', 'CAR'}, SynonymesGenerator(subclass_templates['ASK'], self.synonymes).get_all_expansions())

            if not analyzed_shape['complex_domain'] and len(analyzed_shape['domain_elems']) > 0:
                for query_type in ['SELECT_CAD', 'SELECT_COUNT_CAD']:
                    queries[query_type] = self.materialize_placeholders_with_phrases(analyzed_shape, {'CAR'}, SynonymesGenerator(subclass_templates[query_type], self.synonymes).get_all_expansions())

            if not analyzed_shape['complex_range'] and len(analyzed_shape['range_elems']) > 0:
                for query_type in ['SELECT_CAR', 'SELECT_COUNT_CAR']:
                        queries[query_type] = self.materialize_placeholders_with_phrases(analyzed_shape, {'CAD'}, SynonymesGenerator(subclass_templates[query_type], self.synonymes).get_all_expansions())
        return queries

    def paraphrase_cqs(self, cqs):
        cqs_paraphrased = []
        for cq in cqs:
            matched = re.search("what is (c[0-9]) that ([do]p[0-9]) (.*)", cq)
            #matched = re.search("what is (c[0-9]) that (c[0-9]) ([do]p[0-9]) (.*)", cq)
            if matched:
                paraphrases = [
                    f'[WHAT] {matched.groups(0)[0]} {matched.groups(0)[1]} {matched.groups(0)[2]}',
                    f'[WHAT] [TYPES] of {matched.groups(0)[0]} {matched.groups(0)[1]} {matched.groups(0)[2]}',
                    f'[WHAT] [KIND] of {matched.groups(0)[0]} {matched.groups(0)[1]} {matched.groups(0)[2]}',
                    f'[WHAT] [TYPES] of are {matched.groups(0)[0]} which {matched.groups(0)[1]} {matched.groups(0)[2]}',
                    f'[WHAT] [IS] {matched.groups(0)[0]} which {matched.groups(0)[1]} {matched.groups(0)[2]}',
                    f'[WHAT] [IS] {matched.groups(0)[0]} {matched.groups(0)[1]} {matched.groups(0)[2]}',
                    f'[WHAT] {matched.groups(0)[0]} [DOES] {matched.groups(0)[1]} {matched.groups(0)[2]}',
                    f'[WHAT] {matched.groups(0)[0]} has {matched.groups(0)[1]} {matched.groups(0)[2]}',
                    f'[WHAT] {matched.groups(0)[0]} have {matched.groups(0)[1]} {matched.groups(0)[2]}',
                ]

                cqs_paraphrased += SynonymesGenerator(paraphrases, self.synonymes).get_all_expansions()
            cqs_paraphrased.append(cq)
        return cqs_paraphrased

class SPARQLOWLGenerator:
    def __init__(self):
        pass

    @staticmethod
    def make_queries(preprocessed_axiom_shape, analyzed_shape):
        queries = {
            "ASK": None,
            "SELECT_CAR": None,
            "SELECT_CAD": None,
            "SELECT_VERB": None,
            "SELECT_COUNT_CAR": None,
            "SELECT_COUNT_CAD": None,
            "SELECT_COUNT_VERB": None,
        }

        turtle = re.sub('[ \t\n]+', ' ', preprocessed_axiom_shape.strip())

        # We can always generate ASK query, we need to simply put the axiom into ASK { } clause
        queries['ASK'] = 'ASK WHERE { ' + turtle + ' }'

        # if
        if analyzed_shape['VERB'] is not None:
            # transform the main property into variable
            ask_for_property = re.sub(rf'<{analyzed_shape["VERB"]}>', '?x', turtle)
            queries['SELECT_VERB'] = 'SELECT ?x WHERE { ' + ask_for_property + ' }'
            queries['SELECT_COUNT_VERB'] = 'SELECT (COUNT(?x) AS ?cnt) WHERE { ' + ask_for_property + ' }'

        # if there is some identifier in domain and it is simple named class - we can make it query focus
        if not analyzed_shape['complex_domain'] and len(analyzed_shape['domain_elems']) > 0:
            # if class axiom domain is a single named class - w transform it into a query target
            id_to_variable = list(analyzed_shape['domain_elems'])[0]
            #print(f"id_to_variable: {id_to_variable}")
            #print("regex: <"+id_to_variable+">")
            ask_for_domain = re.sub(rf'<{id_to_variable}>', '?x', turtle)
            queries['SELECT_CAD'] = 'SELECT ?x WHERE { ' + ask_for_domain + ' }'
            queries['SELECT_COUNT_CAD'] = 'SELECT (COUNT(?x) AS ?cnt) WHERE { ' + ask_for_domain + ' }'

        # if there is some identifier in range and it is simple named class - we can make it query focus
        if not analyzed_shape['complex_range'] and len(analyzed_shape['range_elems']) > 0:
            id_to_variable = list(analyzed_shape['range_elems'])[0]
            ask_for_range = re.sub(rf'<{id_to_variable}>', '?x', turtle)
            queries['SELECT_CAR'] = 'SELECT ?x WHERE { ' + ask_for_range + ' }'
            queries['SELECT_COUNT_CAR'] = 'SELECT (COUNT(?x) AS ?cnt) WHERE { ' + ask_for_range + ' }'
        return queries
