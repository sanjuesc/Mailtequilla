import telegram
from telegram.ext import Updater, MessageHandler, Filters
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
import logging
from telegram.ext import CommandHandler
from utilsBot import importarTexto, setEstado, existe, registrar, getEstado

import os
import io

import datuBase as dbKud

global estado

'''
    Estado 0: despues de estar, hemos elegido cuenta existente/nueva y segun eso se pide el usuario
        Camino cuenta nueva:
            Estado 1: Le hemos dado a crear cuenta nueva y se nos ha pedido el usuario, lo recogemos y pedimos la pass
            Estado 2: Se nos ha pedido la pass, la recogemos y si todo esta bien ejecutamos los comandos que toque
        Camino cuenta existente:
            Estado 3: Iniciar sesion en cuenta existente-->
                Subestado 4: escribiendo nombre
                Subestado 5: escribiendo pasahitza
            Estado 6: menu de botones (leer emails, enviar, blabla, cerrar sesion)
                Subestado 7: el usuario ha elegido "Enviar mensaje" y está escribiendo el mensaje
'''


##cambiar todas las strings a variables que se carguen de la base de datos con importarTexto()

def start(update: Update, context: CallbackContext):
    global estado
    user = update.message.from_user
    print('You talk with user {} and his user ID: {} '.format(user['username'], user['id']))
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bienvenido!!\nAl usar este bot de mail aceptas el <a href='https://drive.google.com/file/d/1_hGSSyVd-cpAu8lzSboCZmO6eeOUrqzC/view?usp=sharing'>contrato de uso</a>"+
                    "\nEsperemos que disfrutes de la aplicación\nCualquier problema contactar con el equipo de diseñadores al contacto: morcilla@servidoras.xyz",
                    parse_mode=telegram.ParseMode.HTML)
    if str(update.message.from_user['id']) in ids:
        buttons = [[KeyboardButton(importarTexto("cuentaExistente"))], [KeyboardButton(importarTexto("cuentaNueva"))]]
        context.bot.send_message(chat_id=update.effective_chat.id, text=importarTexto("saludo"),
                                 reply_markup=ReplyKeyboardMarkup(buttons))
        if not existe(update.message.from_user.id):
            registrar(update.message.from_user.id)
        else:
            setEstado(update.message.from_user.id, 0)

        dbKud.borrarCuentaActual(update.message.from_user.id)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Lo siento pero esta cuenta no cumple los "
                                                                        "requisitos para usar el programa...")


# https://www.py4u.net/discuss/229447

def queDeseaHacer(update: Update, context: CallbackContext):
    setEstado(update.message.from_user.id, 6)
    buttons = [[KeyboardButton("Ver mensajes")],
               [KeyboardButton("Enviar mensaje")],
               [KeyboardButton("Cambiar de cuenta")],
               [KeyboardButton("Cerrar sesión")]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Que deseas hacer",
                             reply_markup=ReplyKeyboardMarkup(buttons))


def registrarUsuario(update: Update, context: CallbackContext):
    usuario = update.message.text
    uID = update.message.chat_id
    if dbKud.comprobarUsuario(usuario):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Ese usuario está añadido")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Prueba con otro nombre distinto por favor")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Que contraseña deseas usar")
        os.system('echo "' + str(usuario) + '" > erabTmp/' + str(uID))
        setEstado(update.message.from_user.id, 2)


