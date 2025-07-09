import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('[MyPythonProcess]')

# Dodanie FileHandler, aby zapisywać logi do pliku i nadpisywać przy każdym uruchomieniu
file_handler = logging.FileHandler('my_python_process.log', mode='w')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)