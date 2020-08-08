import io
import os


def export_all_tables(settings):
    from sqlacodegen.codegen import CodeGenerator
    from sqlalchemy.engine import create_engine
    from sqlalchemy.schema import MetaData

    # Use reflection to fill in the metadata
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    metadata = MetaData(engine)
    metadata.reflect(engine, "public", False, None)

    for _, table_obj in metadata.tables.items():
        metadata.reflect(engine, "public", False, [table_obj.name])
        outfile = io.open(
            os.path.join(settings.MODELS_PATH, f"{table_obj.name}.py"),
            "w",
            encoding="utf-8",
        )
        generator = CodeGenerator(metadata, noclasses=True)
        generator.render(outfile)


def sync(settings, silent: bool = True):
    """
        settings: a framework settings object
    """
    from sqlbag import S, temporary_database as temporary_db
    from migra import Migration

    with open(os.path.join(settings.DDL_PATH, "main.sql"), "r") as f:
        ddl = f.read()

    with temporary_db("postgresql") as TEMP_DB_URL:
        with S(TEMP_DB_URL) as s:
            s.execute(ddl)

        with S(settings.SQLALCHEMY_DATABASE_URI) as s_current, S(
            TEMP_DB_URL
        ) as s_target:
            m = Migration(s_current, s_target)
            m.set_safety(False)
            m.add_all_changes()

            if m.statements:
                print("THE FOLLOWING CHANGES ARE PENDING:", end="\n\n")
                print(m.sql)
                print()
                if (
                    silent
                    or input("Apply these changes (type `yes` to continue)? ")
                    == "yes"
                ):
                    print("Applying...")
                    m.apply()
                else:
                    print("Not applying.")
            else:
                print("Already synced.")
