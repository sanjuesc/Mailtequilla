import mysql.connector


def crearCon():
    datos = []
    file = open('datosTexto.txt')
    for line in file:
        datos.append(str(line.strip()))

    return mysql.connector.connect(host=datos[0], user=datos[1], passwd=datos[2], db=datos[3])


def importarTexto(valor):
    respuesta = ""
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("SELECT valor FROM mensajes where nombre = %s", (valor,))
    for response in cur:
        respuesta = str(response[0])
    cur.close()
    conn.close()

    return respuesta


def setEstado(userId, estado):
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("update estados set estado=%s where id =%s", (estado, userId,))
    conn.commit()
    cur.close()
    conn.close()


def getEstado(userId):
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("select estado from estados where id =%s", (userId,))
    for response in cur:
        respuesta = int(response[0])
    cur.close()
    conn.close()
    return respuesta


def existe(userId):
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("select * from estados where id=%s", (userId,))
    cuantas = cur.rowcount
    cur.close()
    conn.close()

    return cuantas > 0


def registrar(userId):
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("insert into estados(id) values (%s)", (userId,))
    conn.commit()
    cur.close()
    conn.close()
