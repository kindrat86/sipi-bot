(function () {
  "use strict";

  var CONSENT_KEY = "sipi_analytics_consent";
  var POSTHOG_KEY = "phc_lyZCgvTpicjLzAO3rY2GhxuX5WUc5jQjP8ZVwwJqauX";
  var POSTHOG_HOST = "https://eu.i.posthog.com";
  var pending = [];
  var loading = false;

  function consent() {
    try {
      return window.localStorage.getItem(CONSENT_KEY);
    } catch (_) {
      return null;
    }
  }

  function saveConsent(value) {
    try {
      window.localStorage.setItem(CONSENT_KEY, value);
    } catch (_) {}
  }

  function safeProperties(properties) {
    var allowed = {};
    var source = properties || {};
    Object.keys(source).slice(0, 20).forEach(function (key) {
      var value = source[key];
      if (
        /^[a-z0-9_$-]{1,48}$/i.test(key) &&
        (typeof value === "string" ||
          typeof value === "number" ||
          typeof value === "boolean") &&
        String(value).length <= 160
      ) {
        allowed[key] = value;
      }
    });
    allowed.schema_version = 1;
    return allowed;
  }

  window.sipiTrack = function (event, properties) {
    if (!/^[a-z0-9_$-]{1,64}$/i.test(event || "")) return;
    if (consent() === "denied") return;
    var item = [event, safeProperties(properties)];
    if (window.posthog && window.posthog.__loaded) {
      window.posthog.capture(item[0], item[1]);
      return;
    }
    if (pending.length < 50) pending.push(item);
  };

  function flush() {
    if (!(window.posthog && window.posthog.capture)) return;
    while (pending.length) {
      var item = pending.shift();
      window.posthog.capture(item[0], item[1]);
    }
  }

  function loadAnalytics() {
    if (loading || consent() !== "granted") return;
    loading = true;
    var script = document.createElement("script");
    var source = POSTHOG_HOST + "/static/array.js";
    if (window.trustedTypes && window.trustedTypes.createPolicy) {
      try {
        var policy = window.trustedTypes.createPolicy("sipi-analytics", {
          createScriptURL: function (value) {
            return value;
          },
        });
        source = policy.createScriptURL(source);
      } catch (_) {}
    }
    script.src = source;
    script.defer = true;
    script.crossOrigin = "anonymous";
    script.onload = function () {
      window.posthog.init(POSTHOG_KEY, {
        api_host: POSTHOG_HOST,
        autocapture: false,
        capture_pageview: false,
        capture_pageleave: false,
        disable_session_recording: true,
        person_profiles: "never",
        persistence: "localStorage+cookie",
      });
      flush();
    };
    script.onerror = function () {
      loading = false;
    };
    document.head.appendChild(script);
  }

  function removePrompt() {
    var prompt = document.getElementById("sipi-consent");
    if (prompt) prompt.remove();
  }

  function choose(value) {
    saveConsent(value);
    removePrompt();
    if (value === "granted") {
      if (window.posthog && window.posthog.opt_in_capturing) {
        window.posthog.opt_in_capturing();
        flush();
      } else {
        loadAnalytics();
      }
    } else {
      pending.length = 0;
      if (window.posthog && window.posthog.opt_out_capturing) {
        window.posthog.opt_out_capturing();
      }
    }
  }

  function button(label, className, onClick) {
    var element = document.createElement("button");
    element.type = "button";
    element.className = className;
    element.textContent = label;
    element.addEventListener("click", onClick);
    return element;
  }

  function showPrompt() {
    if (document.getElementById("sipi-consent")) return;
    var panel = document.createElement("section");
    panel.id = "sipi-consent";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "Analytics preferences");

    var text = document.createElement("p");
    text.textContent =
      "May we use anonymous product analytics to improve sipi.bot? No advertising or session recording.";
    var privacy = document.createElement("a");
    privacy.href = "/privacy";
    privacy.textContent = " Privacy details";
    text.appendChild(privacy);

    var actions = document.createElement("div");
    actions.appendChild(
      button("No thanks", "sipi-consent-secondary", function () {
        choose("denied");
      })
    );
    actions.appendChild(
      button("Allow analytics", "sipi-consent-primary", function () {
        choose("granted");
      })
    );
    panel.appendChild(text);
    panel.appendChild(actions);
    document.body.appendChild(panel);
  }

  function installPreferencesButton() {
    if (document.getElementById("sipi-privacy-choices")) return;
    var preferences = button("Privacy choices", "", showPrompt);
    preferences.id = "sipi-privacy-choices";
    document.body.appendChild(preferences);
  }

  function installContextualConversion() {
    if (document.querySelector("[data-sipi-conversion]")) return;
    var path = window.location.pathname;
    var config = null;
    if (/^\/(for|integrations)\//.test(path) || path === "/for/") {
      config = {
        family: "integration",
        title: "Use this integration with a production policy",
        body: "Test the live firewall, then issue a hosted key for persistent rules and audit history.",
        primary: ["Run a live transaction", "/playground/?from=integration"],
        secondary: ["Get a production key", "/pricing?from=integration"],
      };
    } else if (/^\/(vs|compare|alternatives|alternatives-to)\//.test(path)) {
      config = {
        family: "comparison",
        title: "Ready to put a real control before the spend?",
        body: "Team includes unlimited evaluations, every rule type, the approval queue, and persistent audit history.",
        primary: ["See Team pricing", "/pricing?from=comparison"],
        secondary: ["Try the firewall first", "/playground/?from=comparison"],
      };
    } else if (/^\/(learn|guides|faq|glossary|tutorials|how-to)\//.test(path)) {
      config = {
        family: "education",
        title: "Turn the guide into a live decision",
        body: "Run a transaction through the production rules engine—no signup, install, or card.",
        primary: ["Run a live check", "/playground/?from=education"],
        secondary: ["See hosted plans", "/pricing?from=education"],
      };
    }
    if (!config) return;

    var section = document.createElement("section");
    section.className = "sipi-contextual-conversion";
    section.dataset.sipiConversion = config.family;
    var heading = document.createElement("h2");
    heading.textContent = config.title;
    var paragraph = document.createElement("p");
    paragraph.textContent = config.body;
    var actions = document.createElement("div");
    [config.primary, config.secondary].forEach(function (entry, index) {
      var link = document.createElement("a");
      link.href = entry[1];
      link.textContent = entry[0];
      link.className = index === 0 ? "sipi-context-primary" : "sipi-context-secondary";
      link.addEventListener("click", function () {
        window.sipiTrack("cta_clicked", {
          cta_id: config.family + "_" + (index === 0 ? "primary" : "secondary"),
          destination: entry[1].split("?")[0],
          placement: "contextual_footer",
          page_family: config.family,
        });
      });
      actions.appendChild(link);
    });
    section.appendChild(heading);
    section.appendChild(paragraph);
    section.appendChild(actions);
    var footer = document.querySelector("footer");
    if (footer) {
      footer.parentNode.insertBefore(section, footer);
    } else {
      document.body.appendChild(section);
    }
  }

  var style = document.createElement("style");
  style.textContent =
    "#sipi-consent{position:fixed;z-index:2147483646;left:16px;right:16px;bottom:16px;max-width:620px;margin:auto;padding:16px 18px;background:#121316;color:#e8e8ea;border:1px solid #34363d;border-radius:14px;box-shadow:0 16px 48px rgba(0,0,0,.45);font:14px/1.5 system-ui,sans-serif}" +
    "#sipi-consent p{margin:0 0 12px;color:#c9ccd3}#sipi-consent a{color:#00d4aa}" +
    "#sipi-consent div{display:flex;justify-content:flex-end;gap:8px;flex-wrap:wrap}" +
    "#sipi-consent button,#sipi-privacy-choices{min-height:40px;border-radius:9px;padding:8px 14px;font-weight:700;cursor:pointer}" +
    ".sipi-consent-primary{border:1px solid #00d4aa;background:#00d4aa;color:#04120e}" +
    ".sipi-consent-secondary{border:1px solid #34363d;background:transparent;color:#e8e8ea}" +
    "#sipi-privacy-choices{position:fixed;z-index:2147483645;right:10px;bottom:10px;border:1px solid #34363d;background:#121316;color:#c9ccd3;font:12px system-ui,sans-serif;opacity:.86}" +
    "#sipi-privacy-choices:focus-visible,#sipi-consent button:focus-visible{outline:3px solid rgba(0,212,170,.55);outline-offset:2px}" +
    ".sipi-contextual-conversion{max-width:900px;margin:48px auto;padding:28px 24px;background:#121316;color:#e8e8ea;border:1px solid #34363d;border-radius:16px;text-align:center;font:16px/1.55 system-ui,sans-serif}" +
    ".sipi-contextual-conversion h2{margin:0 0 8px;font-size:clamp(22px,4vw,30px)}.sipi-contextual-conversion p{margin:0 auto 18px;max-width:660px;color:#aeb1b8}" +
    ".sipi-contextual-conversion div{display:flex;justify-content:center;gap:10px;flex-wrap:wrap}.sipi-contextual-conversion a{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:11px 18px;border-radius:10px;font-weight:700;text-decoration:none}" +
    ".sipi-context-primary{background:#00d4aa;color:#04120e}.sipi-context-secondary{border:1px solid #34363d;color:#e8e8ea}";
  document.head.appendChild(style);

  window.sipiTrack("$pageview", {
    page_path: window.location.pathname,
    viewport_width: window.innerWidth,
    viewport_height: window.innerHeight,
  });
  document.addEventListener("click", function (event) {
    var link = event.target && event.target.closest
      ? event.target.closest('a[href^="/checkout/"]')
      : null;
    if (
      !link ||
      consent() !== "granted" ||
      !(window.posthog && window.posthog.get_distinct_id)
    ) {
      return;
    }
    var distinctId = String(window.posthog.get_distinct_id() || "");
    if (!/^[A-Za-z0-9._:@-]{1,128}$/.test(distinctId)) return;
    var destination = new URL(link.href, window.location.origin);
    destination.searchParams.set("aid", distinctId);
    link.href = destination.pathname + destination.search + destination.hash;
  });
  installContextualConversion();
  installPreferencesButton();

  if (navigator.doNotTrack === "1") {
    choose("denied");
  } else if (consent() === "granted") {
    loadAnalytics();
  } else if (consent() !== "denied") {
    showPrompt();
  }
})();
