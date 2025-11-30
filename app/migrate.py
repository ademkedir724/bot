
import os
import sys
import time
import psycopg2

def run_migrations():
    """Applies database migrations."""
    retries = 10
    while retries > 0:
        try:
            conn = psycopg2.connect(os.environ['DATABASE_URL'])
            cur = conn.cursor()
            with open('migrations/init.sql', 'r') as f:
                cur.execute(f.read())
            conn.commit()
            cur.close()
            conn.close()
            print('--- Database migration successful.')
            return
        except psycopg2.OperationalError as e:
            print(f'DB not ready yet, waiting... ({e})')
            retries -= 1
            time.sleep(3)
        except Exception as e:
            print(f'An unexpected error occurred during migration: {e}', file=sys.stderr)
            sys.exit(1)

    if retries == 0:
        print('Could not connect to database after several retries. Exiting.', file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()
