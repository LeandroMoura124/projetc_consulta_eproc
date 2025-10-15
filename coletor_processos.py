import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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
        driver.get(URL_CONSULTA)
        
        try:
            wait = WebDriverWait(driver, 30) # instancia de espera  (explicit wait) com um timeout de 30 segundos

            print("Aguardando formulário...")
            campo_nome = wait.until(EC.presence_of_element_located((By.ID, "txtStrParte"))) #Buscando por id div
            botao_consultar = wait.until(EC.element_to_be_clickable((By.ID, "sbmNovo")))

            print("Realizando a consulta...")
            campo_nome.clear()
            campo_nome.send_keys(nome)
            botao_consultar.click()
        
            print("Aguardando resultados...")
            wait.until(EC.visibility_of_element_located((By.ID, "divInfraAreaTabela")))

            print("Coletando dados...")
            linhas = driver.find_elements(By.CSS_SELECTOR, "tr.infraTrClara, tr.infraTrEscura") #Pega dados do retorno
            
            if not linhas:
                print(" -> Nenhum registro encontrado.")
                dados_coletados[nome] = []
            else:
                registros_nome = []
                for linha in linhas:
                    colunas = linha.find_elements(By.TAG_NAME, "td")
                    if len(colunas) >= 2: # Verifica se tem pelo menos 2 colunas
                        nome_parte = colunas[0].text.strip()
                        cpf_cnpj = colunas[1].text.strip()
                        registros_nome.append({
                            "nome_parte": nome_parte,
                            "cpf_cnpj": cpf_cnpj
                        })
                
                print(f" -> {len(registros_nome)} registro(s) encontrado(s).")
                dados_coletados[nome] = registros_nome

        except TimeoutException:
            print(" -> Nenhum registro encontrado ou a página demorou para responder.")
            dados_coletados[nome] = []
        
        except Exception as e:
            print(f" -> Ocorreu um erro inesperado: {e}")
            dados_coletados[nome] = []

    driver.quit()

    with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
        json.dump(dados_coletados, f, ensure_ascii=False, indent=4) #SALVA

    print(f"\nColeta finalizada! Os dados retornados foram salvos no arquivo '{ARQUIVO_SAIDA}'")


if __name__ == "__main__":
    coletar_dados()