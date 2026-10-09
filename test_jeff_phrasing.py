import importlib
import unittest

jp = importlib.import_module("jeff-phrasing")


class ContractionTests(unittest.TestCase):
    def setUp(self):
        self.now = 1000.0
        jp.clock = lambda: self.now
        jp.contractions_enabled = False
        jp.last_toggle_time = float("-inf")

    def lookup(self, stroke):
        return jp.lookup([stroke])

    def toggle(self):
        self.now += 1.0
        return self.lookup(jp.CONTRACTION_TOGGLE_STROKE)

    def test_default_is_expanded(self):
        self.assertEqual(self.lookup("SWR*F"), "I have not")
        self.assertEqual(self.lookup("KWHR*F"), "he has not")
        self.assertEqual(self.lookup("SWR*E"), "I am not")
        self.assertEqual(self.lookup("SWRA*"), "I cannot")
        self.assertEqual(self.lookup("SWRAO*"), "I will not")
        self.assertEqual(self.lookup("SWR*"), "I do not")
        self.assertEqual(self.lookup("SWR*EF"), "I have not been")

    def test_toggle_contracts(self):
        self.assertEqual(self.toggle(), "{}")
        self.assertTrue(jp.contractions_enabled)
        self.assertEqual(self.lookup("SWR*F"), "I haven't")
        self.assertEqual(self.lookup("KWHR*F"), "he hasn't")
        self.assertEqual(self.lookup("SWR*E"), "I am not")
        self.assertEqual(self.lookup("SWRA*"), "I can't")
        self.assertEqual(self.lookup("SWRAO*"), "I won't")
        self.assertEqual(self.lookup("SWR*"), "I don't")
        self.assertEqual(self.lookup("SWR*EF"), "I haven't been")

    def test_toggle_twice_restores_expanded(self):
        self.toggle()
        self.toggle()
        self.assertEqual(self.lookup("SWR*F"), "I have not")

    def test_repeated_lookups_of_one_stroke_flip_once(self):
        # Plover and plugins (e.g. `stroke in dictionary`) look up one stroke
        # several times within milliseconds.
        self.now += 1.0
        for _ in range(2):
            self.lookup(jp.CONTRACTION_TOGGLE_STROKE)
            self.now += 0.01
        self.assertTrue(jp.contractions_enabled)

    def test_contract_expand_round_trip(self):
        for text in ["do not", "does not", "did not", "cannot", "could not",
                     "should not", "will not", "would not", "are not",
                     "is not", "were not", "was not", "have not", "has not",
                     "had not"]:
            self.assertEqual(jp.expand(jp.contract(text)), text)

    def test_unrelated_text_untouched(self):
        self.assertEqual(jp.contract("I am not sure whether not"), "I am not sure whether not")
        self.assertEqual(jp.expand("I shan't"), "I shan't")

    def test_reverse_lookup_in_both_modes(self):
        for contracted in (False, True):
            jp.contractions_enabled = contracted
            for text in ("I have not", "I haven't"):
                self.assertIn(("SWR*F",), jp.reverse_lookup(text))

    def test_toggle_stroke_is_not_a_phrase(self):
        with self.assertRaises(KeyError):
            jp.build_phrase([jp.CONTRACTION_TOGGLE_STROKE])


if __name__ == "__main__":
    unittest.main()
