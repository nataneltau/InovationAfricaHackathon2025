import os
import pymysql
from azure.keyvault.secrets import SecretClient
from azure.identity import InteractiveBrowserCredential, ClientSecretCredential
from pymysql import Error
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, key_vault_url, secret_name, host, port, database, username):
        """
        Initialize the DatabaseManager with Azure Key Vault and MySQL connection details
        
        Args:
            key_vault_url (str): Azure Key Vault URL
            secret_name (str): Name of the secret containing the database password
            host (str): Database host
            port (int): Database port
            database (str): Database name
            username (str): Database username
        """
        self.key_vault_url = key_vault_url
        self.secret_name = secret_name
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.connection = None
        
    def get_credential(self):
        """
        Get Azure credential for Key Vault access
        Returns DefaultAzureCredential which works with multiple authentication methods
        """
        try:
            # Try DefaultAzureCredential first (works with managed identity, Azure CLI, etc.)
            credential = InteractiveBrowserCredential()
            return credential
        except Exception as e:
            logger.error(f"Failed to get default credential: {e}")
            
            # Fallback to ClientSecretCredential if environment variables are set
            tenant_id = os.getenv('AZURE_TENANT_ID')
            client_id = os.getenv('AZURE_CLIENT_ID')
            client_secret = os.getenv('AZURE_CLIENT_SECRET')
            
            if tenant_id and client_id and client_secret:
                return ClientSecretCredential(tenant_id, client_id, client_secret)
            else:
                raise Exception("No valid Azure credentials found")
    
    def get_password_from_keyvault(self):
        """
        Retrieve password from Azure Key Vault
        
        Returns:
            str: Database password
        """
        try:
            credential = self.get_credential()
            client = SecretClient(vault_url=self.key_vault_url, credential=credential)
            
            # Retrieve the secret
            secret = client.get_secret(self.secret_name)
            logger.info("Successfully retrieved password from Key Vault")
            return secret.value
            
        except Exception as e:
            logger.error(f"Failed to retrieve password from Key Vault: {e}")
            raise
    
    def connect_to_database(self):
        """
        Connect to MySQL database using credentials from Key Vault
        
        Returns:
            mysql.connector.connection: Database connection object
        """
        try:
            # Get password from Key Vault
            password = self.get_password_from_keyvault()
            print(password)
            # Create database connection
            self.connection = pymysql.connect(
                host="104.248.128.21",
                port=3306,
                database="innovationAfrica", 
                user="hackathon",
                password=password,
                ssl={"ssl": {}},   # if you’re connecting with SSL from Azure/MySQL Cloud
            )
            print("hi")
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM locations limit 10")

            for row in cursor.fetchall():
                print(row)

            self.connection.close()
            
            if self.connection.is_connected():
                db_info = self.connection.get_server_info()
                logger.info(f"Successfully connected to MySQL Server version {db_info}")
                logger.info(f"Connected to database: {self.database}")
                return self.connection
            
        except Error as e:
            logger.error(f"Error while connecting to MySQL: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    def execute_query(self, query, params=None):
        """
        Execute a SQL query
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Query parameters
            
        Returns:
            list: Query results for SELECT queries, None for other queries
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect_to_database()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            
            # For SELECT queries, fetch results
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                logger.info(f"Query executed successfully. Retrieved {len(results)} rows.")
                return results
            else:
                self.connection.commit()
                logger.info(f"Query executed successfully. Affected rows: {cursor.rowcount}")
                return None
                
        except Error as e:
            logger.error(f"Error executing query: {e}")
            raise
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def close_connection(self):
        """
        Close database connection
        """
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                logger.info("MySQL connection is closed")
        except Error as e:
            logger.error(f"Error closing connection: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect_to_database()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_connection()

def main():
    """
    Main function to demonstrate usage
    """
    # Configuration - your actual Key Vault details
    KEY_VAULT_URL = "https://innovation-africa-kv.vault.azure.net/"
    SECRET_NAME = "database-password"  # Your secret name in Key Vault
    HOST = "104.248.128.21"
    PORT = 3306
    DATABASE = "innovationAfrica"
    USERNAME = "hackathon"
    
    try:
        # Using context manager for automatic connection handling
        with DatabaseManager(KEY_VAULT_URL, SECRET_NAME, HOST, PORT, DATABASE, USERNAME) as db:
            
            # Example queries
            # 1. Show tables
            tables = db.execute_query("SHOW TABLES")
            if tables:
                print("\nAvailable tables:")
                for table in tables:
                    print(f"  - {list(table.values())[0]}")
            
            # 2. Example SELECT query (replace with your actual table)
            # users = db.execute_query("SELECT * FROM users LIMIT 5")
            # if users:
            #     print(f"\nFirst 5 users:")
            #     for user in users:
            #         print(user)
            
            # 3. Example parameterized query
            # user = db.execute_query("SELECT * FROM users WHERE id = %s", (1,))
            # if user:
            #     print(f"\nUser with ID 1: {user[0]}")
            
    except Exception as e:
        logger.error(f"Application error: {e}")

if __name__ == "__main__":
    main()