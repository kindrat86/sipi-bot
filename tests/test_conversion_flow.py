import os
import tempfile
import unittest
from unittest import mock

from spendfirewall import billing, templates


class CheckoutConversionTests(unittest.TestCase):
    def test_checkout_session_uses_sipibot_branding_and_reassurance(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "billing.db")
            captured = {}

            def fake_stripe_post(path, data, api_version=None):
                captured.update(
                    path=path,
                    data=data,
                    api_version=api_version,
                )
                return {
                    "id": "cs_test_conversion",
                    "url": "https://checkout.stripe.test/session",
                }

            env = {
                "STRIPE_SECRET_KEY": "sk_test_example",
                "STRIPE_PRICE_TEAM": "price_team",
                "PUBLIC_URL": "https://sipi.bot",
            }
            with mock.patch.dict(os.environ, env, clear=False), \
                    mock.patch.object(billing, "_DB", db_path), \
                    mock.patch.object(billing, "_stripe_post", side_effect=fake_stripe_post):
                url = billing.create_checkout_session("team")

        self.assertEqual(url, "https://checkout.stripe.test/session")
        self.assertEqual(captured["path"], "/checkout/sessions")
        self.assertEqual(captured["api_version"], "2025-09-30.clover")
        self.assertEqual(captured["data"]["branding_settings[display_name]"], "sipi.bot")
        self.assertEqual(captured["data"]["branding_settings[button_color]"], "#00D4AA")
        self.assertEqual(
            captured["data"]["branding_settings[icon][url]"],
            "https://sipi.bot/favicon.svg",
        )
        self.assertIn("API key is issued immediately", captured["data"]["custom_text[submit][message]"])
        self.assertEqual(
            captured["data"]["success_url"],
            "https://sipi.bot/keys/{CHECKOUT_SESSION_ID}",
        )
        self.assertNotIn("client_reference_id", captured["data"])

    def test_pricing_leads_with_team_and_keeps_free_path_secondary(self):
        html = templates.pricing_html()
        team = html.index("Team · recommended")
        playground = html.index(">Playground<")
        business = html.index(">Business<")

        self.assertLess(team, playground)
        self.assertLess(playground, business)
        self.assertIn("API key issued immediately after payment", html)
        self.assertIn("Start Team — $99/mo", html)

    def test_homepage_exposes_focused_actions_before_long_form_content(self):
        html = templates.landing_page_html()
        actions = html.index('class="hero-actions"')
        first_code_example = html.index("<!-- TRY IT NOW -->")

        self.assertLess(actions, first_code_example)
        self.assertIn("Protect my agent — see plans", html)
        self.assertIn("Run a free live check", html)
        self.assertNotIn("Get access</button>", html)

    def test_success_page_guides_activation(self):
        html = templates.key_success_html({"key": "sk_live_test", "tier": "team"})

        self.assertIn("Save the key", html)
        self.assertIn("Protect the first spend", html)
        self.assertIn("Choose my integration", html)
        self.assertNotIn("api_key_copied", html)
        self.assertNotIn("checkout_success_viewed", html)
        self.assertNotIn("posthog", html.lower())
        self.assertIn("history.replaceState", html)


if __name__ == "__main__":
    unittest.main()
