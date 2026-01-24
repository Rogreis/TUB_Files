import faiss
import pickle
import os
import sys
import time
from sentence_transformers import SentenceTransformer

# Caminho para o modelo treinado (mesmo prefixo usado no treinamento)
MODEL_PREFIX = os.path.join("dados_modelo", "tub_modelo")

class MotorBusca:
    def __init__(self, model_prefix):
        self.index_path = f"{model_prefix}.index"
        self.meta_path = f"{model_prefix}_meta.pkl"
        self.model = None
        self.index = None
        self.metadata = None

    def carregar(self):
        """Carrega os arquivos do modelo e inicializa a IA."""
        if not os.path.exists(self.index_path) or not os.path.exists(self.meta_path):
            print(f"Erro Crítico: Arquivos do modelo não encontrados em '{MODEL_PREFIX}'.")
            print("Certifique-se de executar o script 'treinar_modelo.py' primeiro.")
            return False

        print("--> Carregando Inteligência Artificial (SentenceTransformer)...")
        # Carrega o modelo de linguagem (transforma texto em números)
        # device='cpu' garante que rode em qualquer máquina
        self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

        print("--> Carregando Índice de Busca Rápida (FAISS)...")
        self.index = faiss.read_index(self.index_path)

        print("--> Carregando Metadados (Textos e Links)...")
        with open(self.meta_path, "rb") as f:
            self.metadata = pickle.load(f)
            
        print("--> Sistema Pronto!\n")
        return True

    def buscar(self, query, top_k=5):
        """Executa a busca e retorna os resultados formatados."""
        if not query.strip():
            return []

        start_time = time.time()

        # 1. Converter pergunta em vetor
        vector = self.model.encode([query])
        
        # 2. Normalizar (para similaridade de cosseno)
        faiss.normalize_L2(vector)
        
        # 3. Buscar no índice
        scores, indices = self.index.search(vector, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            score = scores[0][i]
            # O índice retornado pelo FAISS corresponde à posição na lista de metadados
            if idx < len(self.metadata):
                item = self.metadata[idx]
                results.append({
                    "rank": i + 1,
                    "score": score,
                    "assunto": item[0],
                    "links": item[1]
                })
        
        elapsed = time.time() - start_time
        return results, elapsed

def main():
    print("========================================================")
    print("       BUSCA SEMÂNTICA - INTERFACE INTERATIVA")
    print("========================================================")

    buscador = MotorBusca(MODEL_PREFIX)
    sucesso = buscador.carregar()

    if not sucesso:
        sys.exit(1)

    print("Instruções: Digite sua pesquisa e tecle ENTER.")
    print("            Digite 'sair' ou 'exit' para encerrar.\n")

    while True:
        try:
            termo = input("\nO que você deseja buscar? > ").strip()
            
            if termo.lower() in ['sair', 'exit', 'quit']:
                print("Encerrando...")
                break
            
            if not termo:
                continue

            resultados, tempo = buscador.buscar(termo)

            print(f"\n--- Resultados para: '{termo}' ({tempo:.4f}s) ---")
            
            if not resultados:
                print("Nenhum resultado relevante encontrado.")
            else:
                for res in resultados:
                    # Formatação visual do score (Ex: 0.75 -> 75%)
                    score_pct = res['score'] * 100
                    print(f"#{res['rank']} [{score_pct:.1f}%] {res['assunto']}")
                    print(f"      Link(s): {res['links']}")
                    print("-" * 40)

        except KeyboardInterrupt:
            print("\nEncerrando...")
            break
        except Exception as e:
            print(f"Ocorreu um erro na busca: {e}")

if __name__ == "__main__":
    main()
