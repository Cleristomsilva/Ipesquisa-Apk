import sqlite3

import configparser
from matplotlib import pyplot as plt
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



class CreateAccountWindow(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)

    Window.clearcolor=[0,0,0,1]

    def __init__(self, usuario='', **kwargs):
        super(CreateAccountWindow, self).__init__(**kwargs)
        self.create_table_usuarios()
        data_hora=datetime.now()

        print(os.getenv("JAVA_HOME"))
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

    def submit(self):
        if self.email.text != "" and self.email.text.count("@") == 1 and self.email.text.count(".") > 0:
            if self.password.text != "":
                if self.verifica_email_existente() == False:
                    self.create_table_usuarios()
                    self.connection = sqlite3.connect('usuarios.db')
                    cursor = self.connection.cursor()
                    cursor.execute("INSERT INTO usuarios VALUES (?, ?, ?)", (self.email.text, self.password.text, datetime.now()))
                    self.connection.commit()
                    self.connection.close()
                    self.reset()
                    sm.current = "login"
                else:
                    popup = Popup(title='Erro', content=Label(text='Email ja existe'), size_hint=(None, None), size=(250, 200))
                    popup.open()
            else:
                popup = Popup(title='Erro', content=Label(text='Insira uma senha'), size_hint=(None, None), size=(250, 200))
                popup.open()

        else:
            popup = Popup(title='Erro', content=Label(text='Preencha todos\nos campos corretamente'), size_hint=(None, None), size=(250, 200))
            popup.open()

#ok

    def login(self):
        self.reset()
        sm.current = "login"
#ok

    def reset(self):
        self.email.text = ""
        self.password.text = ""
#ok

class ConfigWindow(Screen):
    pass

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

#ok

    def createBtn(self):
        self.reset()
        sm.current = "create"
#ok

    def reset(self):
        self.email.text = ""
        self.password.text = ""
#ok

class MainWindow(Screen):
    n = ObjectProperty(None)
    created = ObjectProperty(None)
    email = ObjectProperty(None)
    current = ""

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)


#ok
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

    def obter_pasta_downloads():
        Environment=autoclass('android.os.Environment')
        return Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)

    def export_data(self):
        try:
            connection=sqlite3.connect('pesquisa.db')
            cursor=connection.cursor()
            cursor.execute('SELECT * FROM pesquisa')
            rows=cursor.fetchall()

            # Criar um novo arquivo Excel (xlsx)
            workbook=Workbook()

            # Adicionar uma planilha ao arquivo Excel
            sheet=workbook.active

            # Adicionar os cabeçalhos das colunas
            sheet.append(['ID','Faixa etária','Genero','Escolaridade','Renda','Governo fez','O bairro precisa','Conhece Luciana',"Conhece Kadu" , 'Usuario', 'Data'])

            # Adicionar os dados do banco de dados ao arquivo Excel
            for row in rows:
                sheet.append(row)

                # Salvar o arquivo Excel no diretório do aplicativo
            file_path=os.path.join(os.getcwd(),'pesquisa.xlsx')
            workbook.save(filename=file_path)

            # Obter o diretório de downloads
            pasta_downloads=obter_pasta_downloads()

            # Salvar o arquivo Excel na pasta de downloads
            download_file_path=os.path.join(pasta_downloads,'pesquisa.xlsx')
            workbook.save(filename=download_file_path)

            cursor.close()
            connection.close()

            # Informar ao usuário que os dados foram exportados
            btn_fechar=Button(text='Fechar',size_hint=(None,None),size=(200,50),pos_hint={'center_x':0.5})
            content=BoxLayout(orientation='vertical')
            content.add_widget(Label(text="Os dados foram exportados para pesquisa.xlsx"))
            content.add_widget(btn_fechar)

            popup=Popup(title='Sucesso',content=content,size_hint=(None,None),size=(250,200))
            btn_fechar.bind(on_press=popup.dismiss)
            popup.open()

        except sqlite3.Error as e:
            self.show_message("Erro",f"Ocorreu um erro ao exportar os dados: {e}")



    def show_message(self,title,message):
        content=BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))

        popup=Popup(title=title,content=content,size_hint=(None,None),size=(250,200))
        popup.open()


    def delete_data(self):
        content=BoxLayout(orientation='vertical')
        content.add_widget(Label(text="Tem certeza que deseja\napagar todos os dados?"))

        button_layout=BoxLayout(orientation='horizontal')

        confirm_button=Button(text='Confirmar',background_color=[0,1,0,1], size_hint=(None,None),size=(111,50))
        cancel_button=Button(text='Cancelar',background_color=[1,0,0,1], size_hint=(None,None),size=(111,50))

        confirm_button.bind(on_press=self.confirm_delete)
        cancel_button.bind(on_press=self.dismiss_popup)

        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)

        content.add_widget(button_layout)

        self.popup=Popup(title='Excluir Dados',content=content,size_hint=(None,None),size=(250,200))
        self.popup.open()
