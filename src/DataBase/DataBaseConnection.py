import os
import pymysql
import logging
from azure.keyvault.secrets import SecretClient
from azure.identity import InteractiveBrowserCredential, ClientSecretCredential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Simple DB manager that retrieves the DB password from Azure Key Vault,
    keeps a PyMySQL connection open for reuse, and returns query results
    (list of dicts) when the statement produces rows; otherwise returns the
    number of affected rows (int).
    """

    def __init__(self, key_vault_url, secret_name, host, port, database, username):
        self.key_vault_url = key_vault_url
        self.secret_name = secret_name
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.connection = None

    def get_credential(self):
        # Try interactive browser credential first (works for local dev)
        try:
            return InteractiveBrowserCredential()
        except Exception:
            tenant_id = os.getenv("AZURE_TENANT_ID")
            client_id = os.getenv("AZURE_CLIENT_ID")
            client_secret = os.getenv("AZURE_CLIENT_SECRET")
            if tenant_id and client_id and client_secret:
                return ClientSecretCredential(tenant_id, client_id, client_secret)
            raise Exception("No valid Azure credentials found for Key Vault access")

    def get_password_from_keyvault(self):
        try:
            credential = self.get_credential()
            client = SecretClient(vault_url=self.key_vault_url, credential=credential)
            secret = client.get_secret(self.secret_name)
            logger.info("Successfully retrieved password from Key Vault")
            return secret.value
        except Exception as e:
            logger.error(f"Failed to retrieve password from Key Vault: {e}")
            raise

    def connect_to_database(self):
        # Return existing open connection if available
        try:
            if self.connection and getattr(self.connection, "open", False):
                return self.connection

            password = self.get_password_from_keyvault()
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=password,
                database=self.database,
                ssl={"ssl": {}},  # keep if your server requires SSL (Azure)
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )

            try:
                server_info = self.connection.get_server_info()
            except Exception:
                server_info = "unknown"
            logger.info(f"Connected to MySQL database {self.database} at {self.host}:{self.port} (server info: {server_info})")
            return self.connection

        except Exception as e:
            logger.error(f"Error while connecting to MySQL: {e}")
            raise

    def execute_query(self, query, params=None):
        """
        Execute a SQL query. If the statement produces rows (cursor.description is present),
        returns a list of dict rows. Otherwise commits and returns the affected row count (int).
        """
        conn = None
        try:
            conn = self.connect_to_database()
            with conn.cursor() as cursor:
                cursor.execute(query, params)

                # If the statement produced a result set, fetch rows
                if cursor.description:
                    results = cursor.fetchall()  # list of dicts because of DictCursor
                    logger.info(f"Query executed successfully. Retrieved {len(results)} rows.")
                    return results

                # No result set: commit and return affected rows
                conn.commit()
                logger.info(f"Query executed successfully. Affected rows: {cursor.rowcount}")
                return cursor.rowcount

        except Exception as e:
            # Keep logging concise and re-raise so callers can handle it
            logger.error(f"Error executing query: {e}")
            raise

    def close_connection(self):
        try:
            if self.connection and getattr(self.connection, "open", False):
                self.connection.close()
                logger.info("MySQL connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")

    def __enter__(self):
        self.connect_to_database()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()


# Example usage for scripts that import this module:
def main():
    KEY_VAULT_URL = "https://innovation-africa-kv.vault.azure.net/"
    SECRET_NAME = "database-password"
    HOST = "104.248.128.21"
    PORT = 3306
    DATABASE = "innovationAfrica"
    USERNAME = "hackathon"

    try:
        with DatabaseManager(KEY_VAULT_URL, SECRET_NAME, HOST, PORT, DATABASE, USERNAME) as db:
            tables = db.execute_query("SHOW TABLES")
            if isinstance(tables, list) and tables:
                print("\nAvailable tables:")
                for table in tables:
                    # table is a dict like {'Tables_in_innovationAfrica': 'locations'}
                    first_val = next(iter(table.values()))
                    print(f"  - {first_val}")
            else:
                print("No tables returned or zero rows.")

            # Example SELECT usage
            rows = db.execute_query("SELECT * FROM locations LIMIT 5")
            if isinstance(rows, list):
                print("\nSample rows from locations:")
                for r in rows:
                    print(r)
            else:
                print(f"SELECT returned non-list value: {rows}")

    except Exception as e:
        logger.error(f"Application error: {e}")

if __name__ == "__main__":
    main()
