import os
import tempfile
import unittest
from pathlib import Path
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
        self.assertIn("Apply for the paid implementation pilot", html)
        self.assertIn("Run a free live check", html)
        self.assertNotIn("Get access</button>", html)

    def test_paid_pilot_page_has_one_fixed_scope_application_path(self):
        html = templates.pilot_html()

        self.assertIn("Paid implementation pilot", html)
        self.assertIn("one real agent workflow", html.lower())
        self.assertIn("This is not a free beta", html)
        self.assertIn('action="/api/pilot-applications"', html)
        self.assertIn('name="company"', html)
        self.assertIn('name="email"', html)
        self.assertIn('name="agent_stack"', html)
        self.assertIn('name="primary_risk"', html)
        self.assertNotIn("AgentShield Starter Kit", html)

    def test_homepage_and_pricing_prioritize_the_paid_pilot(self):
        homepage = templates.landing_page_html()
        pricing = templates.pricing_html()

        self.assertIn('href="/pilot" class="btn"', homepage)
        self.assertIn("Apply for the paid implementation pilot", homepage)
        self.assertIn('href="/pilot"', pricing)
        self.assertIn("Want us to implement the spend controls?", pricing)

    def test_buyer_facing_pages_do_not_claim_an_unverified_founder_loss(self):
        pages = "\n".join((
            templates.landing_page_html(),
            templates.blog_page_html(),
            templates.masterclass_html(),
        ))

        for unverified_claim in (
            "loss that inspired sipi.bot",
            "my own AI agent spent",
            "I woke up to Stripe notifications",
            "what happened when I shipped my first agent",
        ):
            self.assertNotIn(unverified_claim, pages)

    def test_homepage_keeps_measured_portfolio_cross_promo(self):
        html = templates.landing_page_html()

        self.assertEqual(html.count('data-portfolio-cross-promo="v1"'), 1)
        self.assertEqual(html.count("utm_source=sipi.bot"), 9)
        for domain in (
            "sipiteno.com",
            "gitdealflow.com",
            "signals.gitdealflow.com",
            "invisibleexit.com",
            "unlocksaas.com",
            "voicelogpro.com",
            "carshake.online",
            "churnlens.site",
            "sanctionsai.dev",
        ):
            self.assertIn(f"https://{domain}/?utm_source=sipi.bot", html)

    def test_success_page_guides_activation(self):
        html = templates.key_success_html({"key": "sk_live_test", "tier": "team"})

        self.assertIn("Save the key", html)
        self.assertIn("Protect the first spend", html)
        self.assertIn("Choose my integration", html)
        self.assertNotIn("api_key_copied", html)
        self.assertNotIn("checkout_success_viewed", html)
        self.assertNotIn("posthog", html.lower())
        self.assertIn("history.replaceState", html)

    def test_legacy_email_how_it_works_route_redirects_to_live_developer_guide(self):
        api_source = (Path(__file__).parents[1] / "spendfirewall" / "api.py").read_text()
        self.assertIn('if path == "/how-it-works":', api_source)
        self.assertIn('self._redirect_301("/for/ai-developers")', api_source)


if __name__ == "__main__":
    unittest.main()
