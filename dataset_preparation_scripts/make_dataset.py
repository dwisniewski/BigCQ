import csv
from verbalization_analyzer import Analyzer
from generators import CQGenerator, SPARQLOWLGenerator
from summarizer import Summarizer
import pprint

def is_ACE_error(verbalization: str) -> bool:
    ''' Check if verbalization contains ACE error '''
    return verbalization.startswith("/* BUG:")

resources_path = './debug_patterns/'
pp = pprint.PrettyPrinter(indent=4)

analyzer = Analyzer()
cq_generator = CQGenerator(
    spo_templates_path = f'{resources_path}/cq_general_templates_spo.json',
    subclass_templates_path = f'{resources_path}/cq_general_templates_subclass.json',
    synonymes_path = f'{resources_path}/synonym_classes.json')
query_generator = SPARQLOWLGenerator()

with open('../axiom2turtle.preprocessed.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    result = []

    for row in csv_reader:
        idx = row[0]
        verbalization = row[1]
        axiom_shape_preprocessed = row[2]

        if is_ACE_error(verbalization) or verbalization in result:
            continue

        analyzed_shape = analyzer.process(verbalization)

        cqs = cq_generator.make_cqs(verbalization, analyzed_shape)
        queries = SPARQLOWLGenerator.make_queries(axiom_shape_preprocessed, analyzed_shape)

        result.append((verbalization, cqs, queries))

    Summarizer(result).make_summary()
