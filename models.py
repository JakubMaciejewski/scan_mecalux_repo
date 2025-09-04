import bs4
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import requests
import threading
import logging
import json
import shutil

import logging


class MecaluxConnector:
    def __init__(self, logger):
        self.import_folder_path = os.getenv('MECALUX_IMPORT_FOLDER_PATH')
        self.export_folder_path = os.getenv('MECALUX_EXPORT_FOLDER_PATH')
        self.post_url = os.getenv('POST_URL')
        self.logger = logger
        self.logger.info(f'MecaluxConnector initialized')
        self.list_of_communicates = []


    def one_xml_scan(self):
        self.list_of_communicates = []

        for root, dirs, files in os.walk(self.import_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.xml') and file.startswith('SOF'):
                    self.get_SOF_communicates(file_path)
                if file.endswith('.xml') and file.startswith('SOC'):
                    self.get_SOC_communicates(file_path)

                if os.path.isfile(file_path):
                    os.remove(file_path)

        for root, dirs, files in os.walk(self.export_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.xml') and file.startswith('SOR'):
                    self.get_SOR_communicates(file_path)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        self.send_communicates()


    def get_SOF_communicates(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                soup = BeautifulSoup(content, 'lxml-xml')
                shipping_finalization_list = soup.find_all('ShippingOrderFinalization')
                for finalization in shipping_finalization_list:
                    temp_dic = {}
                    temp_dic['Flag'] = 'close'
                    sor_code_info = finalization.find('SorCode').text
                    parts = sor_code_info.replace("___", '_').split('_')  # finding localization, user and id
                    if len(parts) == 3:  # if format correct
                        temp_dic['SorCode'] = parts[2]
                        temp_dic['user'] = parts[1]
                        temp_dic['location'] = parts[0]
                        temp_dic['sector'] = 'completion'
                    elif len(parts) == 1:
                        temp_dic['SorCode'] = sor_code_info
                        temp_dic['sector'] = 'delivery'
                    else:
                        self.logger.error(f"error occurred while reading sorecode info: {sor_code_info}")
                        continue
                    temp_dic['timestamp'] = datetime.now().isoformat()
                    self.list_of_communicates.append(temp_dic)
        except Exception as e:
            self.logger.error(f"error occurred while opening the file {file_path}: {e}")


    def get_SOC_communicates(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                soup = BeautifulSoup(content, 'lxml-xml')
                status_change_list = soup.find_all('ShippingOrderStatusChange')
                for status_change in status_change_list:
                    temp_dic = {}
                    temp_dic['Flag'] = 'update'
                    sor_code_info = status_change.find('SorCode').text
                    parts = sor_code_info.replace("___", '_').split('_') # finding localization, user and id
                    if len(parts) == 3: # if format correct
                        temp_dic['SorCode'] = parts[2]
                        temp_dic['user'] = parts[1]
                        temp_dic['location'] = parts[0]
                        temp_dic['sector'] = 'completion'
                    elif len(parts) == 1:
                        temp_dic['SorCode'] = sor_code_info
                        temp_dic['sector'] = 'delivery'
                    else:
                        self.logger.error(f"error occurred while reading sorecode info: {sor_code_info}")
                        continue
                    temp_dic['status'] = status_change.find('Status').text
                    temp_dic['update_timestamp'] = datetime.now().isoformat()
                    self.list_of_communicates.append(temp_dic)
        except Exception as e:
            self.logger.error(f"error occurred while opening the file {file_path}: {e}")

    def get_SOR_communicates(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                soup = BeautifulSoup(content, 'lxml-xml')
                shipping_order_list = soup.find_all('ShippingOrder')
                for shipping_order in shipping_order_list:
                    temp_dic = {}
                    temp_dic['Flag'] = 'create'
                    sor_code_info = shipping_order.find('SorCode').text
                    parts = sor_code_info.replace("___", '_').split('_')  # finding localization, user and id
                    if len(parts) == 3: # if format correct
                        temp_dic['SorCode'] = parts[2]
                        temp_dic['user'] = parts[1]
                        temp_dic['location'] = parts[0]
                        temp_dic['sector'] = 'completion'
                    elif len(parts) == 1:
                        temp_dic['SorCode'] = sor_code_info
                        temp_dic['sector'] = 'delivery'
                    else:
                        self.logger.error(f"error occurred while reading sorecode info: {sor_code_info}")
                        continue

                    temp_dic['status'] = 'created'
                    temp_dic['timestamp'] = datetime.now().isoformat()
                    temp_dic['material_index'] = shipping_order.find('LneItemCode').text
                    temp_dic['Quantity'] = shipping_order.find('LneQtyOrder').text
                    temp_dic['UOM'] = shipping_order.find('LneQtyUoMCode').text

                    self.list_of_communicates.append(temp_dic)
        except Exception as e:
            self.logger.error(f"error occurred while opening the file {file_path}: {e}")

    def send_communicates(self):
        requests.post(self.post_url, json=self.list_of_communicates)

    def get_list_of_communicates(self):
        return self.list_of_communicates