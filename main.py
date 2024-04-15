from kivy.config import Config
Config.set('graphics', 'width', '280')  # Definindo a largura da janela como 360 pixels
Config.set('graphics', 'height', '560')  # Definindo a altura da janela como 640 pixels

import sqlite3
import pytz
import configparser
import os
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from matplotlib import pyplot as plt
from openpyxl import Workbook
from functools import partial
from datetime import datetime
from kivy.uix.boxlayout import BoxLayout



class CreateAccountWindow(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)

    Window.clearcolor=[0,0,0,1]

    def __init__(self, usuario='', **kwargs):
        super(CreateAccountWindow, self).__init__(**kwargs)
        self.create_table_usuarios()

        fuso_horario=pytz.timezone('America/Sao_Paulo')

        # Obtenha a data e hora atual
        data_hora=datetime.now()
        print("data e hora 45",data_hora)



    def create_table_usuarios(self):
        self.connection = sqlite3.connect('usuarios.db')
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                                email TEXT PRIMARY KEY,
                                password TEXT NOT NULL,
                                data_criacao TEXT NOT NULL
                            )''')
        self.connection.commit()

    def submit(self):
        if self.email.text != "" and self.email.text.count("@") == 1 and self.email.text.count(".") > 0:
            if self.password.text != "":
                data_criacao=datetime.now()
                self.data_formatada=data_criacao.strftime("%d-%m-%Y %H:%M:%S")
                try:
                    self.connection=sqlite3.connect('usuarios.db')
                    cursor=self.connection.cursor()
                    cursor.execute(
                        "INSERT INTO usuarios VALUES (?, ?, ? )",
                        (self.email.text,self.password.text,self.data_formatada)
                        )
                    self.connection.commit()
                    self.connection.close()
                    print("Dados inseridos com sucesso")
                    sm.current="login"
                except sqlite3.Error as e:
                    print("Erro ao inserir dados:",e)
                    # Trate o erro conforme necessário
            else:
                invalidForm(sm)
        else:
            invalidForm(sm)
#ok

    def login(self):
        self.reset()
        sm.current = "login"
#ok

    def reset(self):
        self.email.text = ""
        self.password.text = ""
#ok

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
        print("carregar_ultimo_usuario:", row)
        if row is not None:
            self.email.text = row[1]
            self.connection.close()

    def salvar_email_toggle(self,switch):
        if switch.active:
            print("Email será salvo")
            # App.get_running_app().atualizar_ultimo_usuario()  # Atualiza o último usuário no banco de dados
            App.get_running_app().root.get_screen("login").atualizar_ultimo_usuario()
        else:
            # App.get_running_app().deletar_ultimo_usuario()  # Deleta o último usuário do banco de dados
            App.get_running_app().root.get_screen("login").deletar_ultimo_usuario()

            print("Email não será salvo")


    def atualizar_ultimo_usuario(self):
        if self.email.text.strip() != '':
            id="1"
            print("atualizar_ultimo_usuario:", self.email.text.strip())
            self.connection = sqlite3.connect('ultimo_usuario.db')
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM ultimo_usuario")
            cursor.execute("INSERT INTO ultimo_usuario VALUES (?, ?)", (id,self.email.text.strip(),))
            self.connection.commit()
            self.connection.close()
            print("Ultimo usuario atualizado com sucesso")


    def deletar_ultimo_usuario(self):
        print("deletar_ultimo_usuario 152")
        self.connection = sqlite3.connect('ultimo_usuario.db')
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM ultimo_usuario WHERE id = ?",(1,))
        self.connection.commit()
        self.connection.close()
        print("Ultimo usuario deletado com sucesso")
    #
    # def on_leave(self):
    #     # Fecha a conexão com o banco de dados ao sair da tela de login
    #     App.get_running_app().close_connection()
    def loginBtn(self):
        email = self.email.text.strip()
        password = self.password.text.strip()
        self.usuario = email
        print("email:", email, "password:", password)
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
                    print("Login bem-sucedido")
                    sm.current = "main"
                else:
                    invalidLogin()
            except sqlite3.Error as e:
                print("Erro ao executar a consulta:", e)
                # Trate o erro conforme necessário
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
            print("logout clicado chamando carregar_ultimo_usuario")
            sm.current_screen.carregar_ultimo_usuario()

    # def carregar_ultimo_usuario(self):
    #     self.connection = sqlite3.connect('ultimo_usuario.db')
    #     cursor = self.connection.cursor()
    #     cursor.execute("SELECT email FROM ultimo_usuario")
    #     row = cursor.fetchone()
    #     print("carregar_ultimo_usuario:", row)
    #     if row is not None:
    #         print("email:", row[0])
    #         self.email.text = row[0]
    #         self.connection.close()

    def deletar_ultimo_usuario(self):
        print("deletar_ultimo_usuario 236")
        self.connection = sqlite3.connect('ultimo_usuario.db')
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM ultimo_usuario WHERE id = ?",(1,))
        self.connection.commit()
        self.connection.close()
        print("Ultimo usuario deletado com sucesso")

    def tema_fundo(self,switch,value):
        if switch.active:  # Se o valor for verdadeiro (Switch está ativado)
            Window.clearcolor=[0,0,0,1]  # Define o fundo azul claro (RGB: 1, 1, 1)
            self.texto_branco()  # Chama o método para alterar a cor do texto para branco
        else:  # Se o valor for falso (Switch está desativado)
            Window.clearcolor=[236,236,236,1]  # Define o fundo como preto (RGB: 0, 0, 0)
            self.texto_preto()  # Chama o método para alterar a cor do texto para preto


        App.get_running_app().root.get_screen("pesquisa").tema_fundo(switch,value)

    def texto_preto(self):
        for widget in self.children[0].children:  # Percorre todos os widgets no layout
            if isinstance(widget,Label):
                widget.color=[0,0,0,1]  # Define a cor do texto como preto

    def texto_branco(self):
        for widget in self.children[0].children:  # Percorre todos os widgets no layout
            if isinstance(widget, Label) or isinstance(widget, Button):
                widget.color = [1, 1, 1, 1]  # Define a cor do texto como branco

    def atualizar_tema_label(self,switch,value):
        if switch.active:
            self.ids.tema_label.text="Tema Escuro"
        else:
            self.ids.tema_label.text="Tema Claro"


    def nova_pesquisa(self):
        print("Abrindo nova pesquisa...")
        print("self.email 133: ",self.email)
        sm.current='pesquisa'
        #envia o valor de self.email para a tela de pesquisa
        App.get_running_app().root.get_screen("pesquisa").usuario = self.email

    def export_data(self):
        print("Exportando dados...")

        try:
            # Conectar ao banco de dados
            connection=sqlite3.connect('votos.db')
            cursor=connection.cursor()

            # Executar uma consulta SQL para selecionar todos os registros da tabela 'votos'
            cursor.execute('SELECT * FROM votos')
            rows=cursor.fetchall()

            # Criar um novo arquivo Excel (xlsx)
            workbook=Workbook()  # Aqui está a importação correta do Workbook

            # Adicionar uma planilha ao arquivo Excel
            sheet=workbook.active

            # Adicionar os cabeçalhos das colunas
            sheet.append(['ID','Faixa etária','Genero','Escolaridade','Renda','Intenção de Voto','Usuario'])

            # Adicionar os dados do banco de dados ao arquivo Excel
            for row in rows:
                sheet.append(row)

            # Salvar o arquivo Excel
            workbook.save(filename='votos.csv')
            workbook.save(filename='votos.xlsx')

            # Fechar o cursor e a conexão com o banco de dados
            cursor.close()
            connection.close()

            # Informar ao usuário que os dados foram exportados
            # self.show_message("Sucesso","Os dados foram exportados\n para votos.xlsx")
            btn_fechar=Button(text='Fechar',size_hint=(None,None),size=(200,50),pos_hint={'center_x':0.5})
            content=BoxLayout(orientation='vertical')
            content.add_widget(Label(text="Os dados foram exportados\n para votos.xlsx"))
            content.add_widget(btn_fechar)

            popup=Popup(title='Sucesso',content=content,size_hint=(None,None),size=(250,200))
            btn_fechar.bind(on_press=popup.dismiss)
            popup.open()

        except sqlite3.Error as e:
            # Em caso de erro, mostrar uma mensagem de erro
            self.show_message("Erro",f"Ocorreu um erro ao\nexportar os dados: {e}")

    def show_message(self,title,message):
        # Criar e exibir um popup com a mensagem
        content=BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))

        popup=Popup(title=title,content=content,size_hint=(None,None),size=(250,200))
        popup.open()


    def delete_data(self):
        print("Apagando dados...")
        # Criar o conteúdo do Popup
        content=BoxLayout(orientation='vertical')

        # Adiciona o texto acima dos botões
        content.add_widget(Label(text="Tem certeza que deseja\napagar todos os dados?"))

        # Layout para os botões (horizontal)
        button_layout=BoxLayout(orientation='horizontal')

        # Botões de confirmação e cancelamento
        confirm_button=Button(text='Confirmar',background_color=[0,1,0,1])
        cancel_button=Button(text='Cancelar',background_color=[1,0,0,1])

        # Associa as ações aos botões
        confirm_button.bind(on_press=self.confirm_delete)
        cancel_button.bind(on_press=self.dismiss_popup)

        # Adiciona os botões ao layout horizontal
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)

        # Adiciona o layout dos botões ao conteúdo do Popup
        content.add_widget(button_layout)

        # Cria e mostra o Popup
        self.popup=Popup(title='Excluir Dados',content=content,size_hint=(None,None),size=(300,200))
        self.popup.open()
#ok

    def confirm_delete(self,instance):
        # Código para apagar os dados do votos.db
        self.connection=sqlite3.connect('votos.db')
        cursor=self.connection.cursor()
        cursor.execute('DELETE FROM votos')
        self.connection.commit()
        self.connection.close()

        print("Apagando dados...")
        # Fechar o Popup após a confirmação
        self.dismiss_popup(instance)
#ok

    def dismiss_popup(self,instance):
        self.popup.dismiss()
#ok

    def visualizar_votos(self):
        self.connection=sqlite3.connect('votos.db')
        cursor=self.connection.cursor()
        cursor.execute('SELECT COUNT(*), voto FROM votos GROUP BY voto')
        rows=cursor.fetchall()

        # Preparar os dados para o gráfico
        labels=[row[1] for row in rows]
        counts=[row[0] for row in rows]

        # Criar o gráfico de barras usando Matplotlib
        plt.bar(labels,counts)
        plt.xlabel('Voto')
        plt.ylabel('Número de Votos')
        plt.title('Número de Votos por Voto')

        # Adiciona botões de filtro
        self.add_filter_buttons()

        # Exibir o gráfico
        plt.show()
#ok



    def add_filter_buttons(self):
        # # Botão para filtrar por idade
        # btn_idade=Button(text='Filtrar por Idade',size_hint=(None,None),size=(150,40))
        # btn_idade.bind(on_release=self.show_idade_dropdown)
        #
        # # Botão para filtrar por gênero
        # btn_genero=Button(text='Filtrar por Gênero',size_hint=(None,None),size=(150,40))
        # btn_genero.bind(on_release=self.show_genero_dropdown)
        #
        # # Adiciona os botões ao layout
        # layout=BoxLayout(orientation='horizontal')
        # layout.add_widget(btn_idade)
        # layout.add_widget(btn_genero)

        plt.gca().figure.canvas.manager.toolbar.pan()
        plt.gca().figure.canvas.manager.toolbar.zoom()
        plt.gca().figure.canvas.manager.toolbar.home()
        plt.gca().figure.canvas.manager.toolbar.back()
        plt.gca().figure.canvas.manager.toolbar.forward()

        plt.gca().figure.canvas.manager.toolbar.update()
        plt.gca().figure.canvas.draw()


    def mostrar_botoes_filtro(self):
        # Criar um layout para os botões
        layout=GridLayout(cols=2,spacing=10,padding=(50,10))

        # Botão para filtrar por idade
        btn_idade=Button(text='Filtrar por Idade',size_hint=(None,None),size=(150,40))
        btn_idade.bind(on_release=self.show_idade_dropdown)
        layout.add_widget(btn_idade)

        # Botão para filtrar por gênero
        btn_genero=Button(text='Filtrar por Gênero',size_hint=(None,None),size=(150,40))
        btn_genero.bind(on_release=self.show_genero_dropdown)
        layout.add_widget(btn_genero)

        # Criar um popup para exibir os botões
        popup=Popup(title='Filtros',content=layout,size_hint=(None,None),size=(300,150))
        popup.open()

    def show_idade_dropdown(self,instance):
        dropdown=DropDown()

        # Adicionar opções de idade ao dropdown
        opcoes_idade=['16-18','18-24','25-34','35-44','45-54','55-64','65 ou mais']
        for idade in opcoes_idade:
            btn=Button(text=idade,size_hint_y=None,height=40)
            btn.bind(on_release=lambda btn:self.filtrar_por_idade(btn.text))
            dropdown.add_widget(btn)

        # Mostrar o dropdown abaixo do botão de idade
        dropdown.open(instance)

    def show_genero_dropdown(self,instance):
        dropdown=DropDown()

        # Adicionar opções de gênero ao dropdown
        opcoes_genero=['Masculino','Feminino','Outro/Prefiro não responder']
        for genero in opcoes_genero:
            btn=Button(text=genero,size_hint_y=None,height=40)
            btn.bind(on_release=lambda btn:self.filtrar_por_genero(btn.text))
            dropdown.add_widget(btn)

        # Mostrar o dropdown abaixo do botão de gênero
        dropdown.open(instance)

    def filtrar_por_idade(self,idade):
        # Implementar a lógica para filtrar os votos por idade
        print(f"Filtrar por idade: {idade}")

    def filtrar_por_genero(self,genero):
        # Implementar a lógica para filtrar os votos por gênero
        print(f"Filtrar por gênero: {genero}")

class PesquisaWindow(Screen):
    def __init__(self, usuario='', **kwargs):
        super(PesquisaWindow, self).__init__(**kwargs)

        self.usuario = usuario
        self.connection = sqlite3.connect('votos.db')
        self.create_table()

        self.layout = GridLayout(cols=1, spacing=10, padding=10)
        self.layout.add_widget(Label(text='Questionário', bold=True))


        self.layout.add_widget(Label(text='Idade:',size_hint=(None, None),size=(50, 30)))
        self.idade_input = Spinner(text='Selecione a sua faixa etária', values=['16-18', '18-24', '25-34', '35-44', '45-54', '55-64', '65 ou mais'],size_hint_y=None, height=40)
        self.layout.add_widget(self.idade_input)

        self.layout.add_widget(Label(text='Gênero:',size_hint=(None, None),size=(62, 15)))
        self.genero_input = Spinner(text='Selecione o seu gênero', values=['Masculino', 'Feminino', 'Outro/Prefiro não responder'],size_hint_y=None, height=40)
        self.layout.add_widget(self.genero_input)

        self.layout.add_widget(Label(text='Escolaridade:',size_hint=(None, None),size=(100, 15)))
        self.escolaridade_input = Spinner(text='Selecione a sua escolaridade', values=['Ensino fundamental incompleto', 'Ensino fundamental completo', 'Ensino médio incompleto', 'Ensino médio completo', 'Ensino superior incompleto', 'Ensino superior completo'],size_hint_y=None, height=40)
        self.layout.add_widget(self.escolaridade_input)

        self.layout.add_widget(Label(text='Renda mensal familiar:',size_hint=(None, None),size=(160, 15)))
        self.renda_input = Spinner(text='Selecione sua faixa de renda', values=['Até R$ 1.400', 'de R$ 1.400 a R$ 2.800','de R$ 2.800 a R$ 4.200', 'de R$ 4.200 a R$ 5.600', 'Acima de R$ 5.600'],size_hint_y=None, height=40)
        self.layout.add_widget(self.renda_input)

        self.layout.add_widget(Label(text='Intenção de voto:',size_hint=(None, None),size=(120, 15)))
        self.voto_input = Spinner(text='Selecione sua intenção de voto', values=['Candidato A', 'Candidato B', 'Candidato C', 'Indeciso', 'Nenhum (branco/nulo)'],size_hint_y=None, height=40)
        self.layout.add_widget(self.voto_input)

        self.botao_salvar = Button(text='Salvar',background_color=[0,1,0,1],size_hint=(None, None),size=(150, 40))
        self.botao_salvar.bind(on_press=self.salvar_voto)
        self.layout.add_widget(self.botao_salvar)

        self.botao_cancelar = Button(text='Cancelar', background_color=[1,0,0,1],size_hint=(None, None),size=(150, 40))
        self.botao_cancelar.bind(on_press=self.cancelar_pesquisa)
        self.layout.add_widget(self.botao_cancelar)

        self.contador_label = Label(text='Nenhuma pesquisa realizada.')
        self.layout.add_widget(self.contador_label)

        self.update_contador()
        self.add_widget(self.layout)

    def tema_fundo(self,switch,value):
        if switch.active:  # Se o valor for verdadeiro (Switch está ativado)
            Window.clearcolor=[0,0,0,1]  # Define o fundo azul claro (RGB: 1, 1, 1)
            self.texto_branco()  # Chama o método para alterar a cor do texto para branco
        else:
            Window.clearcolor=[1,1,1,1]  # Define o fundo branco (RGB: 1, 1, 1)
            self.texto_preto()  # Chama o método para alterar a cor do texto para preto

    def texto_preto(self):
        for widget in self.children[0].children:  # Percorre todos os widgets no layout
            if isinstance(widget,Label):
                widget.color=[0,0,0,1]  # Define a cor do texto como preto


    def texto_branco(self):
        for widget in self.children[0].children:  # Percorre todos os widgets no layout
            if isinstance(widget, Label) or isinstance(widget, Button):
                widget.color = [1, 1, 1, 1]  # Define a cor do texto como branco

    def atualizar_tema_label(self,switch,value):
        if switch.active:
            self.ids.tema_label.text="Tema Escuro"
        else:
            self.ids.tema_label.text="Tema Claro"


    def salvar_voto(self,instance):
        print("self.usuario em salvar voto 416 :",self.usuario)
        idade=self.idade_input.text
        genero=self.genero_input.text
        escolaridade=self.escolaridade_input.text
        renda=self.renda_input.text
        voto=self.voto_input.text
        usuario=self.usuario

        # Verifica se todos os campos foram preenchidos
        if idade != 'Selecione a sua faixa etária' and genero != 'Selecione o seu gênero' and escolaridade != 'Selecione a sua escolaridade' and renda != 'Selecione sua faixa de renda' and voto != 'Selecione sua intenção de voto':
            try:
                print(idade,genero,escolaridade,renda,voto,usuario)
                cursor=self.connection.cursor()
                cursor.execute(
                    '''INSERT INTO votos (idade, genero, escolaridade, renda, voto, usuario)
                                  VALUES (?, ?, ?, ?, ?, ?)''',(idade,genero,escolaridade,renda,voto,usuario)
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
        print("update_contador 450")
        cursor = self.connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM votos')
        count = cursor.fetchone()[0]
        self.contador_label.text = f'{count} pesquisas realizadas.'

    def mostrar_popup(self,title,message):
        # Conteúdo do pop-up
        content=BoxLayout(orientation='vertical')
        content.add_widget(Label(text='Pesquisa gravada com sucesso!'))
        btn_encerrar_pesquisas=Button(text='Encerrar Pesquisas',background_color=[1,0,0,1])
        btn_encerrar_pesquisas.bind(on_release=self.encerrar_pesquisas)
        btn_nova_pesquisa=Button(text='Nova Pesquisa', background_color=[0,1,0,1])
        btn_nova_pesquisa.bind(on_release=self.nova_pesquisa_btn)
        # Adicionando botões ao layout
        content.add_widget(btn_encerrar_pesquisas)
        content.add_widget(btn_nova_pesquisa)

        # Criando o pop-up
        popup=Popup(title='Sucesso',content=content,size_hint=(None,None),size=(250,200))

        # Vinculando a função de fechar ao pressionar os botões
        btn_encerrar_pesquisas.bind(on_press=popup.dismiss)
        btn_nova_pesquisa.bind(on_press=popup.dismiss)

        # Abrindo o pop-up
        popup.open()

    def encerrar_pesquisas(self,instance):
        print("encerrar pesquisas 482")
        # Redireciona para a MainWindow
        self.manager.current="main"


    def nova_pesquisa_btn(self,instance):
        self.manager.get_screen('pesquisa').usuario=self.usuario

#ok
    def limpar_inputs(self):
        self.idade_input.text = 'Selecione a sua faixa etária'
        self.genero_input.text = 'Selecione o seu gênero'
        self.escolaridade_input.text = 'Selecione a sua escolaridade'
        self.renda_input.text = 'Selecione sua faixa de renda'
        self.voto_input.text = 'Selecione sua intenção de voto'
#ok

    def cancelar_pesquisa(self, instance):
        self.limpar_inputs()
        self.update_contador()
        sm.current = "main"
#ok

    def create_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS votos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            idade TEXT,
                            genero TEXT,
                            escolaridade TEXT,
                            renda TEXT,
                            voto TEXT,
                            usuario TEXT
                            )''')

        self.connection.commit()
#ok

    def visualizar_votos(self, instance):
        cursor = self.connection.cursor()
        cursor.execute('SELECT COUNT(*), voto FROM votos GROUP BY voto')
        rows = cursor.fetchall()

        # Preparar os dados para o gráfico
        labels = [row[1] for row in rows]
        counts = [row[0] for row in rows]

        # Criar o gráfico de barras usando Matplotlib
        plt.bar(labels, counts)
        plt.xlabel('Voto')
        plt.ylabel('Número de Votos')
        plt.title('Número de Votos por Voto')

        # Exibir o gráfico
        plt.show()
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
screens = [LoginWindow(name="login"), CreateAccountWindow(name="create"), MainWindow(name="main"), PesquisaWindow(name="pesquisa")]

for screen in screens:
    sm.add_widget(screen)

sm.current = "login"



class MyMainApp(App):
    def build(self):
        self.conn=sqlite3.connect('ultimo_usuario.db')
        return sm



if __name__ == "__main__":
    MyMainApp().run()
