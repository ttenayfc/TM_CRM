from fastapi import FastAPI
import pyodbc
import xmlrpc.client

app = FastAPI(title='API importar clientes y entidades extranjeras de SISCONT a Odoo v16.')


@app.get("/")
async def root():
    return {"message": "Importar datos desde SISCONT para Odoo16 de los clientes y entidades extranjeras de TM"}


def db_connect_siscont():
    db = {
        "server": "192.168.35.1",
        "port": "1433",
        "database": "siscont5_112023",
        "user": "sa",
        "password": "SQL*2020",
    }

    url_siscont = f'DRIVER=ODBC Driver 17 for SQL SERVER;SERVER={db["server"]};PORT={db["port"]};DATABASE' \
                  f'={db["database"]};TDS_Version=8.0;UID={db["user"]};PWD={db["password"]}'
    try:
        connect_siscont = pyodbc.connect(url_siscont)
        return connect_siscont
    except Exception as e:
        print("Error al crear conexion con sqlserver", e)


def db_connect_odoo():
    url = 'http://localhost:8016'
    db = 'db_odoo16'
    username = 'usuario_api'
    password = 'Odoo'
    # Create de common ServerProxy
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    # Authenticate
    uid = common.authenticate(db, username, password, {})
    # Create the models ServerProxy
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    return models, uid, db, password, username, url


# Esta funcion es para marcar que tipo de cliente y proveedor es.
def cliente_proveedor(CliCategoria, CliPaisCodIntern):
    # Crear un cliente nacional. CUBA su codigo internacional es 192, en el CRM es 51
    cliente = None
    cli_potencial = None
    proveedor = None
    prov_potencial = None
    if CliCategoria == 'C' and CliPaisCodIntern == '192':
        print("La categoria es: " + CliCategoria + " codigo pais: " + CliPaisCodIntern)
        cliente = True
    elif CliCategoria == 'P' and CliPaisCodIntern == '192':
        print("Es un cliente-proveedor nacional")
        proveedor = True
    elif CliCategoria == 'CP' and CliPaisCodIntern == '192':
        print("Es un cliente-proveedor nacional")
        cliente = True
        proveedor = True
    elif CliCategoria == 'L' and CliPaisCodIntern == '192':
        print("La categoria es: " + CliCategoria + " codigo pais: " + CliPaisCodIntern)
        cli_potencial = True
    elif CliCategoria == 'LR' and CliPaisCodIntern == '192':
        print("Es un cliente-proveedor nacional")
        prov_potencial = True
        cli_potencial = True
    return cliente, cli_potencial, proveedor, prov_potencial


# Funcion que crea un modelo TMEfgne (tm.efgne)(Empresa o forma de gestion no estatal) o un modelo TMUEBDA (
# tm.uebda)(UEB o Dependencia autorizada)
def efgne_uebda(connection_s5,
                models, uid, db, password, username, url,
                model,
                CliPaisCodIntern, CliDescripcion, CliDireccion, CliTelefono, CliEmail, ProvCod, MunicCod):
    # Buscar si esta registrado en ODOO
    result = models.execute_kw(db, uid, password, model, 'search',
                               [[['name', '=', CliDescripcion]]])
    print("****************RESULTADO DE search ***********")
    print(result)
    if result is None:
        if CliTelefono[0] == "5":
            celular = CliTelefono
            print("************EL CELULAR ES: " + celular)
        else:
            telefono = CliTelefono
            print("************EL TELEFONO ES: " + telefono)
        provincia_id, municipio_id = search_provincia_municipio(connection_s5, models, uid, db, password,
                                                                username, url, CliPaisCodIntern,
                                                                ProvCod, MunicCod)
        # Crear modelo
        id = models.execute_kw(db, uid, password, model, 'create', [{
            'name': CliDescripcion,
            'direccion': CliDireccion,
            'telefono': telefono,
            'celular': celular,
            'correo': CliEmail,
            'provincia_id': provincia_id,
            'municipio_id': municipio_id,
        }])

        print("************EL UEBDA / EFGNE ES: ************")
        print(id)

    return id


