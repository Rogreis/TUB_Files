import json
import os
from dataclasses import dataclass
from typing import List

# 1. Definição da Classe
@dataclass
class RodamManifestItem:
    FileName: str = ""
    FilePath: str = ""
    Optional: bool = False
    Hash256: str = ""

def carregar_manifesto_local() -> List[RodamManifestItem]:
    """
    Lê o arquivo 'rodam_manifest.json' do diretório corrente e 
    retorna uma lista de objetos RodamManifestItem.
    """
    nome_arquivo = "rodam_manifest.json"
    
    # Verifica se o arquivo existe no diretório atual
    if not os.path.exists(nome_arquivo):
        print(f"ERRO: O arquivo '{nome_arquivo}' não foi encontrado no diretório: {os.getcwd()}")
        return []

    try:
        # Abre o arquivo em modo leitura (r) com encoding utf-8
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Converte a lista de dicionários para lista de objetos usando List Comprehension
            # O **item desempacota as chaves do json para os argumentos da classe
            lista_itens = [RodamManifestItem(**item) for item in data]
            
            return lista_itens

    except json.JSONDecodeError:
        print(f"ERRO: O arquivo '{nome_arquivo}' não contém um JSON válido.")
        return []
    except Exception as e:
        print(f"ERRO inesperado: {e}")
        return []

# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    
    # 1. Tenta carregar os dados
    print(f"Procurando arquivo em: {os.getcwd()}...")
    resultado = carregar_manifesto_local()

    # 2. Exibe os resultados
    if resultado:
        print(f"\nSucesso! {len(resultado)} itens carregados:\n")
        print(f"{'FILENAME':<25} | {'HASH (Início)':<15} | {'OPTIONAL'}")
        print("-" * 55)
        
        for item in resultado:
            print(f"{item.FileName:<25} | {item.Hash256[:12]}... | {item.Optional} ! {item.FilePath}")
    else:
        print("\nNenhum item processado. Verifique se o arquivo 'rodam_manifest.json' existe.")
