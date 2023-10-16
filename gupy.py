from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import sys
import time
class Gupy:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get('https://login.gupy.io/candidates/signin')
        self.wait = WebDriverWait(self.driver, 10)
    
    def aceitar_cookies(self):
        try:
            self.driver.find_element(By.XPATH, "//*[@id='onetrust-accept-btn-handler']")\
                .click() 
        except:
            pass

    def login_com_linkedin(self, usuario, senha):
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='linkedin-access-button']")))\
                .click()
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='username']")))\
                .send_keys(usuario)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "password")))\
                .send_keys(senha)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@data-litms-control-urn='login-submit']")))\
                .click()
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "oauth__auth-form__submit-btn")))\
                .click()
        except:
            print("Erro ao fazer login com LinkedIn")

    def obter_lista_vagas_por_pagina(self):
        try:
            ul_lista_vagas = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//ul[@aria-labelledby='my-applications']")))
            lista_vagas = ul_lista_vagas.find_elements(By.TAG_NAME, "li")
            return lista_vagas
        except:
            print("Erro ao obter lista de vagas")
            return []

    def obter_conteudo_json(self, path):
        try:
            if self.verificar_se_existe_o_json(path):
                with open(path, 'r') as json_file:
                    data = json.load(json_file)
                return data
            else:
                self.gravar_vagas_no_json(path, {})
                return self.obter_conteudo_json(path)     
        except:
            print("Erro ao abrir arquivo JSON")
            return {}

    def verificar_se_existe_o_json(self, path):
        try:
            with open(path, 'r') as json_file:
                data = json.load(json_file)
            return True
        except:
            return False

    def adicionar_vagas_no_json(self, path, dicionario_vagas):
        try:
            data = self.obter_conteudo_json(path)
            
            for empresa in dicionario_vagas:
                encontrou_vaga = False
                try:
                    for i in range(len(data[empresa])):
                        for j in range(len(dicionario_vagas[empresa])):
                            if data[empresa][i]['titulo'] == dicionario_vagas[empresa][j]['titulo']:
                                data[empresa][i]['progresso'] = dicionario_vagas[empresa][j]['progresso']
                                encontrou_vaga = True
                    if not encontrou_vaga:
                        data[empresa].append(dicionario_vagas[empresa][0])
                except:
                    data[empresa] = dicionario_vagas[empresa]
            return data
        except:
            print("Erro ao adicionar vagas no arquivo JSON") 
            return dicionario_vagas

    def gravar_vagas_no_json(self, path, dicionario_vagas):
        try:   
            with open(path, 'w') as json_file:
                json.dump(dicionario_vagas, json_file)
        except:
            print("Erro ao gravar vagas no arquivo JSON")
        
    def obter_mudancas_no_progresso(self, dicionario_vagas):
        try:
            path = 'vagas.json'
            vagas_json = self.obter_conteudo_json(path)
            mudancas = {}

            for empresa in dicionario_vagas:
                try:
                    for i in range(len(vagas_json[empresa])):
                        if vagas_json[empresa][i]['titulo'] == dicionario_vagas[empresa][0]['titulo']:
                            if vagas_json[empresa][i]['progresso'] != dicionario_vagas[empresa][0]['progresso']:
                                mudancas[empresa] = []
                                mudancas[empresa].append({
                                    "titulo": vagas_json[empresa][i]['titulo'],
                                    "progresso": vagas_json[empresa][i]['progresso'],
                                    "novo_progresso": dicionario_vagas[empresa][0]['progresso']
                                })
                except:
                    pass
                finally:
                    if mudancas == {}:
                        return {}
            return mudancas
        except:
            print("Erro ao obter mudanças no progresso")
            return {}

    def nao_esta_na_ultima_pagina(self):
        try:
            botao_proxima_pagina = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-testid='pagination-next-button']")))
            if botao_proxima_pagina.get_attribute("aria-disabled") == "true":
                return False
            else:
                return True
        except:
            print("Erro ao verificar se está na última página")
            return False

    def avancar_pagina(self):
        try:
            botao_proxima_pagina = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-testid='pagination-next-button']")))
            botao_proxima_pagina.click()
        except:
            print("Erro ao avançar página")

    def gerar_dicionario_vagas(self):
        vagas_dict = {}
        vagas = self.obter_lista_vagas_por_pagina()
        for vaga in vagas:
            empresa = vaga.find_element(By.XPATH, ".//div[@class='sc-a3bd7ea-4 gXFtLl']")
            vagas_dict[empresa.text] = []
        for vaga in vagas:
            empresa = vaga.find_element(By.XPATH, ".//div[@class='sc-a3bd7ea-4 gXFtLl']").text
            titulo = vaga.find_element(By.TAG_NAME, "h2").text
            progresso = vaga.find_element(By.CSS_SELECTOR, ".linear-progress__description > span:nth-child(2)").text

            vagas_dict[empresa].append({
                "titulo": titulo,
                "progresso": progresso
            })
            
        return vagas_dict

    def navegar_e_realizar_buscas_todas_paginas(self):
        try:
            trava = 0
            count = 0
            while True:
                vagas_pagina_atual = self.gerar_dicionario_vagas()
                print(vagas_pagina_atual)
                print("\n")
                mudancas_vagas = self.obter_mudancas_no_progresso(vagas_pagina_atual)
                    
                self.gravar_vagas_no_json('mudancas_vagas.json', mudancas_vagas)

                vagas_formato_json = self.adicionar_vagas_no_json('vagas.json', vagas_pagina_atual)
                self.gravar_vagas_no_json('vagas.json', vagas_formato_json)
                
                if trava == 1:
                    break
                if self.nao_esta_na_ultima_pagina() == False:
                    trava = 1
                    break
                self.avancar_pagina()
        except:
            print("Erro ao navegar e realizar buscas")
    def fechar_pop_up_opniao(self):
        try:
            botao_fechar = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//span[@class='_hj-BfLwc__styles__openStateToggleIcon _hj-mtJG6__styles__surveyIcons']")))
            botao_fechar.click()
            return True
        except:
            print("Erro ao fechar popup de opinião")
            return False
    def executar(self, usuario, senha):
        try:
            self.aceitar_cookies()
            self.login_com_linkedin(usuario, senha)
            self.navegar_e_realizar_buscas_todas_paginas()
        except:
            print("Erro ao executar")


Gupy().executar(sys.argv[1], sys.argv[2])