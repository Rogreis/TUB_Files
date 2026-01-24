import csv
import sys
import os
import pickle
import time

# Tenta importar as bibliotecas necessárias
try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    print("Erro: Bibliotecas necessárias não encontradas.")
    print(f"Detalhe: {e}")
    print("\nPor favor, instale as dependências executando:")
    print("pip install sentence-transformers faiss-cpu numpy")
    sys.exit(1)

def treinar_modelo(csv_input, model_output_prefix):
    """
    Treina (indexa) os dados do CSV para busca semântica.
    Usa apenas CPU conforme solicitado.
    """
    print(f"--- Iniciando Treinamento (Indexação) ---")
    print(f"Arquivo entrada: {csv_input}")
    
    # 1. Ler o CSV
    assuntos = []
    links = []
    
    if not os.path.exists(csv_input):
        print(f"Erro: Arquivo {csv_input} não encontrado.")
        return

    print("Lendo arquivo CSV...")
    with open(csv_input, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'assunto' in row and 'links' in row:
                assuntos.append(row['assunto'])
                links.append(row['links'])
    
    print(f"Total de registros carregados: {len(assuntos)}")

    # 2. Carregar o Modelo de IA
    # 'all-MiniLM-L6-v2' é ideal para CPU: rápido e com boa acurácia para inglês.
    # Se o conteúdo fosse muito misturado ou puramente português, 'paraphrase-multilingual-MiniLM-L12-v2' seria uma alternativa.
    model_name = 'all-MiniLM-L6-v2'
    print(f"Carregando modelo SentenceTransformer: {model_name} (Dispositivo: CPU)...")
    model = SentenceTransformer(model_name, device='cpu')

    # 3. Gerar Embeddings (Vetores)
    print("Gerando embeddings (pode demorar alguns minutos dependendo do tamanho)...")
    start_time = time.time()
    
    # show_progress_bar=True mostra uma barra se tqdm estiver instalado
    embeddings = model.encode(assuntos, batch_size=64, show_progress_bar=True, convert_to_numpy=True)
    
    end_time = time.time()
    print(f"Embeddings gerados em {end_time - start_time:.2f} segundos.")

    # 4. Criar Índice FAISS
    # Normalizamos os vetores para usar 'Inner Product' (IP) como Similaridade de Cosseno
    print("Normalizando vetores e criando índice FAISS...")
    faiss.normalize_L2(embeddings)
    
    dimension = embeddings.shape[1]
    # IndexFlatIP é exato e usa produto interno. Com vetores normalizados = Cosseno.
    index = faiss.IndexFlatIP(dimension) 
    index.add(embeddings)
    
    print(f"Índice criado com {index.ntotal} vetores.")

    # 5. Salvar Modelo (Índice + Metadados)
    # Criamos uma pasta 'models' se não existir
    os.makedirs(os.path.dirname(model_output_prefix), exist_ok=True)
    
    index_file = f"{model_output_prefix}.index"
    meta_file = f"{model_output_prefix}_meta.pkl"
    
    print(f"Salvando índice em: {index_file}")
    faiss.write_index(index, index_file)
    
    print(f"Salvando metadados em: {meta_file}")
    with open(meta_file, "wb") as f:
        # Salvamos a lista de links (e assuntos, se quiser recuperar o texto original)
        # Salvando (assunto, link) para poder mostrar o texto original na busca
        metadata = list(zip(assuntos, links))
        pickle.dump(metadata, f)

    print("--- Treinamento Concluído com Sucesso ---")

def testar_modelo(query, model_output_prefix, top_k=5):
    """
    Função simples para testar o modelo treinado.
    """
    print(f"\n--- Testando Modelo com query: '{query}' ---")
    
    index_file = f"{model_output_prefix}.index"
    meta_file = f"{model_output_prefix}_meta.pkl"
    
    if not os.path.exists(index_file) or not os.path.exists(meta_file):
        print("Arquivos do modelo não encontrados. Treine primeiro.")
        return

    # Carregar índice
    index = faiss.read_index(index_file)
    
    # Carregar metadados
    with open(meta_file, "rb") as f:
        metadata = pickle.load(f) # lista de (assunto, links)
        
    # Carregar modelo para codificar a query
    model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
    
    # Buscar
    query_vector = model.encode([query])
    faiss.normalize_L2(query_vector)
    
    # D (scrores), I (índices)
    D, I = index.search(query_vector, k=top_k)
    
    print(f"Resultados para '{query}':")
    for i in range(top_k):
        idx = I[0][i]
        score = D[0][i]
        item = metadata[idx]
        print(f"{i+1}. Score: {score:.4f} | Assunto: {item[0]} | Link: {item[1]}")

if __name__ == "__main__":
    arquivo_entrada = 'tub_index_com_links.csv'
    # Define onde salvar os modelos (ex: pasta 'dados_modelo')
    prefixo_saida = 'model/tub_modelo'
    
    # Executa o treinamento
    treinar_modelo(arquivo_entrada, prefixo_saida)
    
    # Teste rápido
    testar_modelo("lucifer rebellion", prefixo_saida)
