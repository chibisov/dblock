# -*- coding: utf-8 -*-
import threading
import time

import unittest
import MySQLdb

from dblock.core.dblock import database_wide_lock


class TestCore(unittest.TestCase):
    def setUp(self):
        self.connection = self.get_connection()

    def tearDown(self):
        self.connection.cursor().execute('DELETE FROM man')

    def get_connection(self):
        return MySQLdb.connect(host='localhost', user='root', passwd='root', db='test')

    def get_name(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT name FROM man WHERE id=1')
        return cursor.fetchone()[0]

    def test_connections(self):
        self.assertNotEquals(self.get_connection(), self.get_connection())
        self.assertNotEquals(self.get_connection(), self.connection)

    def test_acquired__decorator(self):
        @database_wide_lock('test_1', self.get_connection())
        def some_func(name, acquired):
            return name, acquired

        cursor = self.get_connection().cursor()
        cursor.execute("SELECT GET_LOCK('test_1', 0)")
        self.assertEquals(some_func('gena'), ('gena', False))

        cursor.execute("SELECT RELEASE_LOCK('test_1')")
        self.assertEquals(some_func('gena'), ('gena', True))

    def test_acquired__decorator__is_skip_if_could_not_acquire(self):
        is_func_called = []
        @database_wide_lock('test_2', self.get_connection(), is_skip_if_could_not_acquire=True)
        def some_func(name, acquired):
            is_func_called.append(True)
            return name, acquired

        cursor = self.get_connection().cursor()
        cursor.execute("SELECT GET_LOCK('test_2', 0)")
        self.assertEquals(some_func('gena'), None)
        self.assertEquals(is_func_called, [])

        cursor.execute("SELECT RELEASE_LOCK('test_2')")
        self.assertEquals(some_func('gena'), ('gena', True)) 
        self.assertEquals(is_func_called, [True])

    def test_acquired__context(self):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT GET_LOCK('test_3', 0)")
        with database_wide_lock('test_3', self.get_connection()) as acquired:
            self.assertFalse(acquired)

        cursor.execute("SELECT RELEASE_LOCK('test_3')")
        with database_wide_lock('test_3', self.get_connection()) as acquired:
            self.assertTrue(acquired)

    # def test_change_name(self):
        # @database_wide_lock('test_threads', self.get_connection())
        # def some_func(name, acquired):