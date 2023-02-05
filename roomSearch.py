import requests
import json
import sys
from geopy.geocoders import Nominatim
import time

#Tempo inicial. No fim está um tempo final, para sabermos quanto tempo demorou o programa
inicio = time.time()

#Não percebo bem o que isto faz mas é para o calculo das zonas tendo em conta as coordenadas
geolocator = Nominatim(user_agent="geoapiExercises")

#EXEMPLO:
# python roomSearch.py 400 Arroios 20
input = (sys.argv)

p = input[1] #preço
z = input[2] #localização Ex.: Arroios, Parque_das_Nações, Alcântara
d = input[3] #depth 0-20 (quantidade de páginas observadas no inLife e UniPlaces)
zona = z.replace('_', ' ')

listaFinal = [] #Lista final que depois será apresentada no Json

nResults = 0 #número de resultados
# ------------------------------------------------ inLife ---------------------------------------------------
for i in range(int(d)):   
    if p != "":
        #Faço um pedido get caso exista um preço máximo então usa o primeiro link, caso contrário o segundo
        response = requests.get("https://rent.inlifehousing.com/api/map/query?city=Lisboa&budgetMax="+ p + "&numTenants=1&bounds=eyJuZSI6eyJsYXQiOjM4Ljc1MDI5MDA0NjEzMzQxNSwibG5nIjotOS4xMTYwNzU4NTQ2MDcwMDR9LCJzdyI6eyJsYXQiOjM4LjcxMDk4Njc3NDUxNjQxNCwibG5nIjotOS4xNjE1NjYxMTk0OTk1ODJ9fQ%3D%3D&sort=recommended&page="+ str(i))
    else:
        response = requests.get("https://rent.inlifehousing.com/api/map/query?city=Lisboa&budgetMax=1600&numTenants=1&bounds=eyJuZSI6eyJsYXQiOjM4Ljc1MDI5MDA0NjEzMzQxNSwibG5nIjotOS4xMTYwNzU4NTQ2MDcwMDR9LCJzdyI6eyJsYXQiOjM4LjcxMDk4Njc3NDUxNjQxNCwibG5nIjotOS4xNjE1NjYxMTk0OTk1ODJ9fQ%3D%3D&sort=recommended&page=" + str(i))

    data = json.loads(response.text)

    #filtragem para apenas os quartos
    lista = data["hits"]

    for dic in lista:
        #verificação por zonas
        if dic["neighborhood"] == zona:
            nResults = nResults + 1
            test = {
                'title' : dic["title"]["en"],
                'price' : dic["maxRent"],
                'link' : "https://rent.inlifehousing.com/house/" + dic["id"] + "/" + dic["room_id"]
            }
            listaFinal.append(test)

# ------------------------------------------------ uniPlaces ---------------------------------------------------
for i in range(int(d)):   
    if i == 1:
        #Se for a primeira página usa o primeiro link, no resto usa o segundo
        response = requests.get("https://www.uniplaces.com/_next/data/search-29efaf2d1333640e4f90563df7c597293d8e3386/en/accommodation/lisbon.json?city=lisbon")
    else:
        response = requests.get("https://www.uniplaces.com/_next/data/search-29efaf2d1333640e4f90563df7c597293d8e3386/en/accommodation/lisbon.json?page="+ str(i) +"&city=lisbon")

    data = json.loads(response.text)

    #filtragem para apenas os quartos
    lista = data["pageProps"]["offers"]["data"]

    for dic in lista:

        #Obter o preço do quarto, no json os preços estão como 60000 = 600
        price = int(dic["attributes"]["accommodation_offer"]["price"]["amount"])/100

        #filtragem por preço e zona
        if price <= int(p):
            try:
                if dic["attributes"]["property"]["neighbourhood"]["name"] == zona:
                    nResults = nResults + 1
                    test = {
                        'title' : dic["attributes"]["accommodation_offer"]["title"],
                        'price' : price,
                        'link' : "https://www.uniplaces.com/accommodation/lisbon/" + dic["id"]
                    }
                    listaFinal.append(test)
            except:
                pass
# ------------------------------------------------ SpotaHome ---------------------------------------------------

