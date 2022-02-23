#!/usr/bin/env python

"""
Model module that assures work with database
"""

# for verification if upload path exist
import os

# imports to generate file-id
import random
import string

# imports to work with web
from flask import request

# imports to read from pdf
from pdfminer.high_level import extract_text
from pdfminer.pdfdocument import PDFDocument

# imports to extract data from pdf
from pdfminer.pdfparser import PDFParser

# imports to work with databse
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# path to folder where files will be saved
PATH_TO_SAVE_FOLDER = "./uploads/"


# creation and preparation of database
engine = create_engine(
    "sqlite:///pdf.db", echo=False, connect_args={"check_same_thread": False}
)
connection = engine.connect()
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


def init_db():
    """
    Database initialization
    """
    Base.metadata.create_all(engine)


class Pdf(Base):
    """
    Represents pdf-file
    It is used to save metadata, text of pdf-file
    and to retrive this information
    """

    # Table name in the database
    __tablename__ = "pdfs"
    # identifier in database
    id = Column(Integer, primary_key=True)
    # author of pdf-file
    author = Column(String)
    # date of creation of pdf-file
    creation_date = Column(String)
    # last modification of pdf-file
    modification_date = Column(String)
    # creator of pdf-file
    creator = Column(String)
    # status of pdf-file
    status = Column(String)
    # text inside pdf-file
    text = Column(String)
    # id of pdf file that was saved locally
    # for example if file_id = baaatgwcatfnckpi, the file is saved as 'baaatgwcatfnckpi.pdf'
    file_id = Column(String)


def database_is_empty():
    """
    Verifies whether the database is empty
    """

    # default verification result is False
    result = False

    # check if database is empty
    filesize = os.path.getsize("./pdf.db")
    if filesize == 0:
        return True

    return result


def id_in_database(document_id):
    """
    Verifies if a document_id is in dabase
    and whether document_id is a digit
    """

    # default verification result is False
    result = False

    # checks the highest id in database
    max_id_in_database = session.query(Pdf).count()

    # creates an array of existing indexes in database
    list_of_id_in_database = list(range(1, max_id_in_database + 1))

    # checks if requested identifier is a number
    # and whether the id is in database
    if document_id.isdigit() and int(document_id) in list_of_id_in_database:
        result = True
    return result


def create_upload_folder_if_needed():
    """
    Checks if the folder where pdf files are saved exists
    If upload folder does not exist, the function creates it
    """
    if not os.path.exists(PATH_TO_SAVE_FOLDER):
        os.makedirs(PATH_TO_SAVE_FOLDER)


def save_received_pdf(file_id):
    """
    Saves uploaded pdf-file to local path
    It uses file_id as a part of file name
    """
    create_upload_folder_if_needed()
    local_file_path = PATH_TO_SAVE_FOLDER + file_id + ".pdf"
    file = request.files["file"]
    file.save(local_file_path)


def generate_file_id():
    """
    Generates id that will be used to save file in local filesystem
    The id consists of 16 ascii characters
    """
    file_id_length = 16
    file_id = "".join(
        random.choice(string.ascii_lowercase) for i in range(file_id_length)
    )
    return str(file_id)


def save_metadata_and_text_to_data_base(doc_id):
    """
    Saves meta-data and text from pdf to database
    """

    # extracts text and metadata from pdf
    doc_text = extract_text_from_pdf(doc_id)
    meta_data = extract_metadata_from_pdf(doc_id)

    # saves information in database
    session.add_all(
        [
            Pdf(
                author=meta_data["author"],
                creation_date=meta_data["creation_date"],
                modification_date=meta_data["modification_date"],
                creator=meta_data["creator"],
                # status is success since the file is saved locally
                status="success",
                text=doc_text,
                file_id=doc_id,
            )
        ]
    )
    session.commit()

    # gets the record from database using pdf-file name
    pdf_item = session.query(Pdf).filter_by(file_id=doc_id).first()

    # returns identifier of the record in database
    return pdf_item.id


def extract_text_from_pdf(doc_id):
    """
    Extracts text from pdf-file
    """
    # gets previously saved pdf file locally
    path_to_pdf = PATH_TO_SAVE_FOLDER + doc_id + ".pdf"

    # extracts text from the pdf
    text = extract_text(path_to_pdf)
    return text


def extract_metadata_from_pdf(doc_id):
    """
    Extracts metadata from pdf-file
    and returns dictionary with metadata inside
    """

    # gets previously saved pdf file locally
    path_to_pdf = PATH_TO_SAVE_FOLDER + doc_id + ".pdf"

    # extracts metadata from the pdf
    with open(path_to_pdf, "rb") as file:
        parser = PDFParser(file)
        doc = PDFDocument(parser)

        # creates temporary dictionary to save metadata
        meta_data = {}

        for item in doc.info:
            meta_data["author"] = item["Producer"].decode("utf-8", "ignore")
            meta_data["creation_date"] = item["CreationDate"].decode("utf-8", "ignore")
            meta_data["modification_date"] = item["ModDate"].decode("utf-8", "ignore")
            meta_data["creator"] = item["Creator"].decode("utf-8", "ignore")
            # meta_data['title'] = item['Title'].decode("utf-8", 'ignore')

    return meta_data
