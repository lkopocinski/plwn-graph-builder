import re
import pymysql.cursors

from collections import defaultdict


class DB:

    def __init__(self):
        pass

    def connect(self, config_file):
        user, password, host, name, port = self._read_db_config(config_file)
        connection = pymysql.connect(
            user=user,
            password=password,
            host=host,
            db=name,
            port=port,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor)

        return connection

    def _read_db_config(self, config_file):
        config_dict = self._config_to_dict(config_file)
        user = config_dict['User']
        password = config_dict['Password']

        host_db_port = config_dict['Url']
        host_db_port = host_db_port.replace('jdbc:mysql://', '')
        host_db_port = re.split(':|/', host_db_port)

        host = host_db_port[0]
        port = int(host_db_port[1])
        name = host_db_port[2]

        return user, password, host, name, port

    @staticmethod
    def _config_to_dict(config_file):
        config_dict = defaultdict(str)

        with open(config_file, 'r') as f:
            for line in f:
                splitted = line.split('=')
                key = splitted[0]
                value = splitted[1]
                config_dict[key] = value.strip()

        return config_dict
