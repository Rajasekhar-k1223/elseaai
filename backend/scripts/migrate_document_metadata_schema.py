from sqlalchemy import inspect, text

from app.db.database import engine


def main():
    inspector = inspect(engine.sync_engine)
    if not inspector.has_table("documents"):
        print("Table 'documents' does not exist. Create the database tables first.")
        return

    columns = {column["name"] for column in inspector.get_columns("documents")}
    changes = []

    if "document_type" not in columns:
        changes.append("ALTER TABLE documents ADD COLUMN document_type VARCHAR(50) DEFAULT 'general'")
    if "handwriting_detected" not in columns:
        changes.append("ALTER TABLE documents ADD COLUMN handwriting_detected BOOLEAN DEFAULT FALSE")

    if not changes:
        print("No schema changes required for the documents table.")
        return

    with engine.sync_engine.connect() as conn:
        with conn.begin():
            for sql in changes:
                print(f"Executing: {sql}")
                conn.execute(text(sql))

    print("Document metadata schema migration complete.")


if __name__ == "__main__":
    main()
