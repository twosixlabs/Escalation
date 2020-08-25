# coding: utf-8
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class DataUploadMetadatum(Base):
    __tablename__ = "data_upload_metadata"

    upload_id = Column(Integer, primary_key=True, nullable=False)
    table_name = Column(Text, primary_key=True, nullable=False)
    upload_time = Column(DateTime)
    active = Column(Boolean)
