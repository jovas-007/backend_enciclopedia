from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
from enciclopedia_api.models import Episodios  # Asegúrate de que el nombre del modelo sea correcto
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
from tqdm import tqdm  # Para mostrar el progreso

class Command(BaseCommand):
    help = 'Extrae los episodios de Dragon Ball de las páginas web'

    def handle(self, *args, **kwargs):
        # URLs de las tres series
        url_dict = {
            "Z": "https://dbzlatino.com/",
            "GT": "https://dbzlatino.com/capitulos-de-dragon-ball-gt/",
            "Super": "https://dbzlatino.com/dragon-ball-super/"
        }

        # Proceso para cada URL
        for serie, url in url_dict.items():
            self.stdout.write(self.style.SUCCESS(f"Iniciando scraping de {serie} desde {url}..."))
            self.scrape_episodios(serie, url)

    def scrape_episodios(self, serie, url):
        # Configurar reintentos para la solicitud
        session = requests.Session()
        retry = Retry(
            total=10,  # Aumentamos el número de reintentos
            backoff_factor=3,  # Aumento del tiempo de espera entre reintentos
            status_forcelist=[500, 502, 503, 504],  # Qué códigos de error forzar reintentos
            allowed_methods=["HEAD", "GET", "OPTIONS"]  # Métodos HTTP que se reintentarán
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        # Añadir encabezado para simular un navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            # Realizar la solicitud
            response = session.get(url, headers=headers, verify=False)  # Desactivar SSL si es necesario

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Error al acceder a la página: {response.status_code}'))
                return

            # Añadir un retraso para evitar sobrecargar el servidor
            time.sleep(5)  # Esperar 5 segundos entre solicitudes

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extraer el nombre del arco (usando el <h1 class="entry-title">)
            arco = f"Dragon Ball {serie}"  # Definimos el arco según la serie
            self.stdout.write(self.style.SUCCESS(f'Arco: {arco}'))

            # Extraer las sagas (usando el <h2 class="sagatitle">)
            sagas = soup.find_all('h2', class_='sagatitle')  # Encontramos todas las sagas
            self.stdout.write(self.style.SUCCESS(f'Encontradas {len(sagas)} sagas'))

            # Buscar todos los episodios en los enlaces <a>
            episodios = soup.find_all('a', href=True)  # Encontrar todos los enlaces con atributo href

            episodios_para_guardar = []

            # Usamos tqdm para mostrar el progreso del scraping
            for epi in tqdm(episodios, desc="Scrapeando episodios", unit="episodio"):
                try:
                    # Filtrar solo los episodios (enlaces que contienen 'dragon-ball-z-capitulo' o similar)
                    if f"dragon-ball-{serie.lower()}-capitulo" in epi['href']:
                        # Extraer el nombre del episodio y el número (basado en el texto dentro de <a>)
                        texto_episodio = epi.text.strip()
                        if '–' in texto_episodio:
                            numero, nombre = texto_episodio.split('–', 1)
                            numero = int(numero.strip())  # Convertir el número a entero
                            nombre = nombre.strip()  # Eliminar espacios adicionales

                            # Obtener la URL del episodio (completar con la base URL si es relativa)
                            url_episodio = epi['href']
                            if not url_episodio.startswith("http"):
                                url_episodio = f"https://dbzlatino.com{url_episodio}"  # Concatenar si la URL es relativa

                            # Asignar la saga de acuerdo con el número de episodio para cada serie
                            saga = self.asignar_saga(serie, numero)

                            # Crear el objeto Episodios y agregarlo a la lista
                            episodio = Episodios(
                                nombre=nombre,
                                saga=saga,  # Asignamos la saga
                                arco=arco,  # Asignamos el arco
                                numero=numero,
                                url=url_episodio,
                                update=None  # Podemos dejar update como None, Django lo actualizará automáticamente cuando se guarda
                            )

                            episodios_para_guardar.append(episodio)

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error al procesar el episodio: {str(e)}'))

            # Guardar todos los episodios de una vez
            if episodios_para_guardar:
                Episodios.objects.bulk_create(episodios_para_guardar)
                self.stdout.write(self.style.SUCCESS(f'{len(episodios_para_guardar)} episodios guardados correctamente'))

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Error en la conexión: {str(e)}'))

    def asignar_saga(self, serie, numero):
        # Asignamos la saga según el número del episodio y la serie
        if serie == "GT":
            if 1 <= numero <= 21:
                return "EL GRAN VIAJE"
            elif 22 <= numero <= 41:
                return "Bebi"
            elif 42 <= numero <= 47:
                return "Súper Número 17"
            elif 48 <= numero <= 64:
                return "Dragones"
            else:
                return "Saga desconocida"

        elif serie == "Super":
            if 1 <= numero <= 14:
                return "La Batalla de los Dioses"
            elif 15 <= numero <= 27:
                return "La resurrección de Freezer"
            elif 28 <= numero <= 41:
                return "Universo"
            elif 42 <= numero <= 46:
                return "Planeta Potof"
            elif 47 <= numero <= 76:
                return "Goku Black"
            elif 77 <= numero <= 131:
                return "Torneo del poder"
            else:
                return "Saga desconocida"
        
        else:  # Dragon Ball Z
            if 1 <= numero <= 36:
                return "Saga Saiyajin"
            elif 37 <= numero <= 107:
                return "SAGA DE FREEZER"
            elif 108 <= numero <= 117:
                return "GARLICK JR."
            elif 118 <= numero <= 191:
                return "SAGA DE CELL"
            elif 192 <= numero <= 199:
                return "TORNEO DEL OTRO MUNDO"
            elif 200 <= numero <= 291:
                return "SAGA DE MAJIN BUU"
            else:
                return "Saga desconocida"
