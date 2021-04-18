import os
import json
import hashlib


class Serializer:
    def __init__(self, result, out_folder='./BigCQ_mapping/'):
        self.out_folder = out_folder
        self.data = result
        os.mkdir(out_folder)

    def serialize_result(self):
        json_out = dict()
        for _, cqs, queries in self.data:
            for key in queries:
                if queries[key]:
                    query = queries[key]
                    if query not in json_out:
                        json_out[query] = []
                    json_out[query] += cqs[key]

        for idx, query in enumerate(json_out):
            with open(os.path.join(self.out_folder, f'query_to_cqs_{idx + 1}.json'), 'w') as f:
                f.write(json.dumps(
                    {"query": query, "cqs": json_out[query]},
                    indent=4, sort_keys=True)
                )