def search_organismo(connection_s5, models, uid, db, password, username, url, OrganCodigo):
    # connection_s5 -> variable de conexion DB siscont5
    # models, uid, db, password, username, url -> variables de conexion con Odoo
    if OrganCodigo is not None:
        q_organismo = f"SELECT OrganCodigo, OrganDescripcion FROM TEORGANISMO WHERE OrganCodigo = ?"
        q_organismo_s5 = connection_s5.cursor().execute(q_organismo, OrganCodigo)
        organismo = q_organismo_s5.fetchall()
        # Buscar si esta registrado en ODOO
        result = models.execute_kw(db, uid, password, 'tm.organismo', 'search', [[['name', '=', organismo[0][1]]]])
        if not result:
            # Crear un modelo TMOrganismo (tm.organismo)
            organismo_id = models.execute_kw(db, uid, password, 'tm.organismo', 'create', [{
                'name': organismo[0][1],
                'codigo': organismo[0][0]
            }])
        else:
            organismo_id = result[0]
    else:
        organismo_id = None
    return organismo_id


def search_tipificacion(connection_s5, TipifiCodigo, CliTCPMipyme):
    # connection_s5 -> variable de conexion DB siscont5
    if TipifiCodigo is not None:
        query = f"SELECT TipifiCodigo, TipifiDescripcion FROM SCOTIPIFEMPRESA WHERE TipifiCodigo = ?"
        query_s5 = connection_s5.cursor().execute(query, TipifiCodigo)
        value = query_s5.fetchall()
        uebda = False
        tipificacion = None
        if value is not None:
            if value[0][0] == 10 or value[0][0] == 20 or value[0][0] == 40:
                uebda = True
                if 'UEB' in value[0][1]:  # si value[0][1]: TipifiDescripcion contiene substring UEB
                    tipificacion = 'ueb_ees'  # ueb_ees: UEB o Empresa Estatal Socialista
                else:
                    tipificacion = 'ees'  # ees: Empresa Estatal Socialista
            if value[0][0] == 60:
                tipificacion = 'tcp'  # tcp: Trabajador por cuenta propia
            elif value[0][0] == 50:
                tipificacion = 'cna'  # cns: Cooperativa no agropecuaria
        if CliTCPMipyme == 'M':
            tipificacion = 'mipyme'
    return uebda, tipificacion


def search_provincia_municipio(connection_s5, models, uid, db, password, username, url,
                               CliPaisCodIntern, ProvCod, MunicCod):
    # connection_s5 -> variable de conexion DB siscont5
    # models, uid, db, password, username, url -> variables de conexion con Odoo
    if ProvCod is not None:
        query = f"SELECT * FROM TEPROVINCIA WHERE ProvCod = ?"
        query_s5 = connection_s5.cursor().execute(query, ProvCod)
        provincia = query_s5.fetchall()
        print("***** PROVINCIA EN SISCONT *****")
        print(provincia)
        if provincia:
            # Buscar si esta registrado en ODOO
            result = models.execute_kw(db, uid, password, 'res.country.state', 'search',
                                       [[['code', '=', provincia[0][0]]]])
            print("************* RESULT SI ESTA EN ODOO LA PROV ***********")
            print(result)
            if result:
                provincia_id = result[0][0]
            else:
                # Buscar el pais en SISCONT. SCOPAIS
                if CliPaisCodIntern is not None:
                    q_pais = f"SELECT PaisDescripcion FROM SCOPAIS WHERE PaisCodIntern = ?"
                    q_pais_s5 = connection_s5.cursor().execute(q_pais, CliPaisCodIntern)
                    PaisDescripcion = q_pais_s5.fetchval()
                    print("***** PAIS SISCONT *****")
                    print(PaisDescripcion)
                    # Buscar el pais en Odoo
                    country_id = models.execute_kw(db, uid, password, 'res.country', 'search',
                                                   [[['name', '=', PaisDescripcion]]])
                    print("***** RESULTADO DE SEARCH PAIS DADO *****")
                    print(country_id)

                    # Crear la provincia en Odoo. Modelo CountryState (res.country.state)
                    provincia_id = models.execute_kw(db, uid, password, 'res.country.state', 'create', [{
                        'name': provincia[0][1],
                        'code': provincia[0][0],
                        'country_id': country_id
                    }])
                    print("************* NO ESTA EN ODOO LA PROVINCIA Y SE CREO ***********")
                    print(provincia_id)
    else:
        provincia_id = None
    if MunicCod is not None:
        query = f"SELECT * FROM TEMUNICIPIOS WHERE ProvCod = ? AND MunicCod = ?"
        query_s5 = connection_s5.cursor().execute(query, ProvCod, MunicCod)
        municipio = query_s5.fetchall()
        print("***** MUNICIPIO EN SISCONT *****")
        print(municipio)
        if municipio:
            # Buscar si esta registrado en ODOO. municipio[0][0] -> ProvCod / municipio[0][1] -> MunicCod
            municipio_codigo = str(municipio[0][0]) + '.' + str(municipio[0][1])
            print("******* CODIGO MUNICIPIO CONFORMADO *******")
            print(municipio_codigo)
            result = models.execute_kw(db, uid, password, 'tm.municipio', 'search',
                                       [[['code', '=', municipio_codigo]]])
            print("************* RESULT SI ESTA EN ODOO EL MUNICIPIO ***********")
            print(result)
            if result:
                municipio_id = result
            else:
                municipio_id = models.execute_kw(db, uid, password, 'tm.municipio', 'create', [{
                    'name': municipio[0][1],
                    'codigo': municipio[0][0],
                    'provincia_id': provincia_id
                }])
                print("************* NO ESTA EN ODOO EL MUNICIPIO Y SE CREO ***********")
                print(municipio_id)
    else:
        municipio_id = None
    return provincia_id, municipio_id


