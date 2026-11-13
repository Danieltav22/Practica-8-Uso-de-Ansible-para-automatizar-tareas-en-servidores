"""Detecta SSH desde WSL y ajusta las IP del inventario del laboratorio."""
from pathlib import Path
import argparse
import re
import socket
import subprocess


def servidor_ssh(host, port):
    try:
        with socket.create_connection((host, port), timeout=2) as conexion:
            conexion.settimeout(2)
            return conexion.recv(128).startswith(b'SSH-')
    except OSError:
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', help='IP de Windows accesible desde WSL, si se necesita indicarla manualmente')
    args = parser.parse_args()
    candidatos = [args.host] if args.host else ['127.0.0.1']
    if not args.host:
        resultado = subprocess.run(['ip', '-4', 'route', 'show', 'default'], capture_output=True, text=True, check=True)
        coincidencia = re.search(r'\bvia\s+(\S+)', resultado.stdout)
        if coincidencia:
            candidatos.append(coincidencia.group(1))
    for host in dict.fromkeys(candidatos):
        if all(servidor_ssh(host, puerto) for puerto in range(2221, 2226)):
            ruta = Path(__file__).resolve().parent / 'inventario.ini'
            texto = ruta.read_text(encoding='utf-8')
            nuevo, cantidad = re.subn(r'ansible_host=\S+', 'ansible_host=' + host, texto)
            if cantidad != 5:
                raise SystemExit('El inventario debe contener exactamente cinco ansible_host.')
            ruta.write_text(nuevo, encoding='utf-8')
            print(f'Inventario actualizado: {host}, puertos 2221 a 2225. Se detectaron cinco servidores SSH.')
            return
    raise SystemExit('No se pudo acceder a los cinco servidores SSH. Comprueba docker compose ps. Si estan activos, revisa la conexion WSL-Windows y el firewall; no se cambio el inventario.')


if __name__ == '__main__':
    main()
