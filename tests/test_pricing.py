import importlib.util
import pathlib
import unittest


def load_pricing_module():
    pricing_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "addons"
        / "pt_clinic"
        / "domain"
        / "pricing.py"
    )
    spec = importlib.util.spec_from_file_location("pricing", pricing_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PricingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pricing = load_pricing_module()

    def test_percent_discount(self):
        self.assertEqual(self.pricing.apply_discount(100, "percent", 10), 90)

    def test_fixed_discount_floor_zero(self):
        self.assertEqual(self.pricing.apply_discount(50, "fixed", 60), 0)

    def test_best_promo_price(self):
        self.assertEqual(self.pricing.best_promo_price(100, [95, 80, 90]), 80)

    def test_contract_price_priority(self):
        self.assertEqual(self.pricing.resolve_contract_price(120, 75, 10), 75)


if __name__ == "__main__":
    unittest.main()

