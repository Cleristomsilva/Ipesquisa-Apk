import sqlite3
import mysql.connector
import configparser
from openpyxl import Workbook
from datetime import datetime
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
import os
from jnius import autoclass
import sys

if 'android' in sys.platform:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

class CreateAccountWindow(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)
    Window.clearcolor=[0,0,0,1]

    def __init__(self, usuario='', **kwargs):
        super(CreateAccountWindow, self).__init__(**kwargs)
        self.create_table_usuarios()
        data_hora=datetime.now()
        #chama a função exibir_senha_registrar com parametro check_registrar False
        self.exibir_senha_registrar(False)


    def exibir_senha_registrar(self,check_registrar):
        if self.check_registrar.active:
            self.ids.passw.password=False
        else:
            self.ids.passw.password=True


    def create_table_usuarios(self):
        self.connection = sqlite3.connect('usuarios.db')
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                                email TEXT PRIMARY KEY,
                                password TEXT NOT NULL,
                                data_criacao TEXT NOT NULL
                            )''')
        self.connection.commit()


    def verifica_email_existente(self):
        self.connection = sqlite3.connect('usuarios.db')
        cursor = self.connection.cursor()
        cursor.execute("SELECT email FROM usuarios WHERE email=?", (self.email.text,))
        result = cursor.fetchone()
        self.connection.close()
        if result is not None:
            return True
        else:
            return False


    def criar_tabela_ultimo_usuario(self):
        self.connection = sqlite3.connect('ultimo_usuario.db')
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS ultimo_usuario (
                                id TEXT NOT NULL,
                                email TEXT NOT NULL
                            )''')
        self.connection.commit()


    def atualizar_ultimo_user(self):
        if self.email.text.strip() != '':
            id="1"
            self.connection = sqlite3.connect('ultimo_usuario.db')
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM ultimo_usuario")
            cursor.execute("INSERT INTO ultimo_usuario VALUES (?, ?)", (id,self.email.text.strip(),))
            self.connection.commit()
            self.connection.close()


    def submit(self):
        if self.email.text != "" and self.email.text.count("@") == 1 and self.email.text.count(".") > 0:
            # Verifica se a senha tem pelo menos 8 digitos e contem caracteres especiais, letras e numeros
            if len(self.password.text) >= 8 and any(char.isdigit() for char in self.password.text) and any(char.isalpha() for char in self.password.text) and any(char in '!@#$%^&*()_+-=' for char in self.password.text):
                if self.verifica_email_existente() == False:
                    self.create_table_usuarios()
                    self.connection = sqlite3.connect('usuarios.db')
                    cursor = self.connection.cursor()
                    cursor.execute("INSERT INTO usuarios VALUES (?, ?, ?)", (self.email.text, self.password.text, datetime.now()))
                    self.connection.commit()
                    self.connection.close()
                    sm.current = "login"

                else:
                    largura_popup=Window.width * 0.8
                    altura_popup=Window.height * 0.3
                    content=BoxLayout(orientation='vertical')
                    content.add_widget(Label(text='Email ja existe.',font_size=largura_popup * 0.06))
                    btn_fechar=Button(
                        text='Voltar',size_hint=(None,None),size=(largura_popup * 0.48,altura_popup * 0.2),
                        pos_hint={'center_x':0.5},font_size=largura_popup * 0.04
                        )
                    popup=Popup(
                        title='Erro',content=content,size_hint=(None,None),size=(largura_popup,altura_popup),
                        title_size=altura_popup * 0.08
                        )
                    btn_fechar.bind(on_press=popup.dismiss)
                    content.add_widget(btn_fechar)
                    popup.open()
            else:
                largura_popup=Window.width * 0.8
                altura_popup=Window.height * 0.3
                content=BoxLayout(orientation='vertical')
                content.add_widget(Label(text="Verifique a senha.",font_size=largura_popup * 0.06))
                btn_fechar=Button(
                    text='Voltar',size_hint=(None,None),size=(largura_popup * 0.48,altura_popup * 0.2),
                    pos_hint={'center_x':0.5},font_size=largura_popup * 0.04
                    )
                popup=Popup(
                    title='Erro',content=content,size_hint=(None,None),size=(largura_popup,altura_popup),
                    title_size=altura_popup * 0.08
                    )
                btn_fechar.bind(on_press=popup.dismiss)
                content.add_widget(btn_fechar)
                popup.open()



        else:
            largura_popup=Window.width * 0.8
            altura_popup=Window.height * 0.3
            content=BoxLayout(orientation='vertical')
            content.add_widget(Label(text="Preencha todos\nos campos corretamente.",font_size=largura_popup * 0.06))
            btn_fechar=Button(text='Voltar',size_hint=(None,None),size=(largura_popup * 0.48,altura_popup * 0.2),pos_hint={'center_x':0.5},font_size=largura_popup * 0.04)
            popup=Popup(title='Erro',content=content,size_hint=(None,None),size=(largura_popup,altura_popup),title_size=altura_popup * 0.08)
            btn_fechar.bind(on_press=popup.dismiss)
            content.add_widget(btn_fechar)
            popup.open()


    def login(self):
        self.reset()
        sm.current = "login"


    def reset(self):
        self.email.text = ""
        self.password.text = ""


