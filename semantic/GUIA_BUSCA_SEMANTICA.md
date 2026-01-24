# Guia de Implementação da Busca Semântica

Este documento descreve o processo realizado para criar o índice de busca semântica a partir do arquivo CSV e como integrar essa funcionalidade na sua aplicação Python final.

## 1. Visão Geral

Diferente de uma busca por palavras-chave exatas (como SQL `LIKE` ou `Ctrl+F`), a busca semântica converte textos em vetores numéricos (embeddings). Isso permite que o sistema encontre resultados que têm o mesmo *significado*, mesmo que não usem exatamente as mesmas palavras.

**Exemplo:**
- Busca: *"rebellion of light bringer"*
- Resultado Semântico: *"Lucifer rebellion"* (o modelo entende que "light bringer" e "Lucifer" estão relacionados).

## 2. Processo de Treinamento (Indexação)

O script `treinar_modelo.py` realizou os seguintes passos:

1.  **Carga de Dados**: Leu o arquivo `tub_index_com_links.csv`.
2.  **Vetorização**: Utilizou o modelo **`all-MiniLM-L6-v2`** da biblioteca `sentence-transformers`.
    -   Este modelo transforma cada frase em um vetor de 384 dimensões.
    -   É otimizado para CPU (leve e rápido), ideal para rodar localmente sem GPU pesada.
3.  **Criação do Índice**: Utilizou a biblioteca **FAISS** (Facebook AI Similarity Search).
    -   Os vetores foram normalizados.
    -   Foi criado um índice `IndexFlatIP` (Inner Product), que com vetores normalizados equivale à "Similaridade de Cosseno".
4.  **Persistência**: Salvou dois arquivos essenciais para a aplicação:
    -   `dados_modelo/tub_modelo.index`: O índice vetorial binário (FAISS).
    -   `dados_modelo/tub_modelo_meta.pkl`: Um arquivo Python Pickle contendo a lista original de textos e links, mapeados 1:1 com o índice.

## 3. Integração na Aplicação Final

Para que sua aplicação Python utilize a busca, ela não precisa "treinar" nada novamente. Ela apenas precisa **carregar** os arquivos gerados.

### Dependências
Certifique-se de que o ambiente onde a aplicação vai rodar tenha as bibliotecas instaladas:

```bash
pip install sentence-transformers faiss-cpu numpy
```

### Código de Exemplo para a Aplicação

Abaixo está um exemplo de classe que você pode incluir no seu projeto (`app.py` ou `helpers/search.py`) para gerenciar a busca.

```python
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer

class MotorBuscaSemantica:
    def __init__(self, model_path_prefix):
        """
        Inicializa o motor de busca carregando o índice e os metadados.
        :param model_path_prefix: Caminho base sem extensão (ex: 'dados_modelo/tub_modelo')
        """
        self.index_path = f"{model_path_prefix}.index"
        self.meta_path = f"{model_path_prefix}_meta.pkl"
        self.model = None
        self.index = None
        self.metadata = None
        
        self._carregar_recursos()

    def _carregar_recursos(self):
        if not os.path.exists(self.index_path) or not os.path.exists(self.meta_path):
            raise FileNotFoundError("Arquivos do modelo não encontrados. Execute o script de treinamento primeiro.")

        print("Carregando modelo de IA (isso pode levar alguns segundos)...")
        # Carrega o modelo de transformação de texto em vetor
        self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        
        print("Carregando índice FAISS...")
        # Carrega o índice de busca rápida
        self.index = faiss.read_index(self.index_path)
        
        print("Carregando metadados...")
        # Carrega os dados originais (Assuntos e Links)
        with open(self.meta_path, "rb") as f:
            self.metadata = pickle.load(f)

    def buscar(self, query, top_k=5):
        """
        Realiza a busca semântica para uma string de consulta.
        """
        if not query.strip():
            return []

        # 1. Transformar a pergunta do usuário em vetor
        vector = self.model.encode([query])
        
        # 2. Normalizar vetor (necessário para similaridade de cosseno no FAISS)
        faiss.normalize_L2(vector)
        
        # 3. Buscar os 'k' vizinhos mais próximos
        scores, indices = self.index.search(vector, top_k)
        
        resultados = []
        for i in range(top_k):
            idx = indices[0][i]   # Índice do resultado
            score = scores[0][i]  # Pontuação de similaridade (0 a 1)
            
            # Recupera o dado original usando o índice
            dado_original = self.metadata[idx] # (assunto, links)
            
            resultados.append({
                "score": float(score),
                "assunto": dado_original[0],
                "links": dado_original[1]
            })
            
        return resultados

# --- Exemplo de Uso ---
if __name__ == "__main__":
    # Inicialize apenas UMA VEZ no início da aplicação (é pesado carregar)
    buscador = MotorBuscaSemantica(model_path_prefix="dados_modelo/tub_modelo")
    
    # Faça buscas quantas vezes quiser
    termo = "rebellion of the system sovereign"
    print(f"Buscando por: '{termo}'")
    
    results = buscador.buscar(termo, top_k=3)
    
    for res in results:
        print(f"[{res['score']:.2f}] {res['assunto']} -> {res['links']}")
```

## 4. Arquivos para Deploy

Ao levar sua aplicação para produção ou outro computador, você deve incluir:

1.  A pasta com os arquivos gerados (`dados_modelo/` ou similar).
2.  O arquivo `.index` e o `.pkl`.
3.  O código Python da classe `MotorBuscaSemantica` acima.

Não é necessário levar o arquivo CSV original nem o script de treinamento para o ambiente de produção.
