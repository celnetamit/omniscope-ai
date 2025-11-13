"""
Data Anonymization Engine for OmniScope AI
Implements PII detection and anonymization for GDPR compliance
"""

import re
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .encryption import hash_data

class AnonymizationService:
    """Service for data anonymization and PII detection"""
    
    # PII detection patterns
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'date_of_birth': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        'postal_code': r'\b\d{5}(?:-\d{4})?\b',
        'passport': r'\b[A-Z]{1,2}\d{6,9}\b',
        'driver_license': r'\b[A-Z]{1,2}\d{5,8}\b',
        'bank_account': r'\b\d{8,17}\b',
        'medical_record': r'\bMRN[-:]?\s*\d{6,10}\b',
        'patient_id': r'\bPID[-:]?\s*\d{6,10}\b',
        'insurance_number': r'\b[A-Z]{2,3}\d{6,10}\b',
        'url': r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
    }
    
    @staticmethod
    def detect_pii(text: str) -> Dict[str, List[str]]:
        """
        Detect PII in text
        
        Args:
            text: Text to scan for PII
        
        Returns:
            Dictionary mapping PII type to list of detected values
        """
        detected = {}
        
        for pii_type, pattern in AnonymizationService.PII_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Handle tuple matches (like phone numbers with groups)
                if isinstance(matches[0], tuple):
                    matches = [''.join(match) for match in matches]
                detected[pii_type] = matches
        
        return detected
    
    @staticmethod
    def hash_anonymize(value: str, salt: Optional[str] = None) -> str:
        """
        Anonymize data using hashing
        
        Args:
            value: Value to anonymize
            salt: Optional salt for hashing
        
        Returns:
            Hashed value
        """
        if salt:
            value = f"{value}{salt}"
        return hash_data(value)
    
    @staticmethod
    def mask_anonymize(value: str, mask_char: str = '*', visible_chars: int = 4) -> str:
        """
        Anonymize data using masking
        
        Args:
            value: Value to anonymize
            mask_char: Character to use for masking
            visible_chars: Number of characters to keep visible at the end
        
        Returns:
            Masked value
        """
        if len(value) <= visible_chars:
            return mask_char * len(value)
        
        masked_length = len(value) - visible_chars
        return mask_char * masked_length + value[-visible_chars:]
    
    @staticmethod
    def generalize_date(date_str: str, precision: str = 'month') -> str:
        """
        Generalize date to reduce precision
        
        Args:
            date_str: Date string to generalize
            precision: Level of precision ('year', 'month', 'day')
        
        Returns:
            Generalized date string
        """
        try:
            # Try to parse date
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                return date_str  # Return original if can't parse
            
            if precision == 'year':
                return str(date.year)
            elif precision == 'month':
                return f"{date.year}-{date.month:02d}"
            else:
                return date.strftime('%Y-%m-%d')
        except:
            return date_str
    
    @staticmethod
    def generalize_age(age: int, bin_size: int = 5) -> str:
        """
        Generalize age into bins
        
        Args:
            age: Age to generalize
            bin_size: Size of age bins
        
        Returns:
            Age range string (e.g., "25-30")
        """
        lower = (age // bin_size) * bin_size
        upper = lower + bin_size
        return f"{lower}-{upper}"
    
    @staticmethod
    def generalize_location(location: str, level: str = 'state') -> str:
        """
        Generalize location to reduce precision
        
        Args:
            location: Location string
            level: Level of generalization ('country', 'state', 'city')
        
        Returns:
            Generalized location
        """
        # Simple implementation - can be enhanced with geocoding
        parts = location.split(',')
        
        if level == 'country' and len(parts) > 0:
            return parts[-1].strip()
        elif level == 'state' and len(parts) > 1:
            return ', '.join(parts[-2:]).strip()
        else:
            return location
    
    @staticmethod
    def anonymize_text(
        text: str,
        method: str = 'mask',
        pii_types: Optional[List[str]] = None
    ) -> str:
        """
        Anonymize PII in text
        
        Args:
            text: Text to anonymize
            method: Anonymization method ('mask', 'hash', 'remove')
            pii_types: List of PII types to anonymize (None = all)
        
        Returns:
            Anonymized text
        """
        detected_pii = AnonymizationService.detect_pii(text)
        
        anonymized_text = text
        
        for pii_type, values in detected_pii.items():
            # Skip if not in specified types
            if pii_types and pii_type not in pii_types:
                continue
            
            for value in values:
                if method == 'mask':
                    replacement = AnonymizationService.mask_anonymize(value)
                elif method == 'hash':
                    replacement = AnonymizationService.hash_anonymize(value)
                elif method == 'remove':
                    replacement = f"[{pii_type.upper()}_REMOVED]"
                else:
                    replacement = f"[{pii_type.upper()}]"
                
                anonymized_text = anonymized_text.replace(value, replacement)
        
        return anonymized_text
    
    @staticmethod
    def anonymize_dataset(
        data: Dict[str, Any],
        field_config: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Anonymize a dataset based on field configuration
        
        Args:
            data: Dataset to anonymize
            field_config: Configuration for each field
                Example: {
                    'email': {'method': 'hash'},
                    'age': {'method': 'generalize', 'bin_size': 5},
                    'date_of_birth': {'method': 'generalize', 'precision': 'year'}
                }
        
        Returns:
            Anonymized dataset
        """
        anonymized_data = data.copy()
        
        for field, config in field_config.items():
            if field not in anonymized_data:
                continue
            
            value = anonymized_data[field]
            method = config.get('method', 'mask')
            
            if method == 'hash':
                anonymized_data[field] = AnonymizationService.hash_anonymize(str(value))
            elif method == 'mask':
                visible_chars = config.get('visible_chars', 4)
                anonymized_data[field] = AnonymizationService.mask_anonymize(
                    str(value),
                    visible_chars=visible_chars
                )
            elif method == 'generalize':
                if 'bin_size' in config:
                    # Age generalization
                    anonymized_data[field] = AnonymizationService.generalize_age(
                        int(value),
                        config['bin_size']
                    )
                elif 'precision' in config:
                    # Date generalization
                    anonymized_data[field] = AnonymizationService.generalize_date(
                        str(value),
                        config['precision']
                    )
                elif 'level' in config:
                    # Location generalization
                    anonymized_data[field] = AnonymizationService.generalize_location(
                        str(value),
                        config['level']
                    )
            elif method == 'remove':
                anonymized_data[field] = None
        
        return anonymized_data
    
    @staticmethod
    def k_anonymity_check(
        dataset: List[Dict[str, Any]],
        quasi_identifiers: List[str],
        k: int = 5
    ) -> bool:
        """
        Check if dataset satisfies k-anonymity
        
        Args:
            dataset: List of records
            quasi_identifiers: List of quasi-identifier fields
            k: Minimum group size for k-anonymity
        
        Returns:
            True if dataset satisfies k-anonymity
        """
        # Group records by quasi-identifier values
        groups = {}
        
        for record in dataset:
            # Create key from quasi-identifiers
            key = tuple(record.get(qi) for qi in quasi_identifiers)
            
            if key not in groups:
                groups[key] = []
            groups[key].append(record)
        
        # Check if all groups have at least k records
        return all(len(group) >= k for group in groups.values())
    
    @staticmethod
    def gdpr_delete_user_data(
        db: Session,
        user_id: str,
        tables: List[str]
    ) -> Dict[str, int]:
        """
        Delete user data for GDPR compliance (right to erasure)
        
        Args:
            db: Database session
            user_id: User ID to delete data for
            tables: List of table names to delete from
        
        Returns:
            Dictionary mapping table name to number of deleted records
        """
        deleted_counts = {}
        
        # This is a simplified implementation
        # In production, you would need to handle foreign key constraints
        # and cascade deletes properly
        
        for table_name in tables:
            try:
                # Get table model
                from .models import Base
                table = None
                for mapper in Base.registry.mappers:
                    if mapper.class_.__tablename__ == table_name:
                        table = mapper.class_
                        break
                
                if table:
                    # Delete records
                    deleted = db.query(table).filter(
                        table.user_id == user_id
                    ).delete()
                    deleted_counts[table_name] = deleted
            except Exception as e:
                deleted_counts[table_name] = f"Error: {str(e)}"
        
        db.commit()
        
        return deleted_counts
    
    @staticmethod
    def generate_anonymization_report(
        original_data: Dict[str, Any],
        anonymized_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a report of anonymization changes
        
        Args:
            original_data: Original dataset
            anonymized_data: Anonymized dataset
        
        Returns:
            Report dictionary
        """
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'fields_anonymized': [],
            'pii_detected': {},
            'anonymization_methods': {}
        }
        
        for field in original_data:
            if field in anonymized_data:
                if original_data[field] != anonymized_data[field]:
                    report['fields_anonymized'].append(field)
        
        # Detect PII in original data
        for field, value in original_data.items():
            if isinstance(value, str):
                detected = AnonymizationService.detect_pii(value)
                if detected:
                    report['pii_detected'][field] = list(detected.keys())
        
        return report
