from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pandas as pd
import requests
import sqlite3
import time
import os

dados = {
    "conta1":{
        "SERVICE_ACCOUNT_FILE": "sheets.json",
        "SPREADSHEET_ID": "",
        "RANGE_NAME": "",
        "BASE_URL": "https://api.mercadolibre.com",
        "DB_NAME": "mercado_livre.db",
        "EXCEL_FILE":"mercado_livre.xlsx",
        "EXCEL_NCM":"conta01.xlsx",
    },
    "conta2":{
        "SERVICE_ACCOUNT_FILE": "sheets.json",
        "SPREADSHEET_ID": "",
        "RANGE_NAME": "",
        "BASE_URL": "https://api.mercadolibre.com",
        "DB_NAME": "mercado_livre.db",
        "EXCEL_FILE":"mercado_livre.xlsx",
        "EXCEL_NCM":"conta02.xlsx",
    },
    "conta3":{
        "SERVICE_ACCOUNT_FILE": "sheets.json",
        "SPREADSHEET_ID": "",
        "RANGE_NAME": "",
        "BASE_URL": "https://api.mercadolibre.com",
        "DB_NAME": "mercado_livre.db",
        "EXCEL_FILE":"mercado_livre.xlsx",
        "EXCEL_NCM":"conta03.xlsx",
    }
}

def get_access_token(aux):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    credentials = Credentials.from_service_account_file(dados[aux]['SERVICE_ACCOUNT_FILE'], scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=dados[aux]['SPREADSHEET_ID'], range=dados[aux]['RANGE_NAME']).execute()
    value = result.get('values', [])
    return value[0][0] if value else None


def delete_database(aux):
    if os.path.exists(dados[aux]['DB_NAME']):
        os.remove(dados[aux]['DB_NAME'])
        print(f"Banco de dados {dados[aux]['DB_NAME']} excluído.")
    else: 
        print(f"Nenhum banco de dados existente com o nome {dados[aux]['DB_NAME']}")

