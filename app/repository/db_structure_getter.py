import asyncio
from sqlalchemy import inspect
from app.db.session import engine
from sqlalchemy import text


async def show_db_structure():
    async with engine.begin() as conn:
        def get_structure(sync_conn):
            inspector = inspect(sync_conn)
            tables_info = {}
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                tables_info[table_name] = [
                    {"name": col["name"], "type": str(col["type"])}
                    for col in columns
                ]
            return tables_info

        structure = await conn.run_sync(get_structure)

        for table, columns in structure.items():
            print(f"Table: {table}")
            for column in columns:
                print(f"  - {column['name']} ({column['type']})")
            print()

asyncio.run(show_db_structure())