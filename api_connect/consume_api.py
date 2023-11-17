import requests

proxies = {
    'http': 'proxy.isp.cupet.cu:3128',
    'https': 'proxy.isp.cupet.cu:3128'
}
# 'http': 'vs2502.tm.cupet.cu:3128',
# 'https': 'vs2502.tm.cupet.cu:3128',
# resp = requests.get('http://172.18.210.10/ws_af_tm/apiclient/getallclient', proxies=proxies)

resp = requests.get('http://172.18.210.10/ws_af_tm/apiclient/getallclient', proxies=proxies)
# print(resp.status_code)
# print(resp.json())
data = resp.json()
for e in data["SDTGetClient"]:
    # Datos de un organismo tb-> tm.organismo
    name = e["CliDescripcion"]
    # codigo = e["OrganCodigo"]
    direccion = e["CliDireccion"]
    # Crear una provicia de ser necesario

    # Datos de un OSDE tb-> tm.osde
    print(e["OrganCodigo"])
