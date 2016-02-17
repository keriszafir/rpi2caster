# -*- coding: utf-8 -*-
"""database_backends: connections for various database types,
currently supported: sqlite and postgres"""
import getpass


class GenericDBConnection(object):
    """Generic methods and attributes for connection objects"""
    def __init__(self):
        self.db_conn = None

    def __enter__(self):
        return self.db_conn


class SQLiteConnection(GenericDBConnection):
    """SQLite3 connection - local database on a file"""
    def __init__(self, db_path):
        super().__init__()
        import sqlite3
        try:
            self.db_conn = sqlite3.connect(db_path)
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            pass


class PostgresConnection(GenericDBConnection):
    """PostgreSQL connection without SSH tunnelling or SSL security"""
    def __init__(self, db_name, db_host='localhost', db_port=5432,
                 db_username='postgres', db_password='postgres'):
        super().__init__()
        import psycopg2
        try:
            self.db_conn = psycopg2.connect(database=db_name,
                                            port=db_port,
                                            user=db_username,
                                            password=db_password,
                                            host=db_host)
        except (psycopg2.OperationalError, psycopg2.DatabaseError):
            pass


class SSLTunnelPostgresConnection(GenericDBConnection):
    """Postgres connection tunnelled over SSH"""
    def __init__(self, db_name, host_address, ssh_port=22,
                 ssh_username=getpass.getuser(), ssh_password='',
                 db_username='postgres',
                 db_password='postgres'):
        super().__init__()
        import psycopg2
        from sshtunnel import SSHTunnelForwarder
        # Connect over SSH tunnel
        listen_addr = ('127.0.0.1', 5432)
        with SSHTunnelForwarder(host_address, ssh_port,
                                ssh_password=ssh_password,
                                ssh_username=ssh_username,
                                remote_bind_address=listen_addr) as server:
            try:
                self.db_conn = psycopg2.connect(database=db_name,
                                                port=server.local_bind_port,
                                                user=db_username,
                                                password=db_password)
            except (psycopg2.OperationalError, psycopg2.DatabaseError):
                pass
