"""
NetMap - Dashboard authentication.
"""

import os

from flask import (
    redirect,
    session,
    url_for,
)

from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)


USERNAME = os.getenv(
    "NETMAP_ADMIN_USER",
    "admin",
)

PASSWORD_HASH = os.getenv(
    "NETMAP_ADMIN_PASSWORD_HASH",
)


def configure_default_password() -> str:
    """
    Generate a development password hash.

    Set NETMAP_ADMIN_PASSWORD_HASH for
    persistent deployments.
    """

    password = os.getenv(
        "NETMAP_ADMIN_PASSWORD",
        "changeme",
    )

    return generate_password_hash(
        password
    )


def get_password_hash() -> str:

    if PASSWORD_HASH:
        return PASSWORD_HASH

    return configure_default_password()


def authenticate(
    username: str,
    password: str,
) -> bool:
    """Validate dashboard credentials."""

    if username != USERNAME:
        return False

    return check_password_hash(
        get_password_hash(),
        password,
    )


def login_required():
    """Return redirect response when unauthenticated."""

    if not session.get(
        "authenticated"
    ):
        return redirect(
            url_for("login")
        )

    return None
