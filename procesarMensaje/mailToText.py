import mysql.connector

def parseatuOrdua(s):
    listaOrdua = list(s)
    return listaOrdua[0] + listaOrdua[1] + ':' + listaOrdua[2] + listaOrdua[3] + ':' + listaOrdua[4] + listaOrdua[5]

def parseatuHila(s):
    listaHila = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    emaitza = 1
    for hil in listaHila:
        if hil == s:
            break
        emaitza += 1
    return emaitza

def dataParseatu(s):
    dataLista = s.split(" ")
    eguna = dataLista[2]
    hila = parseatuHila(dataLista[3]) #Parseatu behar da
    urtea = dataLista[4]
    ordua = parseatuOrdua(dataLista[5]) #Parseatu behar da
    return str(urtea) + '-' + str(hila) + '-' + str(eguna) + ' ' + ordua
datos = []
file = open('../datosSQL.txt')
for line in file:
    datos.append(str(line.strip()))

conn = mysql.connector.connect(host=datos[0], user=datos[1], passwd=datos[2], db=datos[3])
cur = conn.cursor()
#Fitxategia irakurri
f = open("procesarMensaje/email.txt", "r")
lineas = f.readlines()

#Elementuak hasieratu
hartzailea = ""
igorlea = ""
gaia = ""
mezua = ""
data = ""
ordua = ""
txibatoa = False

mezurik = True #True bada mezu berria egongo da eta dban sartuko da
i = 0

for linea in lineas:
    if "No mail for " in linea:
        mezurik = False
        break
    if txibatoa and i < len(lineas) - 2:
        mezua += linea

    if ("Subject: " in linea) and (gaia == ""):
        gaia = linea.split(":")[1]

    #Igorlea ateratzeko
    if ("From: " in linea) and (igorlea == ""):
        igorlea = linea.split("<")[1].replace(">","")
        igorlea = igorlea.split('@')[0]

    #Hartzailea hartzeko
    if("To: <" in linea) and (hartzailea == ""):
        hartzailea = linea.split("<")[1].replace(">","")
        hartzailea = hartzailea.split('@')[0]
    
    #Data hartzeko
    if ("Date: " in linea) and (data == ""):
        linea = linea.split(":")
        for element in linea[1:4]:
            data += str(element)
        data = dataParseatu(data)

    if("Mensaje:" in linea) and (mezua == ""):
        txibatoa = True

    i += 1
if mezurik: #Mezu berrik badago dban sartuko da
    print('Mezua datu basean sartuko da...')
    print(mezua)
    txibatoa = False
    cur.execute("INSERT INTO BIDALI VALUES(%s,%s,%s,%s,%s,0,0)",(igorlea, hartzailea, mezua, data, gaia,))
    conn.commit()
    cur.close()
    conn.close()

else: 
    print("Ez daukazu mezu berririk")
    txibatoa = False
