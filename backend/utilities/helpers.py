from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from bson import ObjectId
import re

def validate_nyu_email(email: str) -> bool:
    """
    Validate if email is from NYU domain
    
    Args:
        email: Email to validate
        
    Returns:
        True if email is valid NYU email, False otherwise
    """
    return email.endswith('@nyu.edu')

def format_mongodb_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format MongoDB document for API response
    
    Args:
        doc: MongoDB document
        
    Returns:
        Formatted document with string ID and proper datetime objects
    """
    if doc is None:
        return None
    
    # Convert ObjectId to string
    if '_id' in doc:
        doc['id'] = str(doc['_id'])
        del doc['_id']
    
    return doc

def generate_search_query(filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate MongoDB query from search filters
    
    Args:
        filters: Search filters
        
    Returns:
        MongoDB query dictionary
    """
    query = {}
    
    # Text search
    if filters.get('keyword'):
        query['$text'] = {'$search': filters['keyword']}
    
    # Category filter
    if filters.get('category'):
        query['category'] = filters['category']
    
    # Price range filter
    if filters.get('min_price') is not None or filters.get('max_price') is not None:
        query['price'] = {}
        if filters.get('min_price') is not None:
            query['price']['$gte'] = filters['min_price']
        if filters.get('max_price') is not None:
            query['price']['$lte'] = filters['max_price']
    
    # Condition filter
    if filters.get('condition') and filters.get('condition').strip():
        query['condition'] = filters['condition'].lower()

    # Status filter
    if filters.get('status') and filters.get('status').strip():
        query['status'] = filters['status'].lower()
    
    # Tags filter
    if filters.get('tags'):
        query['tags'] = {'$in': filters['tags']}
    
    return query

def is_valid_object_id(id: str) -> bool:
    """
    Check if a string is a valid MongoDB ObjectId
    
    Args:
        id: String to check
        
    Returns:
        True if valid ObjectId, False otherwise
    """
    return ObjectId.is_valid(id)

def calculate_expiration_date(days: int = 7) -> datetime:
    """
    Calculate expiration date for reservations
    
    Args:
        days: Number of days until expiration
        
    Returns:
        Expiration datetime
    """
    return datetime.utcnow() + timedelta(days=days)
