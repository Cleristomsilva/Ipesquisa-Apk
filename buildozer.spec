[app]

# Título do aplicativo
title = Ipesquisa

# Nome do pacote
package.name = com.example.ipesquisa

# Versão do aplicativo
package.version = 1.0.0

# Versão do aplicativo
version = 1.0.0

# Nome do ícone (certifique-se de ter o arquivo ipesquisa.png no diretório do projeto)
icon.filename = ipesquisa.png

# Diretório de origem do projeto
source.dir = .

# Lista de arquivos a serem incluídos
source.include_exts = py,kv,db,png,ttf,csv,xlsx,cfg

# Dependências do seu aplicativo
requirements = kivy, matplotlib, sqlite3, openpyxl, datetime, os, configparser, pytz, functools

# Versão mínima do Android que o aplicativo suporta
android.minapi = 21

# Permissões necessárias (caso seu aplicativo necessite)
android.permissions = INTERNET

# Orientação do aplicativo vertical
orientation = portrait

[buildozer]

# Adicione as configurações específicas do Buildozer aqui

[requirements]

# Adicione as dependências do seu aplicativo que o Buildozer precisa instalar aqui

