import os
from unittest import TestCase, SkipTest
from tersicore.database import Database


class TestDatabase:
    # TODO: Put database tests here.
    pass


class TestSqlite(TestCase, TestDatabase):
    def getUp(self):
        self.db = Database(engine='sqlite')


class TestMysql(TestCase, TestDatabase):
    def getUp(self):
        host = os.getenv('TERSICORE_TEST_MYSQL_HOST')
        port = os.getenv('TERSICORE_TEST_MYSQL_PORT')
        database = os.getenv('TERSICORE_TEST_MYSQL_DATABASE')
        user = os.getenv('TERSICORE_TEST_MYSQL_USER')
        password = os.getenv('TERSICORE_TEST_MYSQL_PASSWORD')

        if any(e is None for e in [host, port, database, user, password]):
            raise SkipTest("Can't connecto to MySQL database.")

        self.db = Database(host=host, port=port, database=database,
                           user=user, password=password)
