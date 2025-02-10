import requests
import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any
from urllib.parse import urlparse

def crawl_site(url: str, depth: int, data_type: str, request_limit: int) -> Dict[str, Any]:
    """
    Realiza a chamada para a API do Firecrawl com os parâmetros fornecidos.

    Args:
        url (str): URL do site a ser crawleado.
        depth (int): Profundidade do crawling.
        data_type (str): Tipo de dados a extrair (ex.: "links", "text", "images").
        request_limit (int): Limite de requisições.

    Returns:
        Dict[str, Any]: Resposta da API no formato JSON.

    Em caso de erro na requisição, o programa será encerrado.
    """
    firecrawl_api_url = "https://api.firecrawl.com/crawl"  # Substitua pela URL correta da API, se necessário

    # Parâmetros da requisição
    params = {
        "url": url,
        "depth": depth,
        "dataType": data_type,
        "limit": request_limit
    }

    try:
        print("Enviando requisição para a API do Firecrawl...")
        response = requests.get(firecrawl_api_url, params=params)
        response.raise_for_status()  # Levanta exceção para status codes de erro
        return response.json()
    except requests.RequestException as error:
        print(f"Erro na requisição: {error}")
        sys.exit(1)

def save_as_markdown(data: Dict[str, Any], output_dir: Path, data_type: str) -> None:
    """
    Salva os dados do crawling em formato Markdown.

    Args:
        data (Dict[str, Any]): Dados retornados pela API
        output_dir (Path): Diretório de saída
        data_type (str): Tipo de dados extraídos
    """
    md_content = f"# Resultado do Crawling\n\n"
    md_content += f"## Tipo de dados: {data_type}\n\n"

    if data_type == "links":
        md_content += "### Links encontrados:\n\n"
        for link in data.get("links", []):
            md_content += f"- [{link}]({link})\n"
    
    elif data_type == "text":
        md_content += "### Textos extraídos:\n\n"
        for text in data.get("texts", []):
            md_content += f"{text}\n\n---\n\n"
    
    elif data_type == "images":
        md_content += "### Imagens encontradas:\n\n"
        for image in data.get("images", []):
            md_content += f"![{image}]({image})\n\n"

    output_file = output_dir / "crawling_results.md"
    output_file.write_text(md_content, encoding="utf-8")
    print(f"\nResultados salvos em: {output_file}")

def main() -> None:
    # Configuração dos argumentos de linha de comando
    parser = argparse.ArgumentParser(
        description="Programa para crawling e scraping utilizando a API do Firecrawl"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="URL do site para realizar o crawling. Exemplo: https://exemplo.com"
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=1,
        help="Profundidade do crawling (padrão: 1)"
    )
    parser.add_argument(
        "--dataType",
        choices=["links", "text", "images"],
        default="links",
        help="Tipo de dados a extrair: links, text ou images (padrão: links)"
    )
    parser.add_argument(
        "--requestLimit",
        type=int,
        default=10,
        help="Limite de requisições (padrão: 10)"
    )

    args = parser.parse_args()

    # Cria diretório de saída baseado no domínio do site
    domain = urlparse(args.url).netloc
    output_dir = Path("Output") / domain
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Iniciando o crawling...")
    result = crawl_site(args.url, args.depth, args.dataType, args.requestLimit)

    # Salva o resultado em formato Markdown
    save_as_markdown(result, output_dir, args.dataType)

if __name__ == "__main__":
    main()