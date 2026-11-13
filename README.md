# Práctica 3: automatización con Ansible y cinco servidores Ubuntu

**Materia:** Electiva 2  
**Estudiante:** Daniel Tavera

## Objetivo
Crear cinco contenedores Ubuntu con SSH y ejecutar Ansible desde Ubuntu en WSL para actualizar la caché de APT, crear el usuario `itla`, crear `/app/hola.txt` e instalar `cowsay` y `htop` en los cinco servidores.

## Archivos
- `Dockerfile`: Ubuntu 24.04 con SSH, Python y el usuario `ansible`, contraseña `ansible` y sudo sin contraseña.
- `docker-compose.yml`: cinco servicios basados en la misma imagen.
- `inventario.ini`: nombres, direcciones, puertos, usuario y contraseña.
- `ansible.cfg`: selecciona el inventario y desactiva la comprobación de claves SSH para este laboratorio.
- `playbook.yml`: realiza las tareas solicitadas.
- `verificar.yml`: comprueba los resultados en los cinco servidores.
- `configurar_inventario.py`: ajusta las direcciones del inventario según la conectividad desde WSL.

## 1. Crear los cinco servidores desde Windows
Con Docker Desktop iniciado, extraer el ZIP y entrar en la carpeta `practica-3-ansible`, donde está `docker-compose.yml`.

Escribir `cmd` en la barra de direcciones del Explorador y ejecutar:

```cmd
docker compose up -d
docker compose ps
```

Compose construye la imagen si no existe. Deben aparecer cinco servicios en ejecución. Cada contenedor genera sus propias claves SSH al arrancar.

| Servidor | Puerto SSH publicado en Windows | Puerto dentro del contenedor |
|---|---|---|
| servidor1 | 2221 | 22 |
| servidor2 | 2222 | 22 |
| servidor3 | 2223 | 22 |
| servidor4 | 2224 | 22 |
| servidor5 | 2225 | 22 |

Estos contenedores simulan servidores; no son cinco máquinas virtuales completas.

## 2. Abrir Ubuntu en WSL
WSL ya puede estar instalado porque Docker lo necesita. En Inicio, buscar y abrir **Ubuntu**.

Si Ubuntu no aparece, consultar desde CMD:

```cmd
wsl --list --verbose
```

Si solo aparece `docker-desktop` y no Ubuntu, instalar la distribución desde CMD como administrador:

```cmd
wsl --install -d Ubuntu
```

Reiniciar si Windows lo solicita y abrir Ubuntu. Crear el usuario y contraseña de tu Ubuntu personal cuando se solicite. Esta contraseña de WSL es distinta de la cuenta `ansible` que existe dentro de los cinco contenedores. Al escribir una contraseña en Linux no aparecen caracteres en pantalla: es normal.

## 3. Instalar Ansible dentro de Ubuntu
Los siguientes comandos se ejecutan en **Ubuntu**, no en CMD ni en los cinco contenedores:

```bash
sudo apt update
sudo apt install -y ansible sshpass openssh-client python3
ansible --version
```

`sshpass` permite la autenticación SSH con contraseña requerida por la práctica.

## 4. Copiar los archivos al directorio personal de Ubuntu
Para que Ansible lea correctamente `ansible.cfg`, trabajar en el directorio personal de Linux en lugar de una carpeta de Windows bajo `/mnt/c`.

En Ubuntu ejecutar, uno por uno:

```bash
mkdir -p ~/practica3
cd ~/practica3
explorer.exe .
```

Se abre el Explorador de Windows en esa carpeta de Ubuntu. Copiar allí **el contenido** de `practica-3-ansible`: Dockerfile, docker-compose.yml, inventario.ini, ansible.cfg, playbook.yml, verificar.yml, configurar_inventario.py y README.md.

No copiar solamente el ZIP ni dejar una carpeta adicional entre `practica3` y los archivos.

Volver a Ubuntu y comprobar:

```bash
ls
```

Mantener los contenedores creados en el paso 1. No es necesario volver a ejecutar Compose desde esta copia en Ubuntu.

## 5. Ajustar el inventario y comprobar la conexión
Dentro de `~/practica3`, ejecutar:

```bash
python3 configurar_inventario.py
cat inventario.ini
ansible servidores -m ping
```

