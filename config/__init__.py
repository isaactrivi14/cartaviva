# PyMySQL es un conector de MySQL escrito en Python puro: se instala con pip en
# cualquier portátil sin compilar nada. Lo registramos como "MySQLdb", que es el
# nombre del conector que Django busca.
import pymysql

pymysql.version_info = (2, 2, 1, "final", 0)
pymysql.install_as_MySQLdb()