@app.get("/clientes_proveedores")
async def importar_clientes_proveedores():
    try:
        # connection_s5 -> variable de conexion DB siscont5
        connection_s5 = db_connect_siscont()
        query = f"SELECT TOP 8  *  FROM SMGCLIENTEPROVEEDOR"
        # Declarando cursor de la conexion para poder ejecutar la consulta
        cursor_s5 = connection_s5.cursor().execute(query)
        clis_provs = cursor_s5.fetchall()  # clis_provs -> clientes-proveedores

        # Conectando con ODOO
        models, uid, db, password, username, url = db_connect_odoo()
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        for cp in clis_provs:
            # Crear un cliente nacional
            cliente, cli_potencial, proveedor, prov_potencial = cliente_proveedor(cp.CliCategoria, cp.CliPaisCodIntern)
            # *************CREANDO AL CLIENTE****************
            # Buscar el organismo en SISCONT
            if cp.OrganCodigo is not None:
                organismo_id = search_organismo(connection_s5, models, uid, db, password, username, url, cp.OrganCodigo)
            else:
                organismo_id = None
            # Buscar el osde en SISCONT. VER COMO IDENTIFICO EL OSDE EN BD
            # Buscar en SISCONT la tipificacion
            uebda, tipificacion = search_tipificacion(connection_s5, cp.TipifiCodigo, cp.CliTCPMipyme)
            if uebda:  # Si uebda=True es porque es una UEB o Dependencia autorizada
                uebda_id = efgne_uebda(connection_s5,  # Conexion SISCONT
                                       models, uid, db, password, username, url,  # Conexion Odoo
                                       'tm.uebda',  # Modelo de Odoo
                                       cp.CliPaisCodIntern, cp.CliDescripcion, cp.CliDireccion, cp.CliTelefono,
                                       cp.CliEmail,
                                       cp.ProvCod, cp.MunicCod)
            else:  # Entonces es una EFGNE
                efgne_id = efgne_uebda(connection_s5,  # Conexion SISCONT
                                       models, uid, db, password, username, url,  # Conexion Odoo
                                       'tm.efgne',  # Modelo de Odoo
                                       cp.CliPaisCodIntern, cp.CliDescripcion, cp.CliDireccion, cp.CliTelefono,
                                       cp.CliEmail,
                                       cp.ProvCod, cp.MunicCod)
            # Buscar el cargo en SISCONT si existe poner el id sino hay que crearlo en

            # Crear modelo ResPartner (res.partner)
            partner = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
                'name': cp.CliDescripcion,
                'display_name': cp.CliDescripcion,
                'reeup': cp.CliCodigo,
                # 'carnet': carnet,
                'vat': cp.CliNit,
                'organismo_id': organismo_id,
                # 'osde_id': osde_id,
                'no_estatal': tipificacion,
                'cliente': cliente,
                'cli_potencial': cli_potencial,
                'proveedor': proveedor,
                'prov_potencial': prov_potencial,
                'efgne_id': efgne_id,
                'uebda_id': uebda_id,
            }])
    except Exception as e:
        print(f"Error al conectar a la base de datos: {str(e)}")
    return {"Cliente": partner}