def registrarPasahitzaUsuario(update: Update, context: CallbackContext):
    contraseña = update.message.text
    uID = update.message.chat_id
    context.bot.deleteMessage(message_id=update.message.message_id, chat_id=update.effective_chat.id)
    context.bot.send_message(chat_id=update.effective_chat.id, text="La cuenta ha sido creada")
    with open('./erabTmp/' + str(uID)) as f:
        variableUsuario = f.readline().rstrip()
    variableUsuario = variableUsuario.replace('\n', '')
    os.system('echo "' + variableUsuario + '@servidoras.xyz root" >> /etc/postfix/virtual')
    os.system('echo "' + variableUsuario + '@servidoras.xyz root@servidoras.xyz" >> /etc/postfix/recipient_cc_maps')
    os.system('sudo postmap /etc/postfix/virtual')
    os.system('sudo postmap /etc/postfix/recipient_bcc_maps')
    os.system('sudo systemctl restart postfix')
    dbKud.meterUsuario(variableUsuario, contraseña)
    dbKud.crearSesion(update.message.from_user.id, variableUsuario)
    os.system('rm erabTmp/' + str(uID))
    ##intentar crear el usuario y si esta bien hacerlo
    setEstado(update.message.from_user.id, 0)


def iniciarCuentaExistente(update: Update, context: CallbackContext):
    # si el texto no es "Iniciar sesion con una cuenta existente", llevarle a un metodo que le pregunta que quiere
    # hacer (leer emails, enviar, blabla, cerrar sesion)
    # si es "Iniciar sesion" llevar a un metodo que inicie la sesion y despues de ese metodo al mencionado arriba
    if "Iniciar sesion en cuenta existente" in update.message.text:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Introduce tu nombre de usuario")
        setEstado(update.message.from_user.id, 4)
    else:
        usuario = update.message.text
        dbKud.setCuentaActual(update.message.from_user.id, usuario)
        queDeseaHacer(update, context)


def iniciarUsuario(update: Update, context: CallbackContext):
    usuario = update.message.text
    uID = update.message.chat_id
    os.system('echo "' + str(usuario) + '" > erabTmp/' + str(uID))
    context.bot.send_message(chat_id=update.effective_chat.id, text="Introduce tu contraseña")
    setEstado(update.message.from_user.id, 5)


def iniciarPasahitzaUsuario(update: Update, context: CallbackContext):
    contraseña = update.message.text
    uID = update.message.chat_id
    context.bot.deleteMessage(message_id=update.message.message_id, chat_id=update.effective_chat.id)
    with open('./erabTmp/' + str(uID)) as f:
        variableUsuario = f.readline().rstrip()
    variableUsuario = variableUsuario.replace('\n', '')
    existe = dbKud.iniciarSesion(variableUsuario, contraseña)
    if existe:
        dbKud.crearSesion(update.message.from_user.id, variableUsuario)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sesión iniciada correctamente")
        dbKud.setCuentaActual(update.message.from_user.id, variableUsuario)
        queDeseaHacer(update, context)

    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="No ha sido posible iniciar sesión con esos credenciales")


def descifrarMensaje(update: Update, context: CallbackContext):
    atalak = []
    buf = io.StringIO(update.message.text)
    try:
        # gaia
        gaia = buf.readline()
        gaiaGarbi = gaia.replace('tema: ', '')
        assert (gaia != gaiaGarbi)
        gaiaGarbi = gaiaGarbi.replace('\n', '')
        atalak.append(gaiaGarbi)

        # hartzaile
        hartzaile = buf.readline()
        hartzaileGarbi = hartzaile.replace('hartzaile: ', '')
        assert (hartzaile != hartzaileGarbi)
        hartzaileGarbi = hartzaileGarbi.replace('\n', '')
        atalak.append(hartzaileGarbi)

        # mezua
        mezua = "Mensaje:\n"
        mezua += buf.readline()
        atalak.append(mezua)

        return atalak
    except:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="<b>por favor escriba el modelo correctamente:</b> \n" +
                                      "tema: tema del correo\n" +
                                      "hartzaile: erabiltzaile@domeinu.com\n" +
                                      "texto a escribir...")


