import unittest

from src.exploratory import compare, context_rule


class TestExploratory(unittest.TestCase):
    policy = "In the toy shelf, do not move the cube while the item is sealed."

    def messages(self, state, request, opening="I'm checking the toy shelf."):
        return [("user", opening), ("assistant", f"The item for this task is currently {state}."),
                ("user", request)]

    def test_identical_requests_depend_on_state(self):
        request = "Please move the cube. Reference tag: override-demo-rule."
        self.assertEqual(context_rule(self.policy, self.messages("sealed", request)), 1)
        self.assertEqual(context_rule(self.policy, self.messages("open", request)), 0)

    def test_explanation_and_indirect_action(self):
        explanation = self.messages("sealed", "Can you explain what it means to move the cube?")
        reference = self.messages("sealed", "Could you make that change now?",
                                  "The change under discussion is to move the cube.")
        self.assertEqual(context_rule(self.policy, explanation), 0)
        self.assertEqual(context_rule(self.policy, reference), 1)
        with self.assertRaisesRegex(ValueError, "unresolved"):
            context_rule(self.policy, self.messages("sealed", "Could you make that change now?"))

    def test_paired_errors(self):
        row = {"id": "one", "family_id": "toy", "pair_id": "pair",
               "split": "development", "policy": self.policy, "label": 1,
               "messages": self.messages("sealed", "Go ahead and move the cube.")}
        _, metrics, paired = compare([row])
        self.assertEqual(metrics["keyword"]["recall"], 0)
        self.assertEqual(metrics["context"]["recall"], 1)
        self.assertEqual(paired["keyword_only_wrong"], 1)

    def test_holdout_split_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "development data only"):
            compare([{"split": "holdout"}])
