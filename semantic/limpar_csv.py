import csv
import re

# --- Configurações ---
arquivo_entrada = 'tub_index.csv'  # Nome do seu arquivo original
arquivo_saida = 'tub_index_limpo.csv' # Nome do arquivo que será criado
delimitador = ',' # Se seu CSV usa ponto e vírgula, mude para ';'

def limpar_texto(texto):
    # Remove qualquer coisa entre parênteses e os espaços ao redor
    # Ex: "rua(as)" vira "rua", "casa (s)" vira "casa"
    return re.sub(r'\s*\(.*?\)', '', texto).strip()

def processar_csv():
    print("Iniciando o processamento...")
    
    try:
        with open(arquivo_entrada, mode='r', encoding='utf-8', newline='') as f_in, \
             open(arquivo_saida, mode='w', encoding='utf-8', newline='') as f_out:
            
            leitor = csv.reader(f_in, delimiter=delimitador)
            escritor = csv.writer(f_out, delimiter=delimitador)
            
            contador = 0
            
            for linha in leitor:
                if not linha: continue # Pula linhas vazias
                
                # Pega o conteúdo da primeira coluna (índice 0)
                assunto_original = linha[0]
                
                # Limpa o assunto
                assunto_limpo = limpar_texto(assunto_original)
                
                # Atualiza a primeira coluna na linha
                linha[0] = assunto_limpo
                
                # Escreve a linha completa (com as referências inalteradas) no novo arquivo
                escritor.writerow(linha)
                contador += 1

        print(f"Sucesso! {contador} linhas processadas.")
        print(f"Arquivo salvo como: {arquivo_saida}")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo_entrada}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    processar_csv()
