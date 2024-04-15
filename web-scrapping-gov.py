# pip install pdfplumber
import enum
import pdfplumber as pdftool
import unicodedata
import os
from os import listdir
from os.path import join, isfile

import sys

from datetime import datetime
import re

from flask import Flask, request, render_template
from logging import FileHandler, WARNING

app = Flask(__name__)

file_handler = FileHandler("errorlog.txt")
file_handler.setLevel(WARNING)

pasta_cache = "static/pdf_cache"


# remoce acentos e torna tudo minúsculo para deixar a busca mais precisa
def Normaliza_Texto(str):
    texto = str.lower().strip()
    texto = (
        unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode("utf-8")
    )
    return texto



def Lista_Arquivos_PDF():
    lista_arquivos = [f for f in listdir(pasta_cache) if isfile(join(pasta_cache, f))]
    if not lista_arquivos
        return 'NÃO EXISTE NENHUM PDF NA PASTA CACHE'
    return lista_arquivos


def Carrega_Arquivo(filepath):
    if not os.path.isdir(pasta_cache):
        os.mkdir(pasta_cache)

    return pasta_cache + "/" + filepath


def Possui_Texto(termo_busca, filepath):
    achou_pg = 0
    retorno = ""
    resultados = ""
    total = 0

    arquivo = Carrega_Arquivo(filepath)

    # debug variavel
    # print(arquivo, file=sys.stderr)

    with pdftool.open(arquivo) as pdf:
        total_pages = len(pdf.pages)

        for p_no, pagina in enumerate(pdf.pages):
            texto_pdf = pagina.extract_text(x_tolerance=1)

            termo = Normaliza_Texto(termo_busca)
            texto_pdf = Normaliza_Texto(texto_pdf)

            pattern = re.compile(f"(^|\n)(.*?)({termo})(.*?)($|\n)", re.DOTALL)

            for match in re.finditer(pattern, texto_pdf):
                # print(match.group())
                total = total + 1
                str_pg = str(p_no + 1)
                resultados += "<small>Página: " + str_pg + "</small>"
                resultados += f"<div class='resultado'>{match.group(1)}{match.group(2)}<span class='highlight'>{match.group(3)}</span>{match.group(4)}{match.group(5)}</div>"

        retorno += f"<div class='topo'>{total} Resultados encontrados   ||   Arquivo: <a href='{arquivo}'><b>{os.path.basename(arquivo)}</b></a></div>"
        retorno += resultados

        print(retorno, file=sys.stderr)

    return retorno


def Principal():
    termo_busca = request.args.get("termo_busca")
    lista_arquivos = Lista_Arquivos_PDF()

    print(lista_arquivos, file=sys.stderr)

    resultado_principal = f'<h1>"{termo_busca}"</h1>'
    for arquivo in lista_arquivos:
        resultado_principal += Possui_Texto(termo_busca, arquivo)

    return resultado_principal


@app.route("/", methods=["GET", "POST"])
def home():
    resultado = Principal()

    return render_template("index.html", variavel=resultado)
    # return Possui_Texto("autoriz", "teste.pdf")


if __name__ == "__main__":
    app.run()
