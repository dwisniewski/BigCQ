import owlready2
import re2
ontology_path = "/home/dawid/foodon/foodon/foodon.owl"
ontology = owlready2.get_ontology(f"file://{ontology_path}").load()

### THIS IS A PROOF OF CONCEPT PROVIDING SOME GUIDELINES ON HOW TEMPLATES CAN BE MATERIALIZED INTO ACTUAL CQs AND QUERY TEMPLATES


def _get_label(obj) -> str:
    """ Return best label for given ontology.
    Args:
        obj (Any): object to get label from
    Returns:
        str: label of a given object
    """
    if isinstance(obj, str):
    	return obj
    if hasattr(obj, 'prefLabel') and obj.prefLabel.first() is not None:
        return obj.prefLabel.first()
    elif obj.label.first() is not None:
        return obj.label.first()
    else:
        return obj.name



# materialize SPO
sample_query_template = "SELECT ?x WHERE { ?x rdfs:subClassOf [ owl:intersectionOf ( <C2> [ rdf:type owl:Restriction ; owl:onProperty <OP1> ; owl:someValuesFrom <C3> ] ) ] . }"
sample_cq_template = "Which C2 OP1 C3?"

for subject in ontology.classes():
	for property in subject.get_class_properties():
		for object in relation[subject]:
            query = re.sub('<C2>', subject.iri, sample_query_template)
            query = re.sub('<C3>', object.iri, query)
            query = re.sub('<OP1>', property.iri, query)

            cq = re.sub(r'\bC2\b', _get_label(subject), sample_cq_template)
            cq = re.sub(r'\bC3\b', _get_label(object), cq)
            cq = re.sub(r'\bC2\b', _get_label(property), cq)

            # new query and cq represent materialized templates filled with iris and labels.

## owlready supports .is_a fields on class instances to get all superclasses which can be used to transform SS
