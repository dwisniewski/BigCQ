import csv
from verbalization_analyzer import Analyzer
from generators import CQGenerator, SPARQLOWLGenerator
from summarizer import Summarizer
from serializer import Serializer
import pprint
import pickle

def is_ACE_error(verbalization: str) -> bool:
    ''' Check if verbalization contains ACE error '''
    return verbalization.startswith("/* BUG:")

resources_path = './release_patterns/'
pp = pprint.PrettyPrinter(indent=4)

analyzer = Analyzer()
cq_generator = CQGenerator(
    spo_templates_path = f'{resources_path}/cq_general_templates_spo.json',
    spo_templates_equivalence_path = f'{resources_path}/cq_general_templates_spo_equivalence.json',
    subclass_templates_path = f'{resources_path}/cq_general_templates_subclass.json',
    equivalence_templates_path = f'{resources_path}/cq_general_templates_equivalence.json',
    synonymes_path = f'{resources_path}/synonym_classes.json')
query_generator = SPARQLOWLGenerator()

with open('../verbalization2turtle.csv') as csv_file:
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
        for category in cqs:
            cqs[category] = cq_generator.paraphrase_cqs(cqs[category])
        queries = SPARQLOWLGenerator.make_queries(axiom_shape_preprocessed, analyzed_shape)

        result.append((verbalization, cqs, queries))

    serializer = Serializer(result)
    serializer.serialize_result()
    #outfile = open('result','wb')
    #pickle.dump(result, outfile)
    #outfile.close()

    #Summarizer(result).print_queries()
    Summarizer(result).make_summary()
    #Summarizer(result).print_cqs()
