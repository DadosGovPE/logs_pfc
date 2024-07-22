import os
import paramiko
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar logging para diagnóstico detalhado
logging.basicConfig(level=logging.DEBUG)

# Função para baixar arquivos de um diretório SFTP
def download_files_from_sftp():
    sftp_host = os.getenv('SFTP_HOST')
    sftp_user = os.getenv('SFTP_USER')
    sftp_pass = os.getenv('SFTP_PASS')
    sftp_port = int(os.getenv('SFTP_PORT', 22))  # Porta padrão é 22 se não especificada
    sftp_dir = os.getenv('SFTP_DIR')
    local_dir = os.getenv('LOCAL_DIR')

    try:
        # Conectar ao servidor SFTP
        logging.info(f"Conectando ao servidor SFTP {sftp_host}:{sftp_port} com o usuário {sftp_user}")
        transport = paramiko.Transport((sftp_host, sftp_port))
        transport.connect(username=sftp_user, password=sftp_pass)
        logging.info("Conexão SFTP estabelecida com sucesso.")
        
        # Inicializar SFTP
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Verificar se o diretório local existe
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        # Listar arquivos no diretório
        try:
            filenames = sftp.listdir(sftp_dir)
            logging.debug(f"Arquivos encontrados: {filenames}")
        except IOError as e:
            logging.error(f"Erro ao listar arquivos no diretório remoto {sftp_dir}: {e}")
            return

        # Baixar cada arquivo
        for filename in filenames:
            remote_filepath = os.path.join(sftp_dir, filename)
            local_filepath = os.path.join(local_dir, filename)
            try:
                sftp.get(remote_filepath, local_filepath)
                logging.info(f"Arquivo {filename} baixado com sucesso.")
            except Exception as e:
                logging.error(f"Erro ao baixar o arquivo {filename}: {e}")

        # Fechar a conexão SFTP
        sftp.close()
        transport.close()
        logging.info("Conexão SFTP fechada com sucesso.")
    
    except paramiko.AuthenticationException:
        logging.error("Falha de autenticação. Verifique suas credenciais.")
    except paramiko.SSHException as sshException:
        logging.error(f"Erro de SSH: {sshException}")
    except paramiko.SFTPError as sftpError:
        logging.error(f"Erro de SFTP: {sftpError}")
    except Exception as e:
        logging.error(f"Erro ao conectar ao SFTP: {e}")

# Baixar arquivos
download_files_from_sftp()