#Corpo do pedido POST com a query no final
myObj = {
  "operationName": "Markers",
  "variables": {
    "cityId": "lisbon",
    "filters": {
      "bed": "",
      "budget": "",
      "contractDurationTypesAllowed": "",
      "page": 1,
      "noDeposit": 0,
      "instantBooking": 0,
      "plan": "",
      "poiLat": None,
      "poiLng": None,
      "verified": 0,
      "isBestChoice": 0,
      "sortBy": "DataScience-model5-exploration",
      "flexibleMoveIn": 1,
      "flexibleMoveOut": 1,
      "bathrooms": [],
      "features": [],
      "moveIn": "",
      "moveOut": "",
      "rentalType": [],
      "topology": [],
      "type": [],
      "ids": [],
      "areaId": [],
      "moveOutFrom": "",
      "moveOutTo": "",
      "moveInFrom": "",
      "moveInTo": ""
    }
  },
  "query": "query Markers($cityId: String!, $filters: FiltersInput) {\n  search(cityId: $cityId, filters: $filters) {\n    markers {\n      id\n      coord\n      instantBooking\n      minimumPrice\n    }\n  }\n}\n"
}

response = requests.post("https://www.spotahome.com/marketplace/graphql", json = myObj)

data = json.loads(response.text)

lista = data["data"]["search"]["markers"]

