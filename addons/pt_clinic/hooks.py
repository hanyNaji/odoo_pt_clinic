TRANSLATED_CHAR_COLUMNS = (
    ("pt_clinic_dashboard", "name"),
    ("pt_branch", "name"),
)


def _get_cursor(cr_or_env):
    return getattr(cr_or_env, "cr", cr_or_env)


def migrate_translated_char_columns(cr_or_env):
    """Convert legacy translated Char columns to jsonb storage.

    Odoo 19 reads translated Char fields with PostgreSQL's jsonb operators. Existing
    databases that were created before the fields became translatable can still have
    varchar columns, which makes form loading fail with ``operator does not exist:
    character varying ->> unknown``. Keep this migration hook small and idempotent so
    it can safely run during install, upgrade, and model initialization.
    """
    cr = _get_cursor(cr_or_env)
    for table_name, column_name in TRANSLATED_CHAR_COLUMNS:
        cr.execute(
            """
            SELECT udt_name
              FROM information_schema.columns
             WHERE table_name = %s
               AND column_name = %s
            """,
            (table_name, column_name),
        )
        column_info = cr.fetchone()
        if column_info and column_info[0] != "jsonb":
            cr.execute(
                f'''
                ALTER TABLE "{table_name}"
                ALTER COLUMN "{column_name}" TYPE jsonb
                USING CASE
                    WHEN "{column_name}" IS NULL THEN NULL
                    ELSE jsonb_build_object('en_US', "{column_name}"::text)
                END
                '''
            )


def pre_init_hook(cr_or_env):
    migrate_translated_char_columns(cr_or_env)
