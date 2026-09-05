"""Synthetic guard responses; never calls a hosted service."""
import unittest
from unittest.mock import patch
from integrations import sipi_guard


class GuardAcceptance(unittest.TestCase):
    def test_only_explicit_approval_can_reach_paid_tool(self):
        for decision in ({}, {"decision": "REVIEW"}, {"decision": "approved"}, {"decision": None}, {"decision": "BLOCKED"}, {"decision": "FLAGGED"}):
            with self.subTest(decision=decision), patch.object(sipi_guard, "evaluate", return_value=decision):
                reached = []
                try:
                    sipi_guard.guard(1, "synthetic-search", "api")
                    reached.append("paid tool")
                except (sipi_guard.SpendBlocked, sipi_guard.SpendNeedsApproval):
                    pass
                self.assertEqual(reached, [])

    def test_approved_reaches_paid_tool(self):
        with patch.object(sipi_guard, "evaluate", return_value={"decision": "APPROVED"}):
            self.assertEqual(sipi_guard.guard(1)["decision"], "APPROVED")