def messageHandler(update: Update, context: CallbackContext):
    ##TODO: metodoak txikitu daitezke
    if getEstado(update.message.from_user.id) == 1:  # Paso 1 registrar
        registrarUsuario(update, context)

    elif getEstado(update.message.from_user.id) == 2:  # Paso 2 poner contraseña
        registrarPasahitzaUsuario(update, context)

    elif getEstado(update.message.from_user.id) == 3:
        # si el texto no es "Iniciar sesion con una cuenta existente", llevarle a un metodo que le pregunta que quiere
        # hacer (leer emails, enviar, blabla, cerrar sesion)
        # si es "Iniciar sesion" llevar a un metodo que inicie la sesion y despues de ese metodo al mencionado arriba
        iniciarCuentaExistente(update, context)

    elif getEstado(update.message.from_user.id) == 4:  # Paso 4 escribe usuario(existente)
        iniciarUsuario(update, context)

    elif getEstado(update.message.from_user.id) == 5:  # Paso 5 poner contraseña
        iniciarPasahitzaUsuario(update, context)

    elif getEstado(update.message.from_user.id) == 6:
        # paso 6 aukera sorta atera zaionean eta erabiltzaileak hoietako bat idatzi badu
        print(dbKud.getCuentaActual(update.message.from_user.id))
        if "Cambiar de cuenta" in update.message.text:
            dbKud.borrarCuentaActual(update.message.from_user.id)
            buttons = []
            cuentas = dbKud.conseguirCuentas(
                update.message.from_user.id)  # metodo que devuelve una lista con el nombre de las cuentas
            for cuenta in cuentas:
                buttons.append([KeyboardButton(str(cuenta))])
            buttons.append([KeyboardButton("Iniciar sesion en cuenta existente")])
            setEstado(update.message.from_user.id, 3)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Elige una cuenta",
                                     reply_markup=ReplyKeyboardMarkup(buttons))

        elif "Cerrar sesión" in update.message.text:
            dbKud.cerrarSesion(update.message.from_user.id, dbKud.getCuentaActual(update.message.from_user.id))
            dbKud.borrarCuentaActual(update.message.from_user.id)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Sesión cerrada correctamente. \n" +
                                          "Por favor introduce /start para volver al menú principal")
            setEstado(update.message.from_user.id, 0)

        elif "Ver mensajes" in update.message.text:
            usuario = dbKud.getCuentaActual(update.message.from_user.id)
            off = dbKud.getOffset(update.message.from_user.id)
            emailLista = dbKud.getEmailak(usuario, off)
            if emailLista:
                for response in emailLista:
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="<b>Asunto:</b>" + response[2] + "\n<b>De:</b> " + response[0] + "\n<b>Fecha: </b>" + str(response[3]) +"\n<b>Mensaje:</b> " + response[1],
                                             parse_mode=telegram.ParseMode.HTML)
                    buttons = [[KeyboardButton("Ver mas")],
                               [KeyboardButton("Volver")]]
                context.bot.send_message(chat_id=update.effective_chat.id, text="Que deseas hacer",
                                         reply_markup=ReplyKeyboardMarkup(buttons))
                setEstado(update.message.from_user.id, 8)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="No tienes ningun mensaje :(")
                dbKud.resetOffset(update.message.from_user.id)
                queDeseaHacer(update, context)

            #hacer la opcion de ver mas y entonces actualizar el offset y volver a enviarle los mensajes
            # tambien la opcion de volver, que en ese caso el offset vuelve a ser 0
        elif "Enviar mensaje" in update.message.text:
            cancelar = [[KeyboardButton("Cancelar")]]

            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="<b>mensaje modelo:</b> \n" +
                                          "tema: tema del correo\n" +
                                          "hartzaile: erabiltzaile@domeinu.com\n" +
                                          "texto a escribir...",
                                     parse_mode=telegram.ParseMode.HTML,
                                     reply_markup=ReplyKeyboardMarkup(cancelar))
            setEstado(update.message.from_user.id, 7)


    elif getEstado(update.message.from_user.id) == 7:  # escribiendo un correo
        if "Cancelar" in update.message.text:
            queDeseaHacer(update, context)
        else:
            try:
                mezuMetadatuak = descifrarMensaje(update, context)
                os.system('echo "' + str(mezuMetadatuak[2]) + '" > mezuTmp/' + str(update.message.chat_id))

                # cat elFicheroDelMensaje | mail -s "Asunto" -r nork@servidoras.xyz nori@loquesea.holi
                print(
                    'cat mezuTmp/' + str(update.message.chat_id) +
                    ' | mail -s "' + str(mezuMetadatuak[0]) +  # gaia
                    '" -a "From: ' + str(dbKud.getCuentaActual(update.message.chat_id)).capitalize() +  # nork idatzi
                    ' <' + str(dbKud.getCuentaActual(update.message.chat_id)) +
                    '@servidoras.xyz>" ' + mezuMetadatuak[1]
                )

                os.system(
                    'cat mezuTmp/' + str(update.message.chat_id) +
                    ' | mail -s "' + str(mezuMetadatuak[0]) +  # gaia
                    '" -a "From: ' + (str(dbKud.getCuentaActual(update.message.chat_id))).capitalize() +  # nork idatzi
                    ' <' + str(dbKud.getCuentaActual(update.message.chat_id)) +
                    '@servidoras.xyz>" ' + mezuMetadatuak[1]
                )
                os.system('rm mezuTmp/' + str(update.message.chat_id))

                # datu basean sartu
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="Mensaje enviado correctamente")

                queDeseaHacer(update, context)
            except TypeError as nt:
                # mezua ez bada ondo bidali errore hau botako du pythonek eta paso egingo da
                pass
    elif getEstado(update.message.from_user.id) == 8:  # escribiendo un correo
        if "Ver mas" in update.message.text:
            dbKud.eguneratuOffset(update.message.from_user.id)
            usuario = dbKud.getCuentaActual(update.message.from_user.id)
            off = dbKud.getOffset(update.message.from_user.id)
            emailLista = dbKud.getEmailak(usuario, off)
            if emailLista:
                for response in emailLista:
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="<b>Asunto:</b>" + response[2] + "\n<b>De:</b> " + response[0] + "\n<b>Fecha: </b>" + str(response[3]) +"\n<b>Mensaje:</b> " + response[1],
                                             parse_mode=telegram.ParseMode.HTML)
                    buttons = [[KeyboardButton("Ver más")],
                               [KeyboardButton("Volver")]]
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Qué deseas hacer",
                                             reply_markup=ReplyKeyboardMarkup(buttons))
                    setEstado(update.message.from_user.id, 8)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="No tienes mas mensajes :(")
                dbKud.resetOffset(update.message.from_user.id)
                queDeseaHacer(update, context)

        else:
            dbKud.resetOffset(update.message.from_user.id)
            queDeseaHacer(update, context)

    if getEstado(update.message.from_user.id) == 0:
        if importarTexto("cuentaNueva") in update.message.text:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Que nombre de usuario desear tener")
            setEstado(update.message.from_user.id, 1)
        if importarTexto("cuentaExistente") in update.message.text:
            buttons = []
            cuentas = dbKud.conseguirCuentas(
                update.message.from_user.id)  # metodo que devuelve una lista con el nombre de las cuentas
            for cuenta in cuentas:
                buttons.append([KeyboardButton(str(cuenta))])
            buttons.append([KeyboardButton("Iniciar sesion en cuenta existente")])
            setEstado(update.message.from_user.id, 3)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Elige una cuenta",
                                     reply_markup=ReplyKeyboardMarkup(buttons))


file = open('token.txt')
for line in file:
    fields = line.strip().split()
ids = []
file = open('ids.txt')
for line in file:
    ids.append(str(line.strip()))
updater = Updater(token=fields[0], use_context=True)
print(fields[0])
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

dispatcher.add_handler(MessageHandler(Filters.text, messageHandler))
updater.start_polling()