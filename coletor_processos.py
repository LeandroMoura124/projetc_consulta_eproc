import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

#NOMES PARA REQUISIÇÃO
NOMES_PARA_BUSCAR = [
    "ADILSON DA SILVA",
    "JOÂO DA SILVA MORAES",
    "RICARDO DE JESUS",
    "SERGIO FIRMINO DA SILVA",
    "HELENA FARIAS DE LIMA",
    "PAULO SALIM MALUF",
    "PEDRO DE SÁ"
]
URL_CONSULTA = "https://eproc-consulta-publica-1g.tjmg.jus.br/eproc/externo_controlador.php?acao=processo_consulta_publica"
ARQUIVO_SAIDA = "resultados_processos.json"


def coletar_dados():
    servico = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servico)
    driver.maximize_window()

    dados_coletados = {}
    print("Iniciando a coleta de dados...")

    for nome in NOMES_PARA_BUSCAR:
        print(f"\nBuscando por: {nome}")
        
        try:
            driver.get(URL_CONSULTA)
            wait = WebDriverWait(driver, 30) # instancia de espera  (explicit wait) com um timeout de 30 segundos
            print("Aguardando formulário...")
            campo_nome = wait.until(EC.presence_of_element_located((By.ID, "txtStrParte"))) #busca por id div
            botao_consultar = wait.until(EC.element_to_be_clickable((By.ID, "sbmNovo")))
            
            campo_nome.clear()
            campo_nome.send_keys(nome)
            botao_consultar.click()
            print("Realizando a consulta inicial de partes...")
            
            wait.until(EC.visibility_of_element_located((By.ID, "divInfraAreaTabela")))
            links_das_partes = []
            linhas_partes = driver.find_elements(By.CSS_SELECTOR, "tr.infraTrClara, tr.infraTrEscura") # dados do retorno
            
            if not linhas_partes:
                print(" -> Nenhuma parte encontrada para esta busca.")
                dados_coletados[nome] = []
                continue

            print(f"Encontradas {len(linhas_partes)} partes. Coletando informações...")
            for parte in linhas_partes:
                colunas = parte.find_elements(By.TAG_NAME, "td")
                if len(colunas) >= 2:
                    link_elemento = colunas[0].find_element(By.TAG_NAME, "a")
                    links_das_partes.append({
                        "url_lista_processos": link_elemento.get_attribute('href'),
                        "nome_parte": colunas[0].text.strip(),
                        "cpf_cnpj": colunas[1].text.strip(),
                        "processos": []
                    })

            # coletar os links dos processos
            total_partes = len(links_das_partes)
            for i, info_parte in enumerate(links_das_partes):
                print(f"  ({i+1}/{total_partes}) Acessando processos de: {info_parte['nome_parte']}")
                driver.get(info_parte['url_lista_processos'])
                
                try:
                    wait.until(EC.visibility_of_element_located((By.ID, "divInfraAreaTabela")))
                    linhas_processos = driver.find_elements(By.CSS_SELECTOR, "tr.infraTrClara, tr.infraTrEscura")
                    
                    for linha_proc in linhas_processos:
                        colunas_proc = linha_proc.find_elements(By.TAG_NAME, "td")
                        if len(colunas_proc) >= 5:
                            link_processo_el = colunas_proc[0].find_element(By.TAG_NAME, "a")
                            info_parte['processos'].append({
                                "url_detalhes": link_processo_el.get_attribute('href'),
                                "numero_processo": colunas_proc[0].text.strip(),
                                "autor": colunas_proc[1].text.strip(),
                                "reu": colunas_proc[2].text.strip(),
                                "assunto": colunas_proc[3].text.strip(),
                                "ultimo_evento": colunas_proc[4].text.strip(),
                                "detalhes": {}
                            })
                except TimeoutException:
                    print("    -> Nenhuma lista de processos encontrada.")
                    continue

            for info_parte in links_das_partes: #Atribuição de detalhes de cada um dos processos ao nosso relatorio de dados
                if not info_parte['processos']: continue
                print(f"  Coletando detalhes dos processos de: {info_parte['nome_parte']}")
                
                for processo in info_parte['processos']:
                    print(f"    -> Acessando detalhes do processo: {processo['numero_processo']}")
                    driver.get(processo['url_detalhes'])
                    
                    try:
                        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Capa do Processo')]")))
                        
                        def extrair_dado(label):
                            try:
                                return driver.find_element(By.XPATH, f"//*[contains(text(), '{label}')]/following-sibling::span").text.strip()
                            except NoSuchElementException:
                                return "Não informado"
                        
                        orgao_julgador = extrair_dado("Órgão Julgador:")
                        
                        try:
                            valor_causa = driver.find_element(By.XPATH, "//td[contains(., 'Valor da Causa:')]/following-sibling::td").text.strip()
                        except NoSuchElementException:
                            valor_causa = "Não informado"
                        
                        eventos = []
                        tabela_eventos = driver.find_element(By.XPATH, "//table[.//th[text()='Evento']]")
                        linhas_eventos = tabela_eventos.find_elements(By.CSS_SELECTOR, "tbody tr")
                        
                        for linha_evento in linhas_eventos:
                            cols = linha_evento.find_elements(By.TAG_NAME, "td")
                            if len(cols) >= 4:
                                eventos.append({
                                    "seq": cols[0].text.strip(),
                                    "data_hora": cols[1].text.strip(),
                                    "descricao": cols[2].text.strip(),
                                    "usuario": cols[3].text.strip()
                                })
                        
                        processo['detalhes'] = { #Atribui a lista detalhes ao dic de processos
                            "orgao_julgador": orgao_julgador,
                            "valor_causa": valor_causa,
                            "eventos": eventos
                        }
                    except Exception as e:
                        print(f"      Erro ao coletar detalhes do processo: {e}")
                        processo['detalhes'] = {"erro": "Não foi possível coletar os detalhes."} #trat exception

            dados_coletados[nome] = links_das_partes

        except Exception as e:
            print(f" -> Ocorreu um erro geral na busca por '{nome}': {e}")
            dados_coletados[nome] = []

    driver.quit()

    with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
        json.dump(dados_coletados, f, ensure_ascii=False, indent=4) #Salva Elemento Json

    print(f"\nColeta finalizada! Verifique o arquivo '{ARQUIVO_SAIDA}'")

if __name__ == "__main__":
    coletar_dados()