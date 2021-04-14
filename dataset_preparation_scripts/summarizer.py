class Summarizer:
    def __init__(self, verbalization_cqs_queries_triples):
        self.data = verbalization_cqs_queries_triples

    def calc_unique_verbalizations(self, data):
        verbalizations = [d[0].lower() for d in data]
        return len(set(verbalizations))

    def calc_number_of_unique_cqs(self, data):
        total_cqs = []
        for _, cqs, _ in self.data:
            for category in cqs:
                for cq in cqs[category]:
                    total_cqs.append(cq.lower())

        return len(set(total_cqs))

    def calc_number_of_unique_queries(self, data):
        total_queries = []
        for _, _, queries in self.data:
            for category in queries:
                if queries[category]:
                    total_queries.append(queries[category].lower())

        return len(set(total_cqs))

    def average_queries_per_cq(self, data):
        queries_per_cq = dict()

        for _, cqs, queries in self.data:
            for category in queries:  # ASK, SELECT_CAD, etc
                for cq in cqs[category]:
                    cq = cq.lower()
                    if cq not in queries_per_cq:
                        queries_per_cq[cq] = set()

                    if queries[category]:
                        queries_per_cq[cq].add(queries[category])

        return 1.0 * sum([len(v) for k, v in queries_per_cq.items()]) / len(queries_per_cq)

    def average_cqs_per_query(self, data):
        cqs_per_query = dict()

        for _, cqs, queries in self.data:
            for category in queries:  # ASK, SELECT_CAD, etc
                query = queries[category]
                if query:
                    if query not in cqs_per_query:
                        cqs_per_query[query] = set()

                    for cq in cqs[category]:
                        cq = cq.lower()
                        cqs_per_query[query].add(cq)

        return 1.0 * sum([len(v) for k, v in cqs_per_query.items()]) / len(cqs_per_query)

    def calc_number_of_unique_cqs_per_category(self, data):
        total_cqs = dict()
        for _, cqs, _ in self.data:
            for category in cqs:
                if category not in total_cqs:
                    total_cqs[category] = set()
                for cq in cqs[category]:
                    total_cqs[category].add(cq.lower())

        return {k: len(v) for k, v in total_cqs.items()}

    def calc_number_of_unique_queries_per_category(self, data):
        total_queries = dict()
        for _, _, queries in self.data:
            for category in queries:
                if category not in total_queries:
                    total_queries[category] = set()
                if queries[category]:
                    total_queries[category].add(queries[category])

        return {k: len(v) for k, v in total_queries.items()}

    def make_summary(self):
        print(f"Number of unique verbalizations: {self.calc_unique_verbalizations(self.data)}")
        print(f"Number of unique cqs: {self.calc_number_of_unique_cqs(self.data)}")
        print(f"Number of unique queries: {self.calc_number_of_unique_cqs(self.data)}")
        print(f"Average queries per CQ: {self.average_queries_per_cq(self.data)}")
        print(f"Average CQs per query: {self.average_cqs_per_query(self.data)}")
        print(f"Number of unique CQs per question type: {self.calc_number_of_unique_cqs_per_category(self.data)}")
        print(f"Number of unique queries per question type: {self.calc_number_of_unique_queries_per_category(self.data)}")
