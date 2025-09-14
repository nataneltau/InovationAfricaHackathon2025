import os
import pymysql
from azure.keyvault.secrets import SecretClient
from azure.identity import InteractiveBrowserCredential, ClientSecretCredential
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, key_vault_url, secret_name, host, port, database, username):
        self.key_vault_url = key_vault_url
        self.secret_name = secret_name
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.connection = None
        
    def get_credential(self):
        try:
            return InteractiveBrowserCredential()
        except Exception as e:
            logger.error(f"Failed to get interactive credential: {e}")
            tenant_id = os.getenv('AZURE_TENANT_ID')
            client_id = os.getenv('AZURE_CLIENT_ID')
            client_secret = os.getenv('AZURE_CLIENT_SECRET')
            if tenant_id and client_id and client_secret:
                return ClientSecretCredential(tenant_id, client_id, client_secret)
            raise Exception("No valid Azure credentials found")
    
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
        try:
            if self.connection and self.connection.open:
                return self.connection
            
            password = self.get_password_from_keyvault()
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=password,
                database=self.database,
                ssl={"ssl": {}},  # Required for Azure-hosted MySQL
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info(f"Connected to MySQL database {self.database} at {self.host}:{self.port}")
            return self.connection
        except Exception as e:
            logger.error(f"Error while connecting to MySQL: {e}")
            raise
    
    def execute_query(self, query, params=None):
        try:
            conn = self.connect_to_database()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith("SELECT"):
                    results = cursor.fetchall()
                    logger.info(f"Retrieved {len(results)} rows.")
                    return results
                else:
                    conn.commit()
                    logger.info(f"Affected rows: {cursor.rowcount}")
                    return None
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    def close_connection(self):
        try:
            if self.connection and self.connection.open:
                self.connection.close()
                logger.info("MySQL connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
    
    def __enter__(self):
        self.connect_to_database()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()


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
            print("\nAvailable tables:")
            for table in tables:
                print(f"  - {list(table.values())[0]}")
            
            # Example fetch
            rows = db.execute_query("SELECT * FROM locations LIMIT 5")
            print("\nSample rows from locations:")
            for row in rows:
                print(row)
    except Exception as e:
        logger.error(f"Application error: {e}")


if __name__ == "__main__":
    main()
