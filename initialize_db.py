from database.utils import init_database, import_sample_data_to_db

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    
    print("Importing sample data...")
    results = import_sample_data_to_db()
    
    for symbol, count in results.items():
        print(f"Imported {count} records for {symbol}")
    
    print("Database initialization complete.")