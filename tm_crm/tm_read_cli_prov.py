# Esta es la libreria para conextar la API Externa de Odoo. El protocolo es XMLRPC
# 1.Para el uso de la API Externa se debe crear usuario y asignarle un a contrasenna
# 2. Acceder al ERP Odoo con el usuario nuevo
# 3. Crear un archivo extension .py y poner lo que aparece a continuacion
# import xmlrpc.client
import requests

url = 'http://172.18.210.10/ws_af_tm/apiclient/getallclient'
response = requests.get(url)
print(response.status_code)
#
# # Datos de conexion
# url = 'http://localhost:8016'
# db = 'db_odoo16'
# username = 'usuario_api'
# password = 'Odoo'
# clave_api = 'b6863f3ab51434d725b054d2ce73033c8daeb5ae'
#
# # Inicio de sesion
# common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
# # common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
# print(common.version())
#
# uid = common.authenticate(db, username, password, {}) #Aqui se puede usar la clave_api o el password
# # print(uid)
#
# # Llamadas a metodos. Estos se llaman con la funcion RPC: execute_kw
# partner_id = common.execute_kw(db, uid, password, 'res.partner', 'create', [{'name':'New Partner Yntt'}])
# print(partner_id)