El programa prueba SSH en los cinco puertos usando localhost y, si hace falta, la IP de Windows obtenida de la ruta predeterminada de WSL. Solo actualiza el inventario si los cinco servidores responden como SSH.

Con WSL en modo NAT se utiliza normalmente la IP de Windows; con red reflejada puede funcionar `127.0.0.1`. Por eso no se depende de las IP internas de los contenedores de Docker Desktop.

Los cinco nombres comparten la IP del equipo que publica los puertos, pero cada puerto conduce a un contenedor distinto. `ansible_host` indica esa IP y `ansible_port` distingue cada servidor.

El resultado de Ansible debe mostrar `SUCCESS` y `pong` para servidor1, servidor2, servidor3, servidor4 y servidor5. Este ping usa SSH y Python, no es el ping de red de Windows.

Si el script falla, revisar `docker compose ps` desde la carpeta original en CMD y esperar a que SSH arranque. Si los cinco están activos, revisar la comunicación WSL-Windows y las reglas del firewall para Docker. No desactivar el firewall. Si se identifica manualmente una IP accesible de Windows, puede indicarse con `python3 configurar_inventario.py --host IP_DE_WINDOWS`, reemplazando el marcador por la IP real.

## 6. Ejecutar la automatización
En Ubuntu, desde `~/practica3`:

```bash
ansible-playbook --syntax-check playbook.yml
ansible-playbook playbook.yml
```

El playbook usa `become: true` para ejecutar con sudo en los servidores. Hace lo siguiente:
1. Actualiza la caché de APT.
2. Crea `itla` con directorio personal y shell Bash. No se solicita ni se configura contraseña de inicio de sesión para este usuario.
3. Crea `/app`, propiedad de `itla`.
4. Crea `/app/hola.txt` con el contenido `Hola mundo desde Ansible.`.
5. Instala `cowsay` y `htop`.

Al finalizar, el resumen PLAY RECAP debe mostrar los cinco servidores con `failed=0` y `unreachable=0`.

## 7. Verificar los cambios
En Ubuntu:

```bash
ansible-playbook verificar.yml
ansible servidores -m command -a "cat /app/hola.txt"
ansible servidores -m command -a "/usr/games/cowsay Hola ITLA"
```

El playbook de verificación comprueba que existe `itla`, que el archivo tiene el contenido esperado y que ambos paquetes están instalados. `cowsay` dibuja una vaca con el saludo. `htop` es interactivo; su instalación se comprueba mediante los paquetes del sistema.

Opcionalmente, desde CMD en la carpeta original:

```cmd
docker compose exec servidor1 htop
```

Pulsar `q` para salir de htop.

## 8. Evidencias y entrega
Guardar capturas de:
- `docker compose ps` mostrando los cinco servicios.
- `ansible servidores -m ping` con cinco respuestas `pong`.
- PLAY RECAP de la automatización con cinco servidores y cero fallos.
- La verificación y/o el contenido de `/app/hola.txt` en los cinco servidores.

Crear un repositorio público, nombre sugerido `electiva2-practica3-ansible`, y subir todos los archivos de esta carpeta, sin el ZIP. Para conservar la IP detectada, copiar el `inventario.ini` ajustado desde Ubuntu si se suben los archivos originales de Windows. Otro equipo deberá ejecutar nuevamente el ajuste de inventario.

Publicar en el foro la URL del repositorio si la plataforma solicita el enlace. Estas instrucciones no afirman que las pruebas estén ejecutadas: las evidencias deben obtenerse al realizar la práctica.

## 9. Detener el laboratorio
Desde CMD en la carpeta original:

```cmd
docker compose stop
```

Para continuar conservando los cambios:

```cmd
docker compose start
```

`docker compose down` elimina los contenedores. Como los cambios de Ansible están dentro de ellos, al recrearlos se debe ejecutar nuevamente el playbook.

## Alcance del laboratorio
La contraseña `ansible` y sudo sin contraseña se configuran porque lo pide el ejercicio. Los puertos SSH publicados pueden ser accesibles desde otras interfaces del PC según el firewall; esta configuración corresponde a un laboratorio local.

## Referencias
- https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html
- https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html
- https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_module.html
- https://learn.microsoft.com/en-us/windows/wsl/networking
- https://docs.docker.com/desktop/features/networking/