class LoginWindow(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)
    save_email_switch = ObjectProperty(None)
    Window.clearcolor = [0, 0, 0, 1]


    def __init__(self, **kwargs):
        super(LoginWindow, self).__init__(**kwargs)
        # self.load_last_user()
        self.criar_tabela_ultimo_usuario()
        self.carregar_ultimo_usuario()


    def criar_tabela_ultimo_usuario(self):
        self.connection = sqlite3.connect('ultimo_usuario.db')
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS ultimo_usuario (
                                id TEXT NOT NULL,
                                email TEXT NOT NULL
                            )''')
        self.connection.commit()


    def carregar_ultimo_usuario(self):
        self.connection = sqlite3.connect('ultimo_usuario.db')
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM ultimo_usuario")
        row = cursor.fetchone()
        if row is not None:
            self.email.text=""
            self.email.text = row[1]
            self.connection.close()


    def checkbox_login(self,switch):
        if switch.active:
            App.get_running_app().root.get_screen("login").atualizar_ultimo_usuario()
        else:
            App.get_running_app().root.get_screen("login").atualizar_ultimo_usuario()


    def exibir_senha(self,switch):
        if switch.active:
            self.ids.password.password = False
        else:
            self.ids.password.password = True


    def atualizar_ultimo_usuario(self):
        if self.email.text.strip() != '':
            id="1"
            self.connection = sqlite3.connect('ultimo_usuario.db')
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM ultimo_usuario")
            cursor.execute("INSERT INTO ultimo_usuario VALUES (?, ?)", (id,self.email.text.strip(),))
            self.connection.commit()
            self.connection.close()


    def deletar_ultimo_usuario(self):
        self.connection = sqlite3.connect('ultimo_usuario.db')
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM ultimo_usuario WHERE id = ?",(1,))
        self.connection.commit()
        self.connection.close()


    def loginBtn(self):
        email = self.email.text.strip()
        password = self.password.text.strip()
        self.usuario = email
        self.manager.add_widget(PesquisaWindow(usuario=self.usuario))
        # passa o valor de usuario para main
        main_window = self.manager.get_screen("main")
        main_window.email = email

        if email and password:
            try:
                self.connection = sqlite3.connect('usuarios.db')
                cursor = self.connection.cursor()
                cursor.execute("SELECT * FROM usuarios WHERE email=? AND password=?", (email, password))
                result = cursor.fetchone()
                self.connection.close()
                if result:
                    MainWindow.current = email
                    self.reset()
                    sm.current = "main"
                else:
                    invalidLogin()
            except sqlite3.Error as e:
                print(e)
        else:
            invalidForm(sm)


    def createBtn(self):
        self.reset()
        #chama a função exibir_senha_registra da class createwindow para desabilitar a exibição da senha
        create_window = self.manager.get_screen('create')
        create_window.exibir_senha_registrar(False)
        sm.current = "create"


    def reset(self):
        self.email.text = ""
        self.password.text = ""


class MainWindow(Screen):
    n = ObjectProperty(None)
    created = ObjectProperty(None)
    email = ObjectProperty(None)
    current = ""


    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)


    def verifica_conexao(self):
        conexao_mysql,cursor_mysql=self.conectar_bd_mysql()
        if conexao_mysql:
            largura_popup=Window.width * 0.8
            altura_popup=Window.height * 0.3
            content=BoxLayout(orientation='vertical')
            content.add_widget(Label(text="Conexão estabelecida\ncom sucesso.\nDeseja enviar os dados?", font_size=largura_popup * 0.06))
            button_layout=BoxLayout(orientation='horizontal')
            cancel_button=Button(text='Cancelar',background_color=[1,0,0,1],size_hint=(None,None),size=(largura_popup * 0.48,altura_popup * 0.2))
            confirm_button=Button(text='Confirmar',background_color=[0,1,0,1],size_hint=(None,None),size=(largura_popup * 0.48,altura_popup * 0.2))
            confirm_button.bind(on_press=self.enviar_dados_sqlite_para_mysql)
            confirm_button.bind(on_press=self.dismiss_popup)
            cancel_button.bind(on_press=self.dismiss_popup)
            button_layout.add_widget(confirm_button)
            button_layout.add_widget(cancel_button)
            content.add_widget(button_layout)
            self.popup=Popup(title='Enviar Dados',content=content,size_hint=(None,None),size=(largura_popup,altura_popup), title_size= largura_popup * 0.04)
            self.popup.open()

        else:
            largura_popup=Window.width * 0.8
            altura_popup=Window.height * 0.3
            content=BoxLayout(orientation='vertical')
            content.add_widget(Label(text="Sem conexão\ncom o servidor.\nTente mais tarde.", font_size= largura_popup * 0.06))
            btn_fechar=Button(text='Voltar',size_hint=(None,None),size=(largura_popup * 0.48,altura_popup * 0.2),pos_hint={'center_x':0.5}, font_size= largura_popup * 0.04)
            popup=Popup(title='Erro',content=content,size_hint=(None,None),size=(largura_popup,altura_popup), title_size= largura_popup * 0.04)
            btn_fechar.bind(on_press=popup.dismiss)
            content.add_widget(btn_fechar)
            popup.open()


    def logout(self):
        MainWindow.current = ""
        sm.current = "login"
        if isinstance(sm.current_screen,LoginWindow):
            sm.current_screen.carregar_ultimo_usuario()


    def deletar_ultimo_usuario(self):
        self.connection = sqlite3.connect('ultimo_usuario.db')
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM ultimo_usuario WHERE id = ?",(1,))
        self.connection.commit()
        self.connection.close()


    def tema_login(self,id):
        if id == "tema_inicial":
            Window.clearcolor=[0,0,0,1]  # Define o fundo escuro (RGB: 1, 1, 1)
            self.texto_branco()  # Se o valor for verdadeiro (Switch está ativado)


    def tema_fundo(self,switch,value):
        if switch.active:
            Window.clearcolor=[0,0,0,1]
            self.texto_branco()
        else:
            Window.clearcolor=[1,1,1,1]
            self.texto_preto()

        App.get_running_app().root.get_screen("pesquisa").tema_fundo(switch,value)


    def texto_preto(self):
        for widget in self.children:
            if isinstance(widget,Label) or isinstance(widget,Spinner):
                widget.color=[0,0,0,1]  # Define a cor do texto do Label e Spinner como preto
            elif isinstance(widget,Button):
                widget.color=[1,1,1,1]  # Define a cor do texto do Button como branco


    def texto_branco(self):
        for widget in self.children:
            if isinstance(widget,Label) or isinstance(widget,Spinner):
                widget.color=[1,1,1,1]  # Define a cor do texto do Label e Spinner como branco
            elif isinstance(widget,Button):
                widget.color=[1,1,1,1]  # Define a cor do texto do Button como branco


    def atualizar_tema_label(self,switch,value):
        if switch.active:
            self.ids.tema_label.text="Tema Escuro"
            self.ids.tema_label.color=[1,1,1,1]
        else:
            self.ids.tema_label.text="Tema Claro"
            self.ids.tema_label.color=[0,0,0,1]


    def nova_pesquisa(self):
        sm.current='pesquisa'
        #envia o valor de self.email para a tela de pesquisa
        App.get_running_app().root.get_screen("pesquisa").usuario = self.email
        App.get_running_app().root.get_screen("pesquisa").update_contador()


    def abrir_caixa_compartilhamento(file_path):
        #abrir compartilhamento nativo do celular se platarforma diferente de win32
        if platform.system() != 'Windows':
            from android import mimetypes
            from android.content import Intent
            from jnius import autoclass

            intent = Intent()
            intent.setAction(Intent.ACTION_SEND)
            intent.setType(mimetypes.MIMETYPE_TEXT_PLAIN)
            intent.putExtra(Intent.EXTRA_STREAM, file_path)
            context = autoclass('org.kivy.android.PythonActivity').mActivity
            context.startActivity(Intent.createChooser(intent, 'Compartilhar arquivo'))


    def acessar_pasta_em_downloads(self):
        try:
            pasta = '/storage/emulated/0/Download/Pesquisa/'
            if not os.path.exists(pasta):
                os.makedirs(pasta)
                mensagem = 'Pasta criada com sucesso'
            else:
                mensagem = 'Pasta já existe'
            return mensagem, pasta
        except Exception as e:
            return f"Erro ao acessar a pasta de downloads: {str(e)}", None


    def conectar_bd_local(self):
        try:
            conn_sqlite=sqlite3.connect('pesquisa.db')
            cursor_sqlite=conn_sqlite.cursor()
            return conn_sqlite,cursor_sqlite
        except sqlite3.Error as error:
            return None,error


    def desconectar_bd_local(self,conn_sqlite):
        conn_sqlite.close()


    def conectar_bd_mysql(self):
        try:
            conn_mysql=mysql.connector.connect(
                host="189.17.195.66",
                port=41306,
                user="app",
                password="AppP3squIs@",
                database="app"
                )
            cursor_mysql=conn_mysql.cursor()
            return conn_mysql,cursor_mysql
        except mysql.connector.Error as error:
            return None,error  # Retorna None se houver erro


    def backup_local(self):
        try:
            connection = sqlite3.connect('pesquisa.db')
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM pesquisa')
            rows = cursor.fetchall()

            # Criar um novo arquivo Excel (xlsx)
            workbook = Workbook()
            # Adicionar uma planilha ao arquivo Excel
            sheet = workbook.active
            # Adicionar os cabeçalhos das colunas
            sheet.append(['ID', 'Faixa etária', 'Gênero', 'Escolaridade','Bairro', 'Renda', 'Governo fez', 'O bairro precisa',
                          'Conhece Luciana', 'Conhece Kadu', 'Usuário', 'Data'])
            # Adicionar os dados do banco de dados SQLite ao arquivo Excel
            for row in rows:
                sheet.append(row)

            # Salvar o arquivo Excel no diretório de downloads
            if sys.platform != 'win32':
                mensagem, pasta = self.acessar_pasta_em_downloads()
                if pasta is not None:
                    file_path = os.path.join(pasta, 'pesquisa.xlsx')
                    workbook.save(filename=file_path)
                    workbook.close()
                    # Informar ao usuário que os dados foram exportados
                    largura_popup=Window.width * 0.8
                    altura_popup=Window.height * 0.3
                    content=BoxLayout(orientation='vertical')
                    content.add_widget(Label(text="Os dados foram exportados\npara pesquisa.xlsx\nna pasta de downloads", font_size= largura_popup * 0.06))
                    btn_fechar=Button(
                        text='Fechar',size_hint=(None,None),size=(largura_popup * 0.48,altura_popup * 0.2),
                        pos_hint={'center_x':0.5},font_size=largura_popup * 0.04)
                    popup=Popup(title='Sucesso',content=content,size_hint=(None,None),size=(largura_popup,altura_popup), title_size= largura_popup * 0.04)
                    btn_fechar.bind(on_press=popup.dismiss)
                    content.add_widget(btn_fechar)
                    popup.open()
                    return mensagem, file_path
                else:
                    return "Erro ao exportar dados: Pasta de downloads não acessível", None

            else:
                file_path = 'pesquisa.xlsx'
                workbook.save(filename=file_path)
                workbook.close()  # Feche o arquivo após salvar
                # Informar ao usuário que os dados foram exportados
                largura_popup=Window.width * 0.8
                altura_popup=Window.height * 0.3
                btn_fechar=Button(text='Fechar',size_hint=(None,None),size=(largura_popup * 0.48,altura_popup * 0.2),pos_hint={'center_x': 0.5}, font_size= largura_popup * 0.04)
                content=BoxLayout(orientation='vertical')
                content.add_widget(Label(text="Os dados foram exportados\npara pesquisa.xlsx\nna pasta atual", font_size= largura_popup * 0.06))
                popup=Popup(
                    title='Sucesso',content=content,size_hint=(None,None),size=(largura_popup,altura_popup),
                    title_size=altura_popup * 0.08
                    )
                btn_fechar.bind(on_press=popup.dismiss)
                content.add_widget(btn_fechar)
                popup.open()
                return "Os dados foram exportados para pesquisa.xlsx na pasta atual", file_path

        except sqlite3.Error as e:
            self.show_message("Erro",f"Ocorreu um erro\nao exportar os dados:{e}\nEntre em contato com o suporte")


    def show_message(self,title,message):
        largura_popup=Window.width * 0.8
        altura_popup=Window.height * 0.3

        content=BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message, font_size= largura_popup * 0.04))
        popup=Popup(title=title,content=content,size_hint=(None,None),size=(largura_popup,altura_popup), title_size=altura_popup * 0.08)
        popup.open()


    def enviar_dados_sqlite_para_mysql(self,button):
        try:
            conn_sqlite=sqlite3.connect('pesquisa.db')
            cursor_sqlite=conn_sqlite.cursor()

            # Conectar ao banco de dados MySQL
            conn_mysql=mysql.connector.connect(
                host="endereço do seu banco de dados mysql",
                port=porta,
                user="usuario",
                password="senha",
                database="nome do banco de dados"
                )
            cursor_mysql=conn_mysql.cursor()

            # Recuperar dados do SQLite
            cursor_sqlite.execute('SELECT * FROM pesquisa')
            rows=cursor_sqlite.fetchall()

            # Inserir dados no MySQL
            for row in rows:
                data_without_id=row[1:]
                cursor_mysql.execute(
                    'INSERT INTO pesquisa (idade, genero, escolaridade, bairro, renda, resposta1, resposta2, resposta3, resposta4, usuario, data_pesquisa) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    data_without_id
                    )
            conn_mysql.commit()
            conn_mysql.close()
            conn_sqlite.close()

            altura_popup=Window.height * 0.3
            largura_popup=Window.width * 0.8
            btn_fechar=Button(text='Fechar',size_hint=(None,None),size=(largura_popup * 0.48,altura_popup * 0.2),pos_hint={'center_x':0.5}, font_size= largura_popup * 0.04)
            content=BoxLayout(orientation='vertical')
            content.add_widget(Label(text="Os dados foram enviados\ncom sucesso para o servidor", font_size= largura_popup * 0.06))
            popup=Popup(title='Sucesso',content=content,size_hint=(None,None),size=(largura_popup,altura_popup), title_size= altura_popup * 0.08)
            btn_fechar.bind(on_press=popup.dismiss)
            content.add_widget(btn_fechar)
            popup.open()
        except Exception as e:
            self.show_message("Erro",f"Erro ao enviar os dados:\n{e}\nEntre em contato com o suporte")


    def deletar_banco_de_dados(self):
        largura_popup=Window.width * 0.8
        altura_popup=Window.height * 0.3
        content=BoxLayout(orientation='vertical')
        content.add_widget(Label(text="Tem certeza que deseja\napagar todos os dados?", font_size= largura_popup * 0.06))
        button_layout=BoxLayout(orientation='horizontal')
        confirm_button=Button(text='Confirmar',background_color=[0,1,0,1], size_hint=(None,None),size=(largura_popup * 0.48,altura_popup * 0.2), font_size= largura_popup * 0.04)
        cancel_button=Button(text='Cancelar',background_color=[1,0,0,1], size_hint=(None,None),size=(largura_popup * 0.48,altura_popup * 0.2), font_size= largura_popup * 0.04)
        confirm_button.bind(on_press=self.popup_senha)
        confirm_button.bind(on_press=self.dismiss_popup)
        cancel_button.bind(on_press=self.dismiss_popup)
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)
        content.add_widget(button_layout)
        self.popup=Popup(title='Excluir Dados',content=content,size_hint=(None,None),size=(largura_popup,altura_popup), title_size= largura_popup * 0.04)
        self.popup.open()


    def confirmar_senha_master(self, senha):
        altura_popup=Window.height * 0.3
        largura_popup=Window.width * 0.8
        # Senha de administrador que será solicitada e verificada para apagar os dados do BD local
        if senha == "nivel3tidev":
            self.confirmar_deletar_bd(self.popup)
            altura_popup=Window.height * 0.3
            largura_popup=Window.width * 0.8
            content=BoxLayout(orientation='vertical')
            content.add_widget(Label(text="Dados apagados\ncom sucesso", font_size= largura_popup * 0.06))
            btn_fechar=Button(text='Fechar',size_hint=(None,None),size=(largura_popup * 0.48,altura_popup * 0.2),pos_hint={'center_x':0.5}, font_size= largura_popup * 0.04)
            content.add_widget(btn_fechar)
            popup=Popup(title='Sucesso',content=content,size_hint=(None,None),size=(largura_popup,altura_popup), title_size= altura_popup * 0.08)
            btn_fechar.bind(on_press=popup.dismiss)
            popup.open()
        elif senha == "":
            altura_popup=Window.height * 0.3
            largura_popup=Window.width * 0.8
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text="Por favor, digite uma senha.", font_size= largura_popup * 0.06))
            btn_voltar = Button(text='Voltar', size_hint=(None, None), size=(largura_popup * 0.48, altura_popup * 0.2),pos_hint={'center_x': 0.5}, font_size= largura_popup * 0.04)
            content.add_widget(btn_voltar)
            popup = Popup(title='Erro', content=content, size_hint=(None, None), size=(largura_popup, altura_popup), title_size= altura_popup * 0.08)
            btn_voltar.bind(on_press=popup.dismiss)
            btn_voltar.bind(on_press=self.popup_senha)
            popup.open()
        elif senha != "nivel3tidev":
            altura_popup=Window.height * 0.3
            largura_popup=Window.width * 0.8
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text="Senha inválida", font_size= largura_popup * 0.06))
            btn_voltar = Button(text='Voltar', size_hint=(None, None), size=(largura_popup * 0.48, altura_popup * 0.2), pos_hint={'center_x': 0.5}, font_size= largura_popup * 0.04)
            content.add_widget(btn_voltar)
            popup = Popup(title='Erro', content=content, size_hint=(None, None), size=(largura_popup, altura_popup), title_size= altura_popup * 0.08)
            btn_voltar.bind(on_press=popup.dismiss)
            btn_voltar.bind(on_press=self.popup_senha)
            popup.open()


    def popup_senha(self,button):
        altura_popup=Window.height * 0.3
        largura_popup=Window.width * 0.8

        text_input=TextInput(multiline=False, password=True, hint_text='Digite a senha adm', font_size=largura_popup * 0.06,size_hint=(None,None),size=(largura_popup * 0.8,altura_popup * 0.2),pos_hint={'center_x':0.5,'center_y':0.5})
        confirm_button=Button(
            text='Confirmar',background_color=[0,1,0,1],size_hint=(None,None),
            size=(largura_popup * 0.48,altura_popup * 0.2),font_size=largura_popup * 0.04
            )
        cancel_button=Button(
            text='Cancelar',background_color=[1,0,0,1],size_hint=(None,None),
            size=(largura_popup * 0.48,altura_popup * 0.2),font_size=largura_popup * 0.04)
        confirm_button.bind(on_press=lambda instance:self.confirmar_senha_master(text_input.text))
        confirm_button.bind(on_press=lambda instance:popup.dismiss())
        cancel_button.bind(on_press=lambda instance:popup.dismiss())
        button_layout=BoxLayout(orientation='horizontal')
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)
        content=BoxLayout(orientation='vertical')
        content.add_widget(text_input)
        content.add_widget(button_layout)
        popup=Popup(title='Senha',content=content,size_hint=(None,None),size=(largura_popup,altura_popup), title_size= largura_popup * 0.04)
        popup.open()


    def confirmar_deletar_bd(self,instance):
        self.connection = sqlite3.connect('pesquisa.db')
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM pesquisa')
        self.connection.commit()
        self.connection.close()
        self.dismiss_popup(instance)


    def dismiss_popup(self,instance):
        self.popup.dismiss()


class PesquisaWindow(Screen):

    def __init__(self, usuario='', **kwargs):
        super(PesquisaWindow, self).__init__(**kwargs)

        self.usuario = usuario
        self.connection = sqlite3.connect('pesquisa.db')
        self.create_table()
        self.update_contador()
        self.atualizar_tema_pesquisa('True')


    def tema_fundo(self,switch,value):
        self.atualizar_tema_pesquisa(value)
        if switch.active:
            Window.clearcolor=[0,0,0,1]
        else:
            Window.clearcolor=[1,1,1,1]


    def texto_preto(self):
        for widget in self.ids.layout.children:  # Percorre todos os widgets no layout
            if isinstance(widget,Label) or isinstance(widget,Spinner):
                widget.color=[0,0,0,1]  # Define a cor do texto do Label e Spinner como preto
            elif isinstance(widget,Button):
                widget.color=[1,1,1,1]  # Define a cor do texto do Button como branco


    def texto_branco(self):
        for widget in self.ids.layout.children:  # Percorre todos os widgets no layout
            if isinstance(widget,Label) or isinstance(widget,Spinner):
                widget.color=[1,1,1,1]  # Define a cor do texto do Label e Spinner como branco
            elif isinstance(widget,Button):
                widget.color=[1,1,1,1]


    def atualizar_tema_pesquisa(self,value):
        #tema claro = [1,1,1,1] e tema escuro = [0,0,0,1]
        if value == False:
            #fundo branco
            self.ids.questionario.color=[0,0,0,1]
            self.ids.idade.color=[0,0,0,1]
            self.ids.genero.color=[0,0,0,1]
            self.ids.escolaridade.color=[0,0,0,1]
            self.ids.bairro.color=[0,0,0,1]
            self.ids.renda.color=[0,0,0,1]
            self.ids.pergunta1.color=[0,0,0,1]
            self.ids.pergunta2.color=[0,0,0,1]
            self.ids.pergunta3.color=[0,0,0,1]
            self.ids.pergunta4.color=[0,0,0,1]
            self.ids.contador_label.color=[0,0,0,1]

            self.ids.idade_spinner.color=[1,1,1,1]
            self.ids.genero_spinner.color=[1,1,1,1]
            self.ids.escolaridade_spinner.color=[1,1,1,1]
            self.ids.bairro_spinner.color=[1,1,1,1]
            self.ids.renda_spinner.color=[1,1,1,1]
            self.ids.resposta3_spinner.color=[1,1,1,1]
            self.ids.resposta4_spinner.color=[1,1,1,1]

        elif value == True:
            #fundo preto
            self.ids.questionario.color=[1,1,1,1]
            self.ids.idade.color=[1,1,1,1]
            self.ids.genero.color=[1,1,1,1]
            self.ids.escolaridade.color=[1,1,1,1]
            self.ids.bairro.color=[1,1,1,1]
            self.ids.renda.color=[1,1,1,1]
            self.ids.pergunta1.color=[1,1,1,1]
            self.ids.pergunta2.color=[1,1,1,1]
            self.ids.pergunta3.color=[1,1,1,1]
            self.ids.pergunta4.color=[1,1,1,1]
            self.ids.contador_label.color=[1,1,1,1]

            self.ids.idade_spinner.color=[1,1,1,1]
            self.ids.genero_spinner.color=[1,1,1,1]
            self.ids.escolaridade_spinner.color=[1,1,1,1]
            self.ids.bairro_spinner.color=[1,1,1,1]
            self.ids.renda_spinner.color=[1,1,1,1]
            self.ids.resposta3_spinner.color=[1,1,1,1]
            self.ids.resposta4_spinner.color=[1,1,1,1]


    def salvar_pesquisa(self):
        idade=self.ids.idade_spinner.text
        genero=self.ids.genero_spinner.text
        escolaridade=self.ids.escolaridade_spinner.text
        bairro=self.ids.bairro_spinner.text
        renda=self.ids.renda_spinner.text
        resposta1=self.ids.resposta1_input.text
        resposta2=self.ids.resposta2_input.text
        resposta3=self.ids.resposta3_spinner.text
        resposta4=self.ids.resposta4_spinner.text
        usuario=self.usuario
        data=datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Verifica se todos os campos foram preenchidos
        if idade != 'Selecione a sua idade' \
                and genero != 'Selecione o sexo' \
                and escolaridade != 'Selecione a sua escolaridade' \
                and bairro != 'Selecione o seu bairro' \
                and renda != 'Selecione sua faixa de renda' \
                and resposta1 != '' \
                and resposta2 != '' \
                and resposta3 != 'Selecione sua resposta' \
                and resposta4 != 'Selecione sua resposta':
            try:
                cursor=self.connection.cursor()
                cursor.execute(
                    '''INSERT INTO pesquisa (idade, genero, escolaridade, bairro, renda, resposta1, resposta2, resposta3, resposta4, usuario, data)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',(idade,genero,escolaridade,bairro,renda,resposta1,resposta2,resposta3,resposta4,usuario,data)
                    )
                self.connection.commit()
                self.update_contador()
                self.mostrar_popup('Sucesso','Pesquisa gravada\n com sucesso.')
                self.limpar_inputs()
            except sqlite3.Error as e:
                self.mostrar_popup('Erro',f'Ocorreu um erro\nao gravar a pesquisa: {e}')
        else:
            largura_popup=Window.width * 0.8
            altura_popup=Window.height * 0.3
            btn_voltar=Button(
                text='Voltar',size_hint=(None,None),size=(largura_popup * 0.48,altura_popup * 0.2),
                pos_hint={'center_x': 0.5}, font_size= largura_popup * 0.04)
            content=BoxLayout(orientation='vertical')
            content.add_widget(
                Label(text="Por favor,\npreencha todos os campos\nda pesquisa.", font_size= largura_popup * 0.06,
                      size_hint=(None,None),size=(largura_popup * 0.6,altura_popup * 0.5) ,pos_hint={'center_x':0.5})
                )
            content.add_widget(btn_voltar)
            popup=Popup(title='Erro',content=content,size_hint=(None,None),size=(largura_popup,altura_popup), title_size=altura_popup * 0.08)
            btn_voltar.bind(on_press=popup.dismiss)
            popup.open()


    def update_contador(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM pesquisa')
        count = cursor.fetchone()[0]
        self.ids.contador_label.text=f'Pesquisas registradas:  {count} '


    def mostrar_popup(self,title,message):
        largura_popup=Window.width * 0.8
        altura_popup=Window.height * 0.3
        content=BoxLayout(orientation='vertical')
        content.add_widget(Label(text="Pesquisa gravada\ncom sucesso!", font_size= largura_popup * 0.06))
        btn_encerrar_pesquisas=Button(text='Encerrar Pesquisas',background_color=[1,0,0,1],size_hint=(None,None),size=(largura_popup * 0.9,altura_popup * 0.2),pos_hint={'center_x': 0.5}, font_size= largura_popup * 0.06)
        btn_encerrar_pesquisas.bind(on_release=self.encerrar_pesquisas)
        btn_nova_pesquisa=Button(text='Nova Pesquisa', background_color=[0,1,0,1],size_hint=(None,None),size=(largura_popup * 0.9,altura_popup * 0.2),pos_hint={'center_x': 0.5}, font_size= largura_popup * 0.06)
        btn_nova_pesquisa.bind(on_release=self.nova_pesquisa_btn)
        content.add_widget(btn_encerrar_pesquisas)
        content.add_widget(btn_nova_pesquisa)
        popup=Popup(title='Sucesso',content=content,size_hint=(None,None),size=(largura_popup,altura_popup), title_size=altura_popup * 0.08)
        btn_encerrar_pesquisas.bind(on_press=popup.dismiss)
        btn_nova_pesquisa.bind(on_press=popup.dismiss)
        popup.open()


    def encerrar_pesquisas(self,instance):
        # Redireciona para a MainWindow
        self.manager.current="main"


    def nova_pesquisa_btn(self,instance):
        self.manager.get_screen('pesquisa').usuario=self.usuario


    def limpar_inputs(self):
        self.ids.idade_spinner.text='Selecione a sua idade'
        self.ids.genero_spinner.text='Selecione o sexo'
        self.ids.escolaridade_spinner.text='Selecione a sua escolaridade'
        self.ids.bairro_spinner.text='Selecione seu bairro'
        self.ids.renda_spinner.text='Selecione sua faixa de renda'
        self.ids.resposta1_input.text=''
        self.ids.resposta2_input.text=''
        self.ids.resposta3_spinner.text='Selecione sua resposta'
        self.ids.resposta4_spinner.text='Selecione sua resposta'


    def cancelar_pesquisa(self):
        self.limpar_inputs()
        self.update_contador()
        sm.current = "main"


    def create_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS pesquisa (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            idade TEXT,
                            genero TEXT,
                            escolaridade TEXT,
                            bairro TEXT,
                            renda TEXT,
                            resposta1 TEXT,
                            resposta2 TEXT,
                            resposta3 TEXT,
                            resposta4 TEXT,
                            usuario TEXT,
                            data TEXT
                            )''')
        self.connection.commit()


class WindowManager(ScreenManager):
    pass


def invalidLogin():
    largura_popup=Window.width * 0.8
    altura_popup=Window.height * 0.3
    pop = Popup(title='Falha no Login',size_hint=(None,None),size=(largura_popup,altura_popup),title_size= largura_popup * 0.06)
    botao_invalido = Button(text='Ok', size_hint=(0.8, 0.4), pos_hint={'center_x': 0.5}, font_size= largura_popup * 0.06)
    botao_invalido.bind(on_press=pop.dismiss)
    content = BoxLayout(orientation='vertical')
    content.add_widget(Label(text='Email ou Senha\ninválidos.', font_size= largura_popup * 0.06))
    content.add_widget(botao_invalido)
    pop.content = content
    pop.open()


def retorna_para_login(instance, sm):
    sm.current = "login"


def invalidForm(sm):
    largura_popup = Window.width * 0.8
    altura_popup = Window.height * 0.3
    pop = Popup(title='Dados inválidos', size_hint=(None, None), size=(largura_popup, altura_popup),title_size= largura_popup * 0.04)
    content = BoxLayout(orientation='vertical')
    button = Button(text='Voltar ao Login', size_hint=(0.8, 0.4), pos_hint={'center_x': 0.5}, font_size= largura_popup * 0.04)
    button.bind(on_press=pop.dismiss)
    content.add_widget(Label(text='Preencha todas as entradas\n com informações válidas.', font_size= largura_popup * 0.06))
    content.add_widget(button)
    pop.content = content
    pop.open()


kv = Builder.load_file("my.kv")
sm = WindowManager()
screens = [LoginWindow(name="login"), CreateAccountWindow(name="create"), MainWindow(name="main"),
           PesquisaWindow(name="pesquisa")]

for screen in screens:
    sm.add_widget(screen)

sm.current = "login"


class MyMainApp(App):

    def build(self):
        self.conn=sqlite3.connect('ultimo_usuario.db')
        return sm


if __name__ == "__main__":
    MyMainApp().run()
