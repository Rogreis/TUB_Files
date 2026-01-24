import csv
import os

def filtrar_csv(input_file, output_file):
    """
    Lê um arquivo CSV e remove as linhas que não possuem a segunda coluna preenchida (links).
    """
    print(f"Processando '{input_file}' -> '{output_file}'...")
    
    removed_count = 0
    kept_count = 0
    
    try:
        with open(input_file, mode='r', encoding='utf-8', newline='') as infile:
            reader = csv.reader(infile)
            
            # Tenta ler o cabeçalho
            try:
                header = next(reader)
                rows = [header] # Começa com o cabeçalho
            except StopIteration:
                print("Arquivo vazio.")
                return

            for i, row in enumerate(reader, start=2): # Start=2 porque já lemos o cabeçalho
                # Verifica se a linha tem pelo menos 2 colunas e se a segunda não está vazia
                if len(row) >= 2 and row[1].strip():
                    rows.append(row)
                    kept_count += 1
                else:
                    removed_count += 1
                    # Opcional: imprimir linhas removidas para debug
                    # print(f"Linha {i} removida: {row}")

        # Salva o arquivo filtrado
        with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(rows)

        print(f"Concluído.")
        print(f"Linhas mantidas: {kept_count}")
        print(f"Linhas removidas: {removed_count}")
        print(f"Arquivo salvo em: {output_file}")
        
    except FileNotFoundError:
        print(f"Erro: Arquivo '{input_file}' não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    # Define os caminhos dos arquivos
    input_path = 'tub_index_limpo.csv'
    # Vamos salvar num novo arquivo para garantir a integridade, 
    # mas se o usuário quiser substituir, basta renomear depois ou ajustar aqui.
    output_path = 'tub_index_com_links.csv' 
    
    filtrar_csv(input_path, output_path)
