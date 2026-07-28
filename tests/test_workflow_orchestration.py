import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def load_workflow(name):
    path = WORKFLOWS / name
    return yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


class WorkflowOrchestrationTests(unittest.TestCase):
    def test_main_pushes_are_generated_and_validated_by_one_workflow(self):
        sync_workflow = load_workflow("sync-generated-rules.yml")
        sync_push = sync_workflow["on"]["push"]

        self.assertEqual(["main"], sync_push["branches"])
        self.assertNotIn(
            "paths",
            sync_push,
            "Every main push must use the serial generate-and-validate workflow",
        )

        validate_workflow = load_workflow("validate-rules.yml")
        self.assertNotIn(
            "push",
            validate_workflow["on"],
            "A second push workflow races with generated rule synchronization",
        )

    def test_pull_requests_and_manual_runs_keep_independent_validation(self):
        validate_workflow = load_workflow("validate-rules.yml")
        triggers = validate_workflow["on"]

        self.assertIn("pull_request", triggers)
        self.assertIn("workflow_dispatch", triggers)


if __name__ == "__main__":
    unittest.main()
