import re
import os
import glob
import csv

# Definir o padrão da expressão regular para extrair IP, data e requisição GET
log_pattern = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+) - - \[(?P<datetime>[^\]]+)\] "(?P<request>GET [^"]+)"'
)

# Caminho relativo para o diretório que contém os arquivos de log
log_dir_path = './logs'

# Lista de URLs para filtrar
url_patterns = [
    r'registrar/',
    r'logout/',
    r'update-profile/',
    r'cursos/',
    r'ch/',
    r'inscricoes/',
    r'curso_detail/\d+',
    r'curso_detail/\d+/[^/]+',
    r'inscricao_existente/',
    r'inscrever/\d+/',
    r'avaliacao/\d+/',
    r'inscricao_cancelar/\d+/',
    r'validar_ch/',
    r'download_all_pdfs/',
    r'generate_all_pdfs/\d+/',
    r'generate_all_pdfs/\d+/\d+/',
    r'generate_single_pdf/\d+/',
    r'reset-password/',
    r'change-password/',
    r'curadoria_show/',
    r'votar/',
]

# Função para verificar se a URL contém qualquer um dos padrões
def url_matches_any_pattern(url, patterns):
    for pattern in patterns:
        if re.search(pattern, url):
            return True
    return False

# Função para extrair dados de um único arquivo de log
def extract_log_data_from_file(log_file_path):
    extracted_data = []
    
    with open(log_file_path, 'r') as file:
        for line in file:
            match = log_pattern.search(line)
            if match:
                datetime_str = match.group('datetime')
                date, time = datetime_str.split(':', 1)[0], datetime_str.split(':', 1)[1:]
                time = ":".join(time)
                request_url = match.group('request').split(' ')[1]
                
                if '/accounts' not in request_url and '/admin' not in request_url:
                    if url_matches_any_pattern(request_url, url_patterns):
                        # Verifica e substitui requests que contêm '/ch/' ou '/ch/?'
                        if request_url.startswith('/ch/?') and len(request_url) > 4:
                            request_url = '/ch/post'
                        
                        extracted_data.append({
                            'ip': match.group('ip'),
                            'date': date,
                            'time': time,
                            'request': request_url
                        })
    
    return extracted_data

# Função para processar todos os arquivos de log no diretório
def process_all_log_files(log_dir_path):
    all_extracted_data = []
    # Usar glob para corresponder ao padrão de nome dos arquivos
    log_files = glob.glob(os.path.join(log_dir_path, 'access.log*'))
    
    if not log_files:
        print("Nenhum arquivo de log encontrado. Verifique o caminho do diretório.")
        return []
    
    for log_file in log_files:
        all_extracted_data.extend(extract_log_data_from_file(log_file))
    
    return all_extracted_data

# Função para salvar os dados extraídos em um arquivo CSV
def save_to_csv(data, output_file_path):
    with open(output_file_path, 'w', newline='') as csvfile:
        fieldnames = ['ip', 'date', 'time', 'request']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)

# Caminho do arquivo de saída CSV
output_csv_path = 'output.csv'

# Chamar a função e armazenar os dados extraídos de todos os arquivos
all_log_data = process_all_log_files(log_dir_path)

# Salvar os dados extraídos no arquivo CSV
if all_log_data:
    save_to_csv(all_log_data, output_csv_path)
    print(f"Dados salvos no arquivo {output_csv_path}")
else:
    print("Nenhum dado foi extraído para salvar.")
