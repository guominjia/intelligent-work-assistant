from .mail import index_mail
from .onenote import index_onenote
from .document import index_document

def index(embed_model, database_name='chroma_database'):
    index_mail(embed_model, database_name)
    index_onenote(embed_model, database_name)
    index_document(embed_model, database_name)