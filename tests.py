import pytest
from dotenv import load_dotenv

from models import MecaluxConnector
import os
import logging


def test_xml_scanning():
    load_dotenv()

    logging.basicConfig(level=logging.INFO)
    file_handler = logging.FileHandler('my_python_process.log', mode='w')
    file_handler.setLevel(logging.INFO)
    logger = logging.getLogger('[MyPythonProcess]')

    connector = MecaluxConnector(logger)

    connector.one_xml_scan()
    communicates = connector.get_list_of_communicates()

    print(communicates)