#ok

    def confirm_delete(self,instance):
        self.connection=sqlite3.connect('pesquisa.db')
        cursor=self.connection.cursor()
        cursor.execute('DELETE FROM pesquisa')
        self.connection.commit()
        self.connection.close()
        self.dismiss_popup(instance)
#ok

    def dismiss_popup(self,instance):
        self.popup.dismiss()
#ok


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

    # Define a cor do texto do Button como branco

    def atualizar_tema_pesquisa(self,value):
        if value == False:
            self.ids.questionario.color=[0,0,0,1]
            self.ids.idade.color=[0,0,0,1]
            self.ids.genero.color=[0,0,0,1]
            self.ids.escolaridade.color=[0,0,0,1]
            self.ids.renda.color=[0,0,0,1]
            self.ids.pergunta1.color=[0,0,0,1]
            self.ids.pergunta2.color=[0,0,0,1]
            self.ids.pergunta3.color=[0,0,0,1]
            self.ids.pergunta4.color=[0,0,0,1]
            self.ids.contador_label.color=[0,0,0,1]
            self.ids.idade_spinner.color=[1,1,1,1]
            self.ids.genero_spinner.color=[1,1,1,1]
            self.ids.escolaridade_spinner.color=[1,1,1,1]
            self.ids.renda_spinner.color=[1,1,1,1]
        elif value == True:
            self.ids.questionario.color=[1,1,1,1]
            self.ids.idade.color=[1,1,1,1]
            self.ids.genero.color=[1,1,1,1]
            self.ids.escolaridade.color=[1,1,1,1]
            self.ids.renda.color=[1,1,1,1]
            self.ids.pergunta1.color=[1,1,1,1]
            self.ids.pergunta2.color=[1,1,1,1]
            self.ids.pergunta3.color=[1,1,1,1]
            self.ids.pergunta4.color=[1,1,1,1]
            self.ids.contador_label.color=[1,1,1,1]
            self.ids.idade_spinner.color=[1,1,1,1]
            self.ids.genero_spinner.color=[1,1,1,1]
            self.ids.escolaridade_spinner.color=[1,1,1,1]
            self.ids.renda_spinner.color=[1,1,1,1]
            self.ids.pergunta1_input.color=[1,1,1,1]
            self.ids.pergunta2_input.color=[1,1,1,1]
            self.ids.pergunta3_spinner.color=[1,1,1,1]
            self.ids.pergunta4_spinner.color=[1,1,1,1]

    def salvar_pesquisa(self):
        idade=self.ids.idade_spinner.text
        genero=self.ids.genero_spinner.text
        escolaridade=self.ids.escolaridade_spinner.text
        renda=self.ids.renda_spinner.text
        pergunta1=self.ids.pergunta1_input.text
        pergunta2=self.ids.pergunta2_input.text
        pergunta3=self.ids.pergunta3_spinner.text
        pergunta4=self.ids.pergunta4_spinner.text
        usuario=self.usuario
        data=datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Verifica se todos os campos foram preenchidos
        if idade != 'Selecione a sua idade' \
                and genero != 'Selecione o seu gênero' \
                and escolaridade != 'Selecione a sua escolaridade' \
                and renda != 'Selecione sua faixa de renda' \
                and pergunta1 != '' \
                and pergunta2 != '' \
                and pergunta3 != 'Selecione sua resposta' \
                and pergunta4 != 'Selecione sua resposta':
            try:
                cursor=self.connection.cursor()
                cursor.execute(
                    '''INSERT INTO pesquisa (idade, genero, escolaridade, renda, pergunta1, pergunta2, pergunta3, pergunta4, usuario, data)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',(idade,genero,escolaridade,renda,pergunta1,pergunta2,pergunta3,pergunta4,usuario,data)
                    )
                self.connection.commit()
                self.update_contador()
                self.mostrar_popup('Sucesso','Pesquisa gravada com sucesso.')
                self.limpar_inputs()
            except sqlite3.Error as e:
                self.mostrar_popup('Erro',f'Ocorreu um erro\nao gravar a pesquisa: {e}')
        else:
            btn_voltar=Button(text='Voltar',size_hint=(None,None),size=(200,50),pos_hint={'center_x': 0.5})
            content=BoxLayout(orientation='vertical')
            content.add_widget(Label(text='Por favor,\npreencha todos os\ncampos da pesquisa.'))
            content.add_widget(btn_voltar)

            popup=Popup(title='Erro',content=content,size_hint=(None,None),size=(250,200))
            btn_voltar.bind(on_press=popup.dismiss)
            popup.open()

    def update_contador(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM pesquisa')
        count = cursor.fetchone()[0]
        self.ids.contador_label.text=f'{count} pesquisas realizadas.'

    def mostrar_popup(self,title,message):
        content=BoxLayout(orientation='vertical')
        content.add_widget(Label(text='Pesquisa gravada com sucesso!'))
        btn_encerrar_pesquisas=Button(text='Encerrar Pesquisas',background_color=[1,0,0,1])
        btn_encerrar_pesquisas.bind(on_release=self.encerrar_pesquisas)
        btn_nova_pesquisa=Button(text='Nova Pesquisa', background_color=[0,1,0,1])
        btn_nova_pesquisa.bind(on_release=self.nova_pesquisa_btn)

        content.add_widget(btn_encerrar_pesquisas)
        content.add_widget(btn_nova_pesquisa)

        popup=Popup(title='Sucesso',content=content,size_hint=(None,None),size=(250,200))

        btn_encerrar_pesquisas.bind(on_press=popup.dismiss)
        btn_nova_pesquisa.bind(on_press=popup.dismiss)
        popup.open()

    def encerrar_pesquisas(self,instance):
        # Redireciona para a MainWindow
        self.manager.current="main"


    def nova_pesquisa_btn(self,instance):
        self.manager.get_screen('pesquisa').usuario=self.usuario

#ok
    def limpar_inputs(self):
        self.ids.idade_spinner.text='Selecione a sua idade'
        self.ids.genero_spinner.text='Selecione o seu gênero'
        self.ids.escolaridade_spinner.text='Selecione a sua escolaridade'
        self.ids.renda_spinner.text='Selecione sua faixa de renda'
        self.ids.pergunta1_input.text=''
        self.ids.pergunta2_input.text=''
        self.ids.pergunta3_spinner.text='Selecione sua resposta'
        self.ids.pergunta4_spinner.text='Selecione sua resposta'
#ok

    def cancelar_pesquisa(self):
        self.limpar_inputs()
        self.update_contador()
        sm.current = "main"
#ok

    def create_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS pesquisa (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            idade TEXT,
                            genero TEXT,
                            escolaridade TEXT,
                            renda TEXT,
                            pergunta1 TEXT,
                            pergunta2 TEXT,
                            pergunta3 TEXT,
                            pergunta4 TEXT,
                            usuario TEXT,
                            data TEXT
                            )''')

        self.connection.commit()
