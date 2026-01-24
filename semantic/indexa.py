import json
import csv
import os

def create_faiss_index():
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    
    # 1. Carregar seus tópicos
    try:
        with open("topics.json", "r", encoding="utf-8") as f:
            topics_data = json.load(f) 
            # Supondo estrutura: [{"id": 1, "topic": "Ajustadores", "keywords": "..."}, ...]

        # 2. Preparar textos para indexar (Título + Palavras-chave ajudam muito)
        texts_to_embed = [f"{t['topic']} {t.get('keywords', '')}" for t in topics_data]

        # 3. Carregar modelo leve (all-MiniLM-L6-v2 tem ~80MB e é muito rápido)
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # 4. Criar Embeddings
        embeddings = model.encode(texts_to_embed)

        # 5. Criar Índice FAISS
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

        # 6. Salvar tudo para enviar com o App
        faiss.write_index(index, "static/semantic_index.faiss")
        # Salve também o mapeamento de ID para Tópico se necessário
    except FileNotFoundError:
        print("topics.json not found, skipping FAISS index creation.")

def generate_csv_from_json(json_path, csv_output_path, endings_path="endings_report.txt"):
    print(f"Reading from {json_path}")
    
    special_endings = {"of"} # default fallback
    if os.path.exists(endings_path):
        try:
            with open(endings_path, 'r', encoding='utf-8') as f:
                loaded = [line.strip() for line in f if line.strip()]
                if loaded:
                    special_endings = set(loaded)
            print(f"Loaded {len(special_endings)} special endings from {endings_path}")
        except Exception as e:
            print(f"Error reading endings file: {e}")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    row_count = 0
    with open(csv_output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['assunto', 'links'])

        for item in data:
            title = item.get('Title', '')
            details = item.get('Details', [])
            
            for detail in details:
                detail_type = detail.get('DetailType', 0)
                # Considere apenas os Detais.DetaisType >= 100
                if detail_type >= 100:
                    text = detail.get('Text', '').replace(',', '')
                    links = detail.get('Links', [])
                    
                    text_stripped = text.strip()
                    words = text_stripped.split()
                    
                    match_found = False
                    if words:
                        last_word = words[-1]
                        if last_word in special_endings:
                            match_found = True
                            
                    if match_found:
                        subject = f"{text} {title}"
                    else:
                        subject = f"{title} {text}"
                    
                    # Decodificar HTML entities
                    import html
                    subject = html.unescape(subject)
                    
                    subject = subject.strip().lower()
                    
                    # Links: união de todos os links separados por espaço
                    links_str = " ".join(links)
                    
                    writer.writerow([subject, links_str])
                    row_count += 1
    
    print(f"CSV generated at {csv_output_path} with {row_count} rows.")

def analyze_endings(csv_path):
    print(f"\nAnalyzing endings in {csv_path}...")
    unique_endings = set()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # skip header
        for row in reader:
            if not row: continue
            subject = row[0].strip()
            words = subject.split()
            if words:
                last_word = words[-1]
                if len(last_word) <= 4:
                    unique_endings.add(last_word)
    
    print("Unique endings with 4 or fewer characters:")
    sorted_endings = sorted(list(unique_endings))
    # print(sorted_endings)
    # print(f"Total unique count: {len(sorted_endings)}")

def generate_endings_report(csv_path, report_path):
    print(f"\nGenerating endings report at {report_path}...")
    endings_map = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # skip header
        for row in reader:
            if not row: continue
            subject = row[0].strip()
            words = subject.split()
            if words:
                last_word = words[-1]
                if len(last_word) <= 4:
                    if last_word not in endings_map:
                        endings_map[last_word] = []
                    # We store only up to 5 to save memory, as we only need to print 5
                    if len(endings_map[last_word]) < 5:
                        endings_map[last_word].append(subject)
    
    sorted_endings = sorted(endings_map.keys())
    
    with open(report_path, 'w', encoding='utf-8') as f:
        for ending in sorted_endings:
            f.write(f"{ending}\n")
            for example in endings_map[ending]:
                f.write(f"    {example}\n")
            f.write("\n")
            
    print("Report generated.")

if __name__ == "__main__":
    # Testar a nova função
    json_file = os.path.join("data", "tubIndex_000.json")
    csv_file = "tub_index.csv"
    
    if os.path.exists(json_file):
        generate_csv_from_json(json_file, csv_file)
        
        if os.path.exists(csv_file):
            print(f"\n--- First 10 lines of {csv_file} ---")
            with open(csv_file, 'r', encoding='utf-8') as f:
                for _ in range(10):
                    line = f.readline()
                    if not line:
                        break
                    print(line.strip())
            
            analyze_endings(csv_file)
            #generate_endings_report(csv_file, "endings_reportNOVO.txt")
    else:
        print(f"File {json_file} not found.")