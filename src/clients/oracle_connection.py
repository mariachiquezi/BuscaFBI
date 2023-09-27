import cx_Oracle

class DB():
    cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\dudac\OneDrive\Documentos\oracle-path\instantclient_21_11")
    def conectar_banco():
        return cx_Oracle.connect(user="rm96135", password="020303", dsn="oracle.fiap.com.br/ORCL")
