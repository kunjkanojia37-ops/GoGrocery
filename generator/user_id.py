from sqlalchemy.orm import Session
from sqlalchemy import desc

def generate_unique_id(db, model, prefix: str, id_column_name: str = "Id") -> str:
    """
    Generates an incremental ID like SUP-0001, INV-0001 based on the database's last entry.
    """
    # Query the last inserted record ordered by ID descending
    last_record = db.query(model).order_by(desc(getattr(model, id_column_name))).first()
    
    if not last_record:
        return f"{prefix}-0001"
        
    last_id = getattr(last_record, id_column_name) # e.g., "SUP-0005"
    try:
        # Split by dash and increment the numeric part
        numeric_part = int(last_id.split("-")[-1])
        new_number = numeric_part + 1
    except (ValueError, IndexError):
        new_number = 1
        
    return f"{prefix}-{new_number:04d}" # Pads with zeros, e.g., 0006

