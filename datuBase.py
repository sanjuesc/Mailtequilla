import mysql.connector  # Instalatu behar den paketea: mysql-connector-python
import hashlib
import time


def crearCon():
    datos = []
    file = open('datosSQL.txt')
    for line in file:
        datos.append(str(line.strip()))

    return mysql.connector.connect(host=datos[0], user=datos[1], passwd=datos[2], db=datos[3])


##Todas las funciones de abajo va a haber que cambiarlas para como funcione la base de datos
##Mirad utilsBot.py para ver como se hace un preparedstatement

################
# ERABILTZAILE #
################

def comprobarUsuario(user):  # comprueba que exista usuario con nombre user
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("SELECT izena FROM ERABILTZAILE WHERE izena = %s", (user,))
    cuantas = cur.rowcount > 0
    cur.close()
    conn.close()
    return cuantas


def iniciarSesion(izena, hasPass):
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    m = hashlib.sha1(hasPass.encode("utf-8"))
    contra = m.hexdigest()
    cur.execute("select 1 from ERABILTZAILE where izena=%s and pasahitzaSHA1 =%s", (izena, contra,))
    respuesta = cur.rowcount
    cur.close()
    conn.close()
    return respuesta > 0


def meterUsuario(user, hasPass):  # inser usuario con nombre user y pass hasPass
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    m = hashlib.sha1(hasPass.encode("utf-8"))
    contra = m.hexdigest()
    now = time.strftime('%Y-%m-%d')
    cur.execute("INSERT INTO ERABILTZAILE (izena, sortzeData, pasahitzaSHA1) VALUES (%s,%s,%s)", (user, now, contra,))
    conn.commit()
    cur.close()
    conn.close()


################
# AGENDA #
################

def comprobarAgenda(user, lagun):
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("SELECT kontaktu FROM AGENDA WHERE erabIzena = %s AND kontaktu = %s",
                (user, lagun,))  # SELECT kontaktu FROM email.AGENDA WHERE erabIzena = 'admin' AND kontaktu = 'test'
    return cur.fetchall()


def recogerContactos(user):
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("SELECT kontaktu, gakoPub FROM AGENDA WHERE erabIzena = %s",
                (user,))  # SELECT kontaktu, gakoPub FROM email.AGENDA WHERE erabIzena = 'amdin';
    zerrenda = []
    zerrendaI = []
    zerrendaG = []
    for izena, gakoP in cur.fetchall():
        zerrendaI.append(0, izena)  # Kontaktuaren izena
        zerrendaG.append(1, gakoP)  # Kontaktuaren gako publikoa
    zerrenda.append(zerrendaI)
    zerrenda.append(zerrendaG)
    return zerrenda


def insertAgendan(user, izena, gakoP):
    # Konprobatu ea agendan daukan ala ez
    if comprobarAgenda(user, izena):  # Quiero creer que aqui entra si hay resultado
        return 1
    else:
        conn = crearCon()
        cur = conn.cursor(buffered=True)
        cur.execute("INSERT INTO AGENDA (erabIzena, kontaktu, gakoPub) VALUES (%s,%s,%s)", (user, izena,
                                                                                            gakoP,))  # INSERT INTO `email`.`AGENDA` (`erabIzena`, `kontaktu`, `gakoPub`) VALUES ('admin', 'test', '1312');
        return 0


def deleteFromAgenda(user, izena):
    if comprobarAgenda(user, izena):  # Quiero creer que aqui entra si hay resultado
        conn = crearCon()
        cur = conn.cursor(buffered=True)
        cur.execute("DELETE FROM AGENDA WHERE (erabIzena = %s) and (kontaktu = %s)",
                    (user,
                     izena,))  # DELETE FROM `email`.`AGENDA` WHERE (`erabIzena` = 'admin') and (`kontaktu` = 'test');


################
# BIDALI #
################

def getEmailak(user, off):
    # erabiltzailearen email guztiak
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("SELECT nork, mezu, gaia, noiz FROM BIDALI WHERE nori = %s order by noiz DESC LIMIT %s, 4", (user, int(off),))
    mezuak = cur.fetchall()
    return mezuak


def bidaliEmail(user, nori, mezua, gaia):
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    cur.execute("INSERT INTO `BIDALI` (`nork`, `nori`, `mezu`, `noiz`, `gaia`) VALUES (%s, %s, %s, %s, %s)",
                (user, nori, mezua, now,
                 gaia,))  # INSERT INTO `email`.`BIDALI` (`nork`, `nori`, `mezu`, `noiz`, `gaia`) VALUES ('pingo', 'admin', 'awdawdaw', '2000-11-11', 'proba')
    conn.commit()
    cur.close()
    conn.close()


################
# SESION #
################

def crearSesion(userId, izena):
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("INSERT INTO SESION VALUES (%s,%s)", (userId, izena,))
    conn.commit()
    cur.close()
    conn.close()


def conseguirCuentas(userId):  # Devuelve las sesiones abiertas del usuario userId
    sesion = []
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("select izena from SESION where userId =%s", (userId,))
    for response in cur:
        sesion.append(str(response[0]))
    cur.close()
    conn.close()
    return sesion


def cerrarSesion(userId, actual):
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("DELETE FROM SESION WHERE  userID = %s and izena = %s", (userId, actual,))
    conn.commit()
    cur.close()
    conn.close()


################
# CUENTAACTUAL #
################

def setCuentaActual(userId, usuario):
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("INSERT INTO `CUENTAACTUAL` (`userID`, `izena`) VALUES (%s,%s)",
                (userId, usuario,))  # INSERT INTO `email`.`CUENTAACTUAL` (`userID`, `izena`) VALUES ('980', 'jojo')
    conn.commit()
    cur.close()
    conn.close()


def getCuentaActual(userId):
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("select izena from CUENTAACTUAL where userID =%s", (userId,))
    for response in cur:
        respuesta = str(response[0])
    cur.close()
    conn.close()
    return respuesta


def borrarCuentaActual(userId):
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("DELETE FROM CUENTAACTUAL WHERE  userID = %s", (userId,))
    conn.commit()
    cur.close()
    conn.close()


def getOffset(userId):
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("SELECT offset FROM CUENTAACTUAL WHERE userID = %s",
                (userId,))  # SELECT offset FROM email.CUENTAACTUAL WHERE izena='duxon'
    for response in cur:
        off = str(response[0])
    cur.close()
    conn.close()
    return off


def eguneratuOffset(userId):
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("UPDATE `email`.`CUENTAACTUAL` SET `offset` = `offset`+4 WHERE (`userID` = '%s')",
                (userId,))  # UPDATE `email`.`CUENTAACTUAL` SET `offset` = `offset`+1 WHERE (`userID` = '1328198558')
    conn.commit()
    cur.close()
    conn.close()


def resetOffset(userId):
    conn = crearCon()
    cur = conn.cursor(buffered=True)
    cur.execute("UPDATE `email`.`CUENTAACTUAL` SET `offset` = 0 WHERE (`userID` = '%s')",
                (userId,))  # UPDATE `email`.`CUENTAACTUAL` SET `offset` = `offset`+1 WHERE (`userID` = '1328198558')
    conn.commit()
    cur.close()
    conn.close()