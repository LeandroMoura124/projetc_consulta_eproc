# Coletor de Dados Processuais - TJMG

Teste Avaliativo 15/10 - Aplicação em Python para automatizar a busca de informações processuais no portal de consulta pública do eproc (TJMG).

O script realiza buscas a partir de uma lista de nomes pré-definida e armazena os dados coletados em um arquivo JSON.

## Funcionalidades Principais

-   Automação da navegação no portal do TJMG.
-   Coleta de dados de partes encontradas (Nome e CPF/CNPJ).
-   Armazenamento dos resultados em um arquivo JSON estruturado.

## Bibliotecas Utilizadas

O projeto foi construído com Python e utilizei as seguintes bibliotecas:

-   **Selenium:** Responsável pela automação do navegador web, executando ações como preencher formulários, clicar em botões e extrair os dados da página de resultados.

-   **WebDriver Manager:** Utilizada para gerenciar o driver do navegador (ChromeDriver) de forma automática, o que simplifica a configuração e garante a compatibilidade com a versão do Google Chrome instalada no computador.

-   **JSON:** Biblioteca padrão do Python, empregada para formatar e salvar os dados coletados no arquivo de saída `.json`.

## Pré-requisitos

É preciso ter instalado:

-   Python 3.x
-   Navegador Google Chrome

## Como Executar

Siga os passos abaixo para configurar e executar o projeto:

1.  **Clone o repositório ou baixe o arquivo `coletor_processos.py`** para um diretório de sua preferência.

2.  **Abra um terminal** nessa mesma pasta e **instale as dependências** necessárias:
    ```sh
    pip install selenium webdriver-manager
    ```

3.  **Execute o script** com o seguinte comando:
    ```sh
    python coletor_processos.py
    ```

O script iniciará o processo, e você poderá acompanhar o progresso da coleta diretamente no terminal. Ao final, o arquivo `resultados_processos.json` será gerado.

## Autor

Leandro Moura da Silva