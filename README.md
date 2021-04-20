# BigCQ
A big synthetic dataset of CQ templates to SPARQL-OWL templates mappings.

## What is that?
`BigCQ` is a dataset of Competency Question templates paired with SPARQL-OWL query templates. These represent templates of ontology requirements formalizations which are then translated into SPARQL-OWL query language used to query T-Box level of ontologies. Thus, such a dataset can be used in various scenarios regarding ontology authoring:

* Provide a large scale dataset for automatization of CQ involving tasks (automatic extraction of Glossary of Terms from requirements, automatic translation of CQs into queries to check how mature given ontology is).
* Allow to understand better the relation between human-language and ontology constructs.
* Make Competency Question driven ontology authoring more popular, since, although CQs are suggested in many ontology design methodologies, there is very limited set of CQs made publicly available.
* Provide guidelines on how CQs can be constructed to target given modelling styles.

## How to cite that work?
We generated a persistent URI for that dataset using Zenodo:
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4704674.svg)](https://doi.org/10.5281/zenodo.4704674)


## Where can I find the data?
In `BigCQ_dataset` there are the following files and folders:
* `cq_templates_only.txt` -- a list of all generated 77575 unique CQ-templates.
* `sparqlowl_templates_only.txt` -- a list of all generated 549 unique SPARQL-OWL query templates.
* `query_templates_to_cq_template_mappings` -- a folder with mapping from SPARQL-OWL templates to CQ templates. Each file is represents a different SPARQL-OWL query template is represented by a JSON document following the following schema:
```
  {
    'query': 'SPARQL_OWL_QUERY',
    'cqs': ['CQ1', 'CQ2', ...]
  }
```

## Is it possible to modify/extend the dataset?
Sure! Along with the dataset we published the `Python` code creating the dataset from scratch.
Just enter `dataset_preparation_scripts` and type: ` PYTHONPATH=. python3 make_dataset.py ` in your terminal to regenerate the dataset. If you want to add some new CQ templates or synonym sets, you can find them in `dataset_preparation_scripts/statements_to_cqs_transformations/`:
* File synonym_classes defines various synonymes sets.
* Files with filenames starting with `cq_general_templates` define CQ templates for various needs.

Just edit these files and run `make_dataset.py` to make your new (better? :) ) dataset!

## How to use the templates to test my ontology?
We provide a sample (proof of concept) code (using owlready2), that can parse an ontology and fill the placeholders with labels / IRIs. You can use it to adapt to your own needs.

You can find the `materialize.py` script in `template_materialization_poc` folder

## Is there an input verbalizations with axiom shapes file provided?
Sure! Please look at `verbalization2turtle.csv` in the main folder of the repository.

## What is the license?
MIT License.

## What are the weak points of the dataset?
We made an evaluation on a separate set of CQs and SPARQL-OWL queries. The list of cases that are not covered by the dataset is provided in `evaluation` folder. We hope that in the next version of `BigCQ` it will be possible to handle them properly.

We hope that the dataset will help you in your work.
