from odoo.tests.common import TransactionCase


class TestStarterComponentBridge(TransactionCase):
    def test_bridge_models_and_requirement_traceability_fields_exist(self):
        self.assertIn("sco.hvac.product.component.bridge", self.env)
        self.assertIn("sco.hvac.product.component.bridge.line", self.env)
        self.assertIn("component_bridge_line_id", self.env["sco.hvac.boq.line"]._fields)
        self.assertIn("sco_boq_line_id", self.env["purchase.order.line"]._fields)

    def test_purchase_is_not_created_by_requirement_generation(self):
        self.assertFalse(self.env["purchase.order"].search([("origin", "=", "SCO-HVAC-COMPONENT-BRIDGE-TEST")]))
