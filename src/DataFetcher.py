import logging
from datetime import datetime
from typing import List, Dict, Optional
from DataBase.DataBaseConnection import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """
    DataFetcher class to retrieve maintenance data from the Innovation Africa database.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize DataFetcher with a DatabaseManager instance.
        
        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.db_manager = db_manager
        
    def fetch_maintenance_data(self) -> List[Dict]:
        """
        Fetch maintenance data from the database using the specified query.
        
        Returns:
            List of dictionaries containing maintenance records with fields:
            - project_id
            - country
            - district
            - zone
            - created_at
            - maintenance_type
            - category
            - issue_severity
            - issue_solved
        """
        query = """
        SELECT
            s.project_id,
            c.name AS country, 
            d.name AS district, 
            p.zone, 
            DATE(s.created_at) AS created_at,
            MAX(CASE WHEN t.task_id = 2006466 THEN t.value END) AS maintenance_type,
            MAX(CASE WHEN t.task_id = 3908936 THEN t.value END) AS category,
            MAX(CASE WHEN t.task_id = 3908947 THEN t.value END) AS issue_severity,
            MAX(CASE WHEN t.task_id = 3908944 THEN t.value END) AS issue_solved
        FROM sections s
        LEFT JOIN projects p ON p.id = s.project_id
        INNER JOIN countries AS c ON c.id = p.country_id
        LEFT JOIN districts AS d ON d.id = p.district_id
        LEFT JOIN tasks t ON s.id = t.section_id
        WHERE s.section_id = 135688 AND p.active = TRUE
        GROUP BY s.id, s.created_at
        HAVING maintenance_type IS NOT NULL
           AND maintenance_type != ''
           AND issue_solved != 'true'
        """
        
        try:
            logger.info("Fetching maintenance data from database...")
            results = self.db_manager.execute_query(query)
            
            if isinstance(results, list):
                logger.info(f"Successfully fetched {len(results)} maintenance records")
                # Convert date objects to strings for JSON serialization if needed
                for record in results:
                    if 'created_at' in record and record['created_at']:
                        if isinstance(record['created_at'], datetime):
                            record['created_at'] = record['created_at'].strftime('%Y-%m-%d')
                        elif hasattr(record['created_at'], 'isoformat'):
                            record['created_at'] = record['created_at'].isoformat()
                return results
            else:
                logger.warning("Query returned unexpected result type")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching maintenance data: {e}")
            raise
    
    def fetch_maintenance_data_filtered(self, 
                                       country: Optional[str] = None,
                                       district: Optional[str] = None,
                                       severity: Optional[str] = None) -> List[Dict]:
        """
        Fetch maintenance data with optional filters.
        
        Args:
            country: Filter by country name
            district: Filter by district name
            severity: Filter by issue severity
            
        Returns:
            Filtered list of maintenance records
        """
        # First get all data
        data = self.fetch_maintenance_data()
        
        # Apply filters
        if country:
            data = [record for record in data if record.get('country') == country]
            
        if district:
            data = [record for record in data if record.get('district') == district]
            
        if severity:
            data = [record for record in data if record.get('issue_severity') == severity]
            
        logger.info(f"Filtered data: {len(data)} records match the criteria")
        return data
    
    def get_summary_statistics(self) -> Dict:
        """
        Get summary statistics of the maintenance data.
        
        Returns:
            Dictionary containing summary statistics
        """
        data = self.fetch_maintenance_data()
        
        if not data:
            return {
                'total_records': 0,
                'countries': [],
                'severity_counts': {},
                'maintenance_types': []
            }
        
        # Calculate statistics
        countries = list(set(record.get('country') for record in data if record.get('country')))
        severity_counts = {}
        maintenance_types = list(set(record.get('maintenance_type') for record in data if record.get('maintenance_type')))
        
        for record in data:
            severity = record.get('issue_severity', 'Unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'total_records': len(data),
            'countries': countries,
            'severity_counts': severity_counts,
            'maintenance_types': maintenance_types,
            'districts': list(set(record.get('district') for record in data if record.get('district')))
        }


def main():
    """
    Example usage of the DataFetcher class
    """
    # Database configuration (same as in DataBaseConnection.py)
    KEY_VAULT_URL = "https://innovation-africa-kv.vault.azure.net/"
    SECRET_NAME = "database-password"
    HOST = "104.248.128.21"
    PORT = 3306
    DATABASE = "innovationAfrica"
    USERNAME = "hackathon"
    
    try:
        # Initialize database manager and data fetcher
        with DatabaseManager(KEY_VAULT_URL, SECRET_NAME, HOST, PORT, DATABASE, USERNAME) as db_manager:
            fetcher = DataFetcher(db_manager)
            
            # Fetch all maintenance data
            print("\n=== Fetching Maintenance Data ===")
            maintenance_data = fetcher.fetch_maintenance_data()
            
            if maintenance_data:
                print(f"\nTotal records fetched: {len(maintenance_data)}")
                
                # Display first few records
                print("\n=== Sample Records ===")
                for i, record in enumerate(maintenance_data[:3], 1):
                    print(f"\nRecord {i}:")
                    print(f"  Project ID: {record.get('project_id')}")
                    print(f"  Country: {record.get('country')}")
                    print(f"  District: {record.get('district')}")
                    print(f"  Zone: {record.get('zone')}")
                    print(f"  Created: {record.get('created_at')}")
                    print(f"  Maintenance Type: {record.get('maintenance_type')}")
                    print(f"  Category: {record.get('category')}")
                    print(f"  Severity: {record.get('issue_severity')}")
                    print(f"  Solved: {record.get('issue_solved')}")
                
                # Get summary statistics
                print("\n=== Summary Statistics ===")
                stats = fetcher.get_summary_statistics()
                print(f"Total Records: {stats['total_records']}")
                print(f"Countries: {', '.join(stats['countries'])}")
                print(f"Severity Distribution: {stats['severity_counts']}")
                print(f"Maintenance Types: {', '.join(stats['maintenance_types'][:5])}...")  # Show first 5
                
                # Example of filtered data
                print("\n=== Filtered Data Example ===")
                # You can uncomment and modify these based on actual data
                # filtered_data = fetcher.fetch_maintenance_data_filtered(severity='High')
                # print(f"High severity issues: {len(filtered_data)} records")
                
            else:
                print("No maintenance data found matching the criteria")
                
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
