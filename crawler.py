import re
import threading

import requests
from bs4 import BeautifulSoup

DOMINIO = "https://django-anuncios.solyd.com.br"
LINKS = []
TELEFONES = []

def buscar_site(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica se houve algum erro na requisição
        soup = BeautifulSoup(response.text, 'html.parser')
        return response.text  # Retorna o conteúdo da página
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar o site: {e}")
        return None

def menu():
    while True:
        print("\nMenu de Busca de Site")
        print("1. Buscar site")
        print("2. Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            url = input("Digite a URL do site: ")
            iniciar_busca(url)  # Função para iniciar o processo de busca
        elif escolha == '2':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

def iniciar_busca(url):
    resposta_busca = buscar_site(url)
    if resposta_busca:
        soup_busca = parsing(resposta_busca)
        if soup_busca:
            global LINKS  # Usar a variável global LINKS
            LINKS = encontrar_links(soup_busca)

            THREADS = []
            for i in range(10):
                t = threading.Thread(target=descobrir_telefones)
                THREADS.append(t)

            for t in THREADS:
                t.start()

            for t in THREADS:
                t.join()

def requisicao(url):
    try:
        resposta = requests.get(url)
        resposta.raise_for_status()  # Verifica se a requisição teve sucesso
        return resposta.text
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer requisição: {e}")
        return None

def parsing(resposta_html):
    try:
        soup = BeautifulSoup(resposta_html, 'html.parser')
        return soup
    except Exception as e:
        print(f"Erro ao fazer o parsing HTML: {e}")
        return None

def encontrar_links(soup):
    try:
        cards_pai = soup.find("div", class_="ui three doubling link cards")
        cards = cards_pai.find_all("a")
    except AttributeError:
        print("Erro ao encontrar links")
        return None

    links = []
    for card in cards:
        try:
            link = card['href']
            links.append(link)
        except KeyError:
            pass

    return links

def encontrar_telefone(soup):
    try:
        descricao = soup.find_all("div", class_="sixteen wide column")[2].p.get_text().strip()
    except (IndexError, AttributeError):
        print("Erro ao encontrar descrição")
        return None

    regex = re.findall(r"\(?0?([1-9]{2})[ \-\.\)]{0,2}(9[ \-\.]?\d{4})[ \-\.]?(\d{4})", descricao)
    if regex:
        return regex
    return None

def descobrir_telefones():
    while LINKS:
        try:
            link_anuncio = LINKS.pop(0)
        except IndexError:
            return

        resposta_anuncio = requisicao(DOMINIO + link_anuncio)
        if resposta_anuncio:
            soup_anuncio = parsing(resposta_anuncio)
            if soup_anuncio:
                telefones = encontrar_telefone(soup_anuncio)
                if telefones:
                    for telefone in telefones:
                        print("Telefone encontrado:", telefone)
                        TELEFONES.append(telefone)
                        salvar_telefone(telefone)

def salvar_telefone(telefone):
    string_telefone = "{}{}{}\n".format(telefone[0], telefone[1], telefone[2])
    try:
        with open("telefones.csv", "a") as arquivo:
            arquivo.write(string_telefone)
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")

if __name__ == "__main__":
    menu()
