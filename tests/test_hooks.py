import importlib.util
import pathlib
import unittest


def load_hooks_module():
    hooks_path = pathlib.Path(__file__).resolve().parents[1] / "addons" / "pt_clinic" / "hooks.py"
    spec = importlib.util.spec_from_file_location("pt_clinic_hooks", hooks_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeCursor:
    def __init__(self, column_types):
        self.column_types = column_types
        self.queries = []
        self.params = []
        self._last_params = None

    def execute(self, query, params=None):
        self.queries.append(query)
        self.params.append(params)
        self._last_params = params

    def fetchone(self):
        if not self._last_params:
            return None
        return (self.column_types.get(tuple(self._last_params)),)


class HookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hooks = load_hooks_module()

    def test_migrates_legacy_translated_char_columns(self):
        cursor = FakeCursor(
            {
                ("pt_clinic_dashboard", "name"): "varchar",
                ("pt_branch", "name"): "jsonb",
            }
        )

        self.hooks.migrate_translated_char_columns(cursor)

        alter_queries = [query for query in cursor.queries if "ALTER TABLE" in query]
        self.assertEqual(len(alter_queries), 1)
        self.assertIn('ALTER TABLE "pt_clinic_dashboard"', alter_queries[0])
        self.assertIn("jsonb_build_object('en_US'", alter_queries[0])


if __name__ == "__main__":
    unittest.main()
