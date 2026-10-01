import os
import psycopg2
from django.core.management.base import BaseCommand
from django.core.management import call_command
from dotenv import load_dotenv
from pathlib import Path

class Command(BaseCommand):
    help = 'Creates the PostgreSQL database if it does not exist and runs migrations'

    def handle(self, *args, **options):
        env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
        load_dotenv(env_path)

        db_name = os.getenv('DB_NAME', 'gymmentor_db')
        db_user = os.getenv('DB_USER', 'postgres')
        db_pass = os.getenv('DB_PASSWORD', '')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')

        self.stdout.write(f"Connecting to PostgreSQL at {db_host}:{db_port} as user '{db_user}'...")

        try:
            # Connect to default postgres DB first to create target database
            conn = psycopg2.connect(
                dbname='postgres',
                user=db_user,
                password=db_pass,
                host=db_host,
                port=db_port
            )
            conn.autocommit = True
            cur = conn.cursor()

            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cur.fetchone()

            if not exists:
                cur.execute(f'CREATE DATABASE "{db_name}"')
                self.stdout.write(self.style.SUCCESS(f"[OK] Database '{db_name}' created successfully!"))
            else:
                self.stdout.write(self.style.SUCCESS(f"[OK] Database '{db_name}' already exists."))

            cur.close()
            conn.close()

            # Now run Django migrations
            self.stdout.write("Running migrations on PostgreSQL...")
            call_command('migrate')
            self.stdout.write(self.style.SUCCESS("[OK] All database migrations applied successfully!"))

        except psycopg2.OperationalError as e:
            self.stdout.write(self.style.ERROR(f"PostgreSQL connection error: {e}"))
            self.stdout.write(self.style.WARNING("Please check that DB_PASSWORD, DB_USER, and DB_PORT in your .env file match your local PostgreSQL server installation."))
