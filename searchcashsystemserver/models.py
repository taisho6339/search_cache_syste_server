import os

from sklearn.externals import joblib
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from sqlalchemy import (
    Column,
    Integer,
    Text,
)
from sqlalchemy.sql.schema import ForeignKey
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

here = os.path.abspath(os.path.dirname(__file__))
CLF = joblib.load(os.path.join(here, 'svmmodels/skew_ratio'))


class Query(Base):
    """SearchQuery"""
    __tablename__ = 'queries'

    id = Column(Integer, primary_key=True)
    query = Column(Text, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, query):
        self.query = query
        self.count = 0


class Relation(Base):
    """Relation between query and query"""

    __tablename__ = 'relations'

    SPECIFY = 0
    GENERALIZE = 1
    PARALLEL = 2
    FORMAT = 3
    NEW = 4

    id = Column(Integer, primary_key=True)
    first_id = Column(Integer, ForeignKey('queries.id'))
    second_id = Column(Integer, ForeignKey('queries.id'))
    intent = Column(Integer)
    count = Column(Integer)

    def __init__(self, first_id, second_id, intent):
        self.first_id = first_id
        self.second_id = second_id
        self.intent = intent
        self.count = 0


class DocumentRelation(Base):
    __tablename__ = 'document_relations'
    id = Column(Integer, primary_key=True)
    query_id = Column(Integer, ForeignKey('queries.id'))
    document_id = Column(Integer, ForeignKey('documents.id'))
    click_count = Column(Integer)

    def __init__(self, query_id, document_id):
        self.query_id = query_id
        self.document_id = document_id
        self.click_count = 0


class Document(Base):
    """Clicked Documents"""

    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    url = Column(Text)
    title = Column(Text)
    snippet = Column(Text)

    def __init__(self, url, title, snippet):
        self.url = url
        self.title = title
        self.snippet = snippet