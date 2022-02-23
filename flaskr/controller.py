#!/usr/bin/env python
import fr_core_news_md
# pip install https://github.com/explosion/spacy-models/releases/download/fr_core_news_md-3.2.0/fr_core_news_md-3.2.0-py3-none-any.whl
"""
Controller module that describes endpoints and its functions
"""

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from flaskr.model import (
    Pdf,
    database_is_empty,
    generate_file_id,
    id_in_database,
    init_db,
    save_metadata_and_text_to_data_base,
    save_received_pdf,
    session,
)

# Create blueprint objects
index_blueprint = Blueprint("index", __name__)
upload_file_blueprint = Blueprint("upload_file", __name__)
get_file_info_blueprint = Blueprint("get_file_info", __name__)
get_text_blueprint = Blueprint("get_text", __name__)


# Bind function with decorator
@index_blueprint.route("/")
def index():
    """
    Routing to the sample index page http://localhost:5000/
    """
    return str("Index page")


# Bind function with decorator
@upload_file_blueprint.route("/documents", methods=["POST"])
def upload_file():
    """
    Routing to the endpoint that allows file upload
    It saves the uploaded file on local machine and returns file's id
    and checks if file is pdf-type
    """

    # Save the file received in curl in 'file' variable
    file = request.files["file"]

    # Verification of file type from its name block
    # Save the filename from file
    filename = secure_filename(file.filename)

    # Extract file extention
    file_extention = filename[-3::].lower()

    # It Checks if the file is pdf-type
    # If it is pdf, it saves the file and returns its identifier from database in json-format
    
    # 
    # READING A TEXT FILE
    #
    text = ''
    lines = []
    
    if file_extention == "txt":
        file_id = generate_file_id()
        lines = file.readlines()

        for line in lines:
           text += line.decode()
        
        #
        # NLP
        #
        
        # input text
        nlp = fr_core_news_md.load()
        doc = nlp(text)
        
        # output text
        line_all = ''

        if len(doc.ents) == 0:
            for token in doc:
                if token.dep_ == "nsubj":
                    line_all += token.lemma_ + ' '
                if token.dep_ == "obj":
                    line_all += token.lemma_ + ' '
                if token.dep_ == "conj":
                    line_all += token.lemma_ + ' '
                if token.dep_ == "advmode":
                    line_all += token.lemma_ + ' '
                if token.dep_ == "ROOT":
                    line_all += token.lemma_ + ' '
                if token.dep_ == "cop":
                    line_all += token.lemma_ + ' '
                if token.dep_ == "amod":
                    line_all += token.lemma_ + ' '
                if token.dep_ == "obl":
                    line_all += token.lemma_ + ' '

		# if there's at least one named entity
        else:
            for token in doc:
                # if the word is subj
                if token.dep_ == "nsubj":
                    # check if it is a part of entities
                    for i in range(len(doc.ents)):
                        important_part = token
                    if important_part.text in str(doc.ents[i]):
                        # print(important_part.text)
                        line_all += doc.ents[i] + ' '
                        # leave the cycle (United gives one, Kingdome gives two)
                        break
                    else: 
                        line_all += token.text + ' '
                        break

                elif token.dep_ == "obj":
                    for i in range(len(doc.ents)):
                        important_part = token
                        if important_part.text in str(doc.ents[i]):
                            # print(important_part.text)
                            line_all += doc.ents[i] + ' '
                            break
                        else: 
                            line_all += token.text + ' '
                            break

                elif token.dep_ == "conj":
                    for i in range(len(doc.ents)):
                        important_part = token
                        if important_part.text in str(doc.ents[i]):
                            # print(important_part.text)
                            line_all += doc.ents[i] + ' '
                            break
                        else: 
                            line_all += token.text + ' ' 
                            break

                elif token.dep_ == "advmod" or token.dep_ == "ROOT" or token.dep_ == "amod" or token.dep_ == "obl":
                    line_all += token.lemma_ + ' '
      
        doc_id_dictionary = {"text": line_all}
        return jsonify(doc_id_dictionary)

    # In case the file is not pdf
    # it returns error in json and 415 HTTP error code (Unsupported Media Type)
    error_msg = {
        "error_message": "only .pdf or .PDF-file types are allowed",
    }
    return jsonify(error_msg), 415


# Bind function with decorator
@get_file_info_blueprint.route("/documents/<document_id>", methods=["GET"])
def processing_meta_link(document_id):
    """
    Routing to the endpoint that returns document's metadata in json
    id is identifier in database
    """

    # checks if it is the first usage of database
    if database_is_empty():
        error_msg = {
            "error_message": "database is empty",
        }
        return jsonify(error_msg), 404

    # In case the requested <document_id> is in database
    if id_in_database(document_id):
        # It saves in pdf_item the information about the requested record from database
        pdf_item = session.query(Pdf).filter_by(id=document_id).first()

        # Create a dicionary to save information from pdf_item
        meta_data_dictionary = {}
        meta_data_dictionary["author"] = pdf_item.author
        meta_data_dictionary["creation_date"] = pdf_item.creation_date
        meta_data_dictionary["modification_date"] = pdf_item.modification_date
        meta_data_dictionary["creator"] = pdf_item.creator
        meta_data_dictionary["status"] = pdf_item.status
        # meta_data_dictionary['text'] = pdf_item.text
        meta_data_dictionary["file_id"] = pdf_item.file_id
        meta_data_dictionary["link_to_content"] = (
            "http://localhost:5000/text/" + str(pdf_item.id) + ".txt"
        )
        return jsonify(meta_data_dictionary)

    # In case the requested <document_id> is NOT in database,
    # it returns error message in json and 404 HTTP error code (Not Found)
    error_msg = {
        "error_message": "the id you ask does not exist",
    }
    return jsonify(error_msg), 404


# Bind function with decorator
@get_text_blueprint.route("/text/<document_id>.txt", methods=["GET"])
def print_text(document_id):
    """
    Routing to the endpoint that returns related text from database
    """

    # checks if it is the first usage of database
    if database_is_empty():
        error_msg = {
            "error_message": "database is empty",
        }
        return jsonify(error_msg), 404

    # checks if requested document_id in database
    # and returns from database the text in json-format
    if id_in_database(document_id):
        pdf_item = session.query(Pdf).filter_by(id=document_id).first()
        doc_text_in_dict = {"text": pdf_item.text}
        return jsonify(doc_text_in_dict)

    # In case the requested <document_id> is NOT in database,
    # it returns error message in json and 404 HTTP error code (Not Found)
    error_msg = {
        "error_message": "the id you ask does not exist",
    }
    return jsonify(error_msg), 404
