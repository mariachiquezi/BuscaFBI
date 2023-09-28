import cx_Oracle

class DB():
    # inicializando oracle (colocando diretorio do instantclient)
    cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\dudac\OneDrive\Documentos\oracle-path\instantclient_21_11")
    def conectar_banco():
        return cx_Oracle.connect(user="username", password="senha", dsn="Nome do host/SID")
