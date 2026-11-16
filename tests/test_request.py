import unittest
from football_pipeline.request import validate_request


class RequestTests(unittest.TestCase):
    def base(self):
        return {'schemaVersion': 1, 'id': 'scope-test', 'dates': ['2026-11-21'],
                'scope': {'competitionIds': ['47']}, 'categories': ['wins-btts', 'other-markets']}

    def test_variable_scope_and_explicit_routes(self):
        for count in (1, 5, 44, 89):
            spec = self.base()
            spec['scope'] = {'fixtureIds': [str(10000+i) for i in range(count)]}
            parsed = validate_request(spec)
            self.assertEqual(len(parsed['scope']['fixtureIds']), count)
            self.assertEqual(parsed['routing']['retrieval']['model'], 'gpt-6-luna')
            self.assertEqual(parsed['routing']['lead']['model'], 'gpt-6-astra')

    def test_scope_typos_and_implicit_global_search_fail(self):
        for scope in ({}, {'competitionID': ['47']}, {'fixtureIds': ['1;exit']}):
            spec = self.base(); spec['scope'] = scope
            with self.assertRaises(ValueError): validate_request(spec)

    def test_builder_subset_and_limit(self):
        spec = self.base(); spec['categories'].append('bet-builders')
        with self.assertRaises(ValueError): validate_request(spec)
        spec['builderFixtureIds'] = ['100', '101']
        self.assertEqual(validate_request(spec)['builderFixtureIds'], ['100', '101'])
        spec['builderFixtureIds'] = [str(i) for i in range(10)]
        with self.assertRaises(ValueError): validate_request(spec)

    def test_invalid_clock_budget_and_routes(self):
        for field, value in [('dates', ['21/11/2026']), ('timezone', 'Not/AZone'),
                             ('limits', {'maxModelCalls': True}), ('routing', {'retrieval': {'model': 'x --extra'}})]:
            spec=self.base(); spec[field]=value
            with self.assertRaises(ValueError): validate_request(spec)


if __name__ == '__main__': unittest.main()
