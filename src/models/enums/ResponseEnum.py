from enum import Enum

class ResponseSignal(Enum):
    
    PRODUCT_FOUND_SUCCESS = "files founded successfully"
    PRODUCT_FOUND_FAIL = "files not founded"
    PRODUCT_UPLOAD_SUCCESS = "products uploaded successfully"

    EVENT_FOUND_FAIL = "events not founded"
    EVENT_FOUND_SUCCESS =  "events founded successfully"

    EMBEDDING_UPLOADED_SUCCESS= "Embeddings updated successfully"

 