def create_database(aux):
    conn = sqlite3.connect(dados[aux]['DB_NAME'])
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Anuncios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT,
            item_id TEXT UNIQUE,
            conta TEXT,
            estoque_anuncio TEXT,
            venda_anuncio TEXT,
            ncm TEXT,
            ean TEXT,
            status TEXT,
            marca TEXT,
            categoria TEXT,
            data_criacao TEXT
        )
    """)
    conn.commit()
    conn.close()
    print(f"Banco de dados {dados[aux]['DB_NAME']} criado com sucesso.")

def save_item(sku, item_id, aux, estoque_anuncio, venda_anuncio, ncm, ean, status, marca, categoria, data_criacao):
    conn = sqlite3.connect(dados[aux]['DB_NAME'])
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Anuncios (sku, item_id, conta, estoque_anuncio, venda_anuncio, ncm, ean, status, marca, categoria, data_criacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (sku, item_id, aux, estoque_anuncio, venda_anuncio, ncm, ean, status, marca, categoria, data_criacao))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao salvar o item {item_id} no banco de dados da conta {aux}: {e}")
    finally:
        conn.close()

def get_user_id(access_token, aux):
    url = f"{dados[aux]['BASE_URL']}/users/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["id"]
    else:
        raise Exception(f"Erro ao obter ID do usuário: {response.status_code}, {response.text}")
    
def get_all_items_from_seller(user_id, access_token, aux):
    all_item_ids = []
    headers = {"Authorization": f"Bearer {access_token}"}

    # Primeira requisição
    url = f"{dados[aux]['BASE_URL']}/users/{user_id}/items/search?search_type=scan"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Erro inicial: {response.status_code} - {response.text}")
        return all_item_ids

    data = response.json()
    scroll_id = data.get("scroll_id")
    if not scroll_id:
        print("scroll_id não encontrado na resposta inicial.")
        return all_item_ids

    item_ids = data.get("results", [])
    all_item_ids.extend(item_ids)

    pagina = 1
    total_itens = len(item_ids)
    print(f"Página {pagina} - Itens obtidos: {len(item_ids)} - Total acumulado: {total_itens}")

    while True:
        pagina += 1
        url = f"{dados[aux]['BASE_URL']}/users/{user_id}/items/search?search_type=scan&scroll_id={scroll_id}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Erro ao continuar scroll: {response.status_code} - {response.text}")
            break

        data = response.json()
        item_ids = data.get("results", [])
        scroll_id = data.get("scroll_id")  # Atualiza o scroll_id

        if not item_ids:
            print("Fim dos resultados.")
            break

        all_item_ids.extend(item_ids)
        total_itens += len(item_ids)
        print(f"Página {pagina} - Itens obtidos: {len(item_ids)} - Total acumulado: {total_itens}")

        time.sleep(1) 

    print(f"Coleta finalizada. Total de itens coletados: {total_itens}")
    return all_item_ids

def buscar_sku(texto, caminho_arquivo='MLBxSKU.xlsx'):
    try:
        df = pd.read_excel(caminho_arquivo)

        # Verifica se o DataFrame tem pelo menos 2 colunas
        if df.shape[1] < 2:
            print("Erro: Arquivo deve ter pelo menos duas colunas.")
            return None

        
        for i in range(len(df)):
            if str(df.iloc[i, 0]).strip() == str(texto).strip():
                return df.iloc[i, 1]

        return None 
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return None

def get_sku(item_id, access_token, aux):
    status = ""
    sku = ""
    url = f"{dados[aux]['BASE_URL']}/items/{item_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    time.sleep(1)

    if response.status_code == 200:
        status = "Ativo"
        data = response.json()
        
        sku = None
        for attribute in data.get('attributes', []):
            if attribute.get('name') == 'SKU':  
                sku = attribute.get('value_name')  
        
        if sku is None:
            if data.get('seller_custom_field') is not None:
                sku = data.get('seller_custom_field')
            elif data.get('status') != "paused" or data.get('status') is None or data.get('status') == 'under_review':
                sku = buscar_sku(item_id)
        
        

        if sku or data.get('status') == 'paused':
            print("SKU do item:", sku if sku else "Pausado")
            status = "Pausado"
        elif data.get('status') == 'under_review':
            print("SKU do item:", sku if sku else "Pausado")
            status = "under_review"
        else:
            print("SKU do item:", sku if sku else "SKU nao encontrado")
            #print(data)
            #input()
    elif response.status_code == 404:
        print("Erro 404: Recurso nÃ£o encontrado. Verifique o ITEM_ID e ACCESS_TOKEN.")
    else:
        print(f"Erro {response.status_code}: {response.text}")
   
    return sku, status


def get_item_details(item_id, access_token):
    url = f"https://api.mercadolibre.com/items/{item_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    time.sleep(1)

    if response.status_code != 200:
        print(f"Erro {response.status_code}: {response.text}")
        return None

    data = response.json()

    # Coletar campos da raiz
    available_quantity = data.get("available_quantity")
    sold_quantity = data.get("sold_quantity")
    status = data.get("status")
    category_id = data.get("category_id")
    date_created = data.get("date_created")

    if date_created:
        date_obj = datetime.strptime(date_created, "%Y-%m-%dT%H:%M:%S.%fZ")
        date_formatted = date_obj.strftime("%Y-%m-%d")
    else:
        date_formatted = None

    # Coletar atributos
    attributes = data.get("attributes", [])
    ean = brand = None

    for attr in attributes:
        attr_id = attr.get("id")
        value_name = attr.get("value_name")
        if attr_id in ["GTIN", "EAN"] and not ean:
            ean = value_name
        elif attr_id == "BRAND" and not brand:
            brand = value_name

    # Buscar nome da categoria
    category_name = None
    if category_id:
        category_url = f"https://api.mercadolibre.com/categories/{category_id}"
        category_response = requests.get(category_url, headers=headers)

        if category_response.status_code == 200:
            category_data = category_response.json()
            category_name = category_data.get("name")

    # Retornar tudo organizado
    result = {
        'item_id': item_id,
        'available_quantity': available_quantity,
        'sold_quantity': sold_quantity,
        'status': status,
        'ean': ean,
        'brand': brand,
        'category_id': category_id,
        'category_name': category_name,
        'date_created': date_formatted
    }

    print(f"Detalhes do anúncio {item_id}: {result}")
    return result

def excel_ncm(aux):
    arquivo_entrada = dados[aux]['EXCEL_NCM']
    aba = 'Produtos Únicos'

    if not os.path.exists(arquivo_entrada):
        print(f"Arquivo não encontrado: {arquivo_entrada}")
        return {}

    try:
        df_excel = pd.read_excel(arquivo_entrada, sheet_name=aba, skiprows=1, usecols=['Código do Anúncio', 'NCM'])
        df_excel.rename(columns={'Código do Anúncio': 'item_id'}, inplace=True)
        ncm_dict = df_excel.set_index('item_id')['NCM'].astype(str).to_dict()
        return ncm_dict
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return {}


def main():
    for aux in ["conta1", "conta2", "conta3"]:
        try:
            print(f"Processando dados da conta {aux}...")
            access_token = get_access_token(aux)
            if not access_token:
                continue
            
            user_id = get_user_id(access_token, aux)
            create_database(aux)
            
            # Carrega o dicionário de NCMs do Excel
            ncm_dict = excel_ncm(aux)
            
            item_ids = get_all_items_from_seller(user_id, access_token, aux)
            if not item_ids:
                continue
            
            for item_id in item_ids:
                time.sleep(1)
                sku, status = get_sku(item_id, access_token, aux)
                item_details = get_item_details(item_id, access_token)
                if not item_details:
                    continue
                
                # Obtém o NCM do dicionário
                ncm = ncm_dict.get(item_id, None)
                
                save_item(
                    sku,
                    item_id,
                    aux,
                    item_details['available_quantity'],
                    item_details['sold_quantity'],
                    ncm,
                    item_details['ean'],
                    item_details['status'],
                    item_details['brand'],
                    item_details['category_name'],
                    item_details['date_created']
                )
            
            print(f"Processamento concluído para a conta {aux}.\n")
        except Exception as e:
            print(f"Erro ao processar a conta {aux}: {e}")

if __name__ == "__main__":
    main()