#No Spotahome temos uma lista com mais de 4000 quartos. Dito isto é dificil percorrer tudo e calcular a zona com as coordenadas (demoraria demasiado tempo), como tal dividi a lista em 20. Por volta de 200 quartos
#Este número pode ser aumentado mas vai demorar muito mais tempo
shortList = lista[:len(lista) // 20]

for x in shortList:
    #Primeiro filtramos por preço, e depois vamos buscar as coordenadas de cada quarto e vemos a zona
    if int(x["minimumPrice"]) <= int(p):
        location = x["coord"]
        Latitude = str(location[1])
        Longitude = str(location[0])

        #geolocator.reverse(Latitude+","+Longitude) retorna uma morada completa, nr de porta, rua, bairro, etc. Querendo apenas o bairro de lisboa, notei que o bairro aparece sempre na 4ª posição a contar de trás
        bairro = str(geolocator.reverse(Latitude+","+Longitude)).split(",")[-4]

        if bairro.replace(" ","") == zona:
        
            test = {
                'title' : "SpotAHome",
                'price' : x["minimumPrice"],
                'link' : "https://www.spotahome.com/pt/lisbon/for-rent:rooms/" + str(x["id"])
            }
            listaFinal.append(test)
            nResults = nResults + 1

# ------------------------------------------------ Livensa ---------------------------------------------------

#No Livensa toda a informção é estática como tal, aqui vai esta javardice...

preco = int(p)
if zona == "Cidade Universitária" or zona =="Campo Grande" or zona == "Entre Campos":
    if preco >= 567:
        nResults = nResults + 1
        test = {
        'tile' : "Twin Standard - LivensaLiving",
        'price': 567,
        'link' : "https://www.livensaliving.com/en/student-accommodation-lisboa/student-accommodation-lisboa-cidade-universitaria/rooms-prices/"
        }
        listaFinal.append(test)
    if preco >= 638:
        nResults = nResults + 1
        test = {
        'tile' : "Twin Standard with Terrace - LivensaLiving",
        'price': 638,
        'link' : "https://www.livensaliving.com/en/student-accommodation-lisboa/student-accommodation-lisboa-cidade-universitaria/rooms-prices/"
        }
        listaFinal.append(test)
    if preco >= 819:
        nResults = nResults + 1
        test = {
        'tile' : "Standard - LivensaLiving",
        'price': 819,
        'link' : "https://www.livensaliving.com/en/student-accommodation-lisboa/student-accommodation-lisboa-cidade-universitaria/rooms-prices/"
        }
        listaFinal.append(test)
    if preco >= 934:
        nResults = nResults + 1
        test = {
        'tile' : "Standard with Terrace - LivensaLiving",
        'price': 934,
        'link' : "https://www.livensaliving.com/en/student-accommodation-lisboa/student-accommodation-lisboa-cidade-universitaria/rooms-prices/"
        }
        listaFinal.append(test)
    if preco >= 989:
        nResults = nResults + 1
        test = {
        'tile' : "Superior with Terrace - LivensaLiving",
        'price': 989,
        'link' : "https://www.livensaliving.com/en/student-accommodation-lisboa/student-accommodation-lisboa-cidade-universitaria/rooms-prices/"
        }
        listaFinal.append(test)
    if preco >= 1095:
        nResults = nResults + 1
        test = {
        'tile' : "Premium with Terrace - LivensaLiving",
        'price': 1095,
        'link' : "https://www.livensaliving.com/en/student-accommodation-lisboa/student-accommodation-lisboa-cidade-universitaria/rooms-prices/"
        }
        listaFinal.append(test)
    if preco >= 1530:
        nResults = nResults + 1
        test = {
        'tile' : "Super Premium - LivensaLiving",
        'price': 1530,
        'link' : "https://www.livensaliving.com/en/student-accommodation-lisboa/student-accommodation-lisboa-cidade-universitaria/rooms-prices/"
        }
        listaFinal.append(test)
    
if z == "Marquês de Pombal":
    if preco >= 721:
        nResults = nResults + 1
        test = {
        'tile' : "Twin Standard - LivensaLiving",
        'price': 721,
        'link' : "https://www.livensaliving.com/pt/residencias-estudantes-lisboa/residencia-estudantes-lisboa-marques-de-pombal/quartos-precos/"
        }
        listaFinal.append(test)
    if preco >= 820:
        nResults = nResults + 1
        test = {
        'tile' : "Standard - LivensaLiving",
        'price': 638,
        'link' : "https://www.livensaliving.com/pt/residencias-estudantes-lisboa/residencia-estudantes-lisboa-marques-de-pombal/quartos-precos/"
        }
        listaFinal.append(test)
    if preco >= 930:
        nResults = nResults + 1
        test = {
        'tile' : "Superior - LivensaLiving",
        'price': 930,
        'link' : "https://www.livensaliving.com/pt/residencias-estudantes-lisboa/residencia-estudantes-lisboa-marques-de-pombal/quartos-precos/"
        }
        listaFinal.append(test)
    if preco >= 1040:
        nResults = nResults + 1
        test = {
        'tile' : "Premium - LivensaLiving",
        'price': 1040,
        'link' : "https://www.livensaliving.com/pt/residencias-estudantes-lisboa/residencia-estudantes-lisboa-marques-de-pombal/quartos-precos/"
        }
        listaFinal.append(test)
    if preco >= 1425:
        nResults = nResults + 1
        test = {
        'tile' : "Superior Premium - LivensaLiving",
        'price': 1425,
        'link' : "https://www.livensaliving.com/pt/residencias-estudantes-lisboa/residencia-estudantes-lisboa-marques-de-pombal/quartos-precos/"
        }
        listaFinal.append(test)
    if preco >= 1546:
        nResults = nResults + 1
        test = {
        'tile' : "Premium with Terrace - LivensaLiving",
        'price': 1546,
        'link' : "https://www.livensaliving.com/pt/residencias-estudantes-lisboa/residencia-estudantes-lisboa-marques-de-pombal/quartos-precos/"
        }
        listaFinal.append(test)
    if preco >= 1656:
        nResults = nResults + 1
        test = {
        'tile' : "Super Premium with Terrace - LivensaLiving",
        'price': 1656,
        'link' : "https://www.livensaliving.com/pt/residencias-estudantes-lisboa/residencia-estudantes-lisboa-marques-de-pombal/quartos-precos/"
        }
        listaFinal.append(test)

#--------------------------------------------- FIM -----------------------------------------

#Aqui passo a listaFinal para um dicionario que depois formato para ficar com o formato bonito do Json
dic = {"results" : listaFinal}
json_string = json.dumps(dic,indent=4)

#Escrever para o ficheiro
#ATENÇÃO: Caso não tenham o ficheiro criem o ficheiro antes ou assim, apenas consegui por isto a funcionar assim. Se conseguirem mudar, estejam à vontade!
with open('results.json', 'w') as outfile:
    outfile.write(json_string)

fim = time.time()
print("Tempo: " + str(int(fim) - int(inicio)) + "segundos")
print("FIM! " + str(nResults) + " resultados encontrado!")