#ok
#ok

class WindowManager(ScreenManager):
    pass
#ok

def invalidLogin():
    pop = Popup(title='Falha no Login',size_hint=(None,None),size=(250,200))

    botao_invalido = Button(text='Ok', size_hint=(0.8, 0.4), pos_hint={'center_x': 0.5})
    botao_invalido.bind(on_press=pop.dismiss)

    content = BoxLayout(orientation='vertical')

    content.add_widget(Label(text='Email ou Senha inválidos.'))
    content.add_widget(botao_invalido)

    pop.content = content
    pop.open()
#ok

def retorna_para_login(instance, sm):
    sm.current = "login"
#ok

def invalidForm(sm):
    # Cria um popup
    pop = Popup(title='Dados inválidos',size_hint=(None, None), size=(250, 200))
    content = BoxLayout(orientation='vertical')

    # Adiciona um botão ao conteúdo do popup
    button = Button(text='Voltar ao Login', size_hint=(0.8, 0.4), pos_hint={'center_x': 0.5})
    button.bind(on_press=pop.dismiss)

    content.add_widget(Label(text='Preencha todas as entradas\n com informações válidas.'))
    content.add_widget(button)
    pop.content = content
    pop.open()
#ok

kv = Builder.load_file("my.kv")
sm = WindowManager()
screens = [LoginWindow(name="login"), CreateAccountWindow(name="create"), MainWindow(name="main"),
           PesquisaWindow(name="pesquisa"), ConfigWindow(name="config")]

for screen in screens:
    sm.add_widget(screen)

sm.current = "login"

class MyMainApp(App):
    def build(self):
        self.conn=sqlite3.connect('ultimo_usuario.db')
        return sm



if __name__ == "__main__":
    MyMainApp().run()
