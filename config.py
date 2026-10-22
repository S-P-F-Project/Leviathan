"""Public settings for the SPF site. Do not put passwords or access tokens here."""

SITE_NAME = "spf-project"
SITE_TAGLINE = "Мир. Персонажи. Истории."
SITE_DESCRIPTION = (
    "SPF — ролевой проект, в котором игроки создают персонажей "
    "и развивают собственные истории."
)

AGE_LIMIT = 18
AGE_COOKIE_NAME = "spf_age_confirmed"

# Relative paths are routed by the web server on the shared domain.
WIKI_URL = "/wiki/"
OFFER_URL = "/wiki/docs/oferta"

# Empty fields are never displayed publicly.
CONTACTS = {
    "email": "",
    "phone": "",
}

# Replace with real seller data before enabling payments.
REQUISITES = {
    "status": "Самозанятый",
    "full_name": "",
    "inn": "",
}

# Navigation only: this is not a health check or an availability indicator.
MICROSERVICES = [
    {"name": "Leviathan", "url": "/", "description": "Главный портал проекта"},
    {"name": "Wiki", "url": WIKI_URL, "description": "Документация и мир SPF"},
]
