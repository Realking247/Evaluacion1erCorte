"""Explora archivos JSON y CSV de un directorio de Google Drive."""

import json
import os
from datetime import datetime
from typing import Any, Dict, List


DIRECTORIO = "/content/drive/My Drive/LPII_2026"
EXTENSIONES_PERMITIDAS = {".json", ".csv"}
ARCHIVO_INVENTARIO = "inventario.json"


def _validar_registros_inventario(datos: Any) -> List[Dict[str, Any]]:
    """Comprueba que el inventario sea una lista de registros tipo objeto."""
    if not isinstance(datos, list):
        raise ValueError("El contenido de inventario.json debe ser una lista.")
    if any(not isinstance(registro, dict) for registro in datos):
        raise ValueError(
            "Cada registro de inventario.json debe ser un objeto JSON."
        )
    return datos


def list_files_in_directory(directorio: str) -> Dict[str, Any]:
    """Lista archivos JSON/CSV y devuelve metadatos e inventario para una API."""
    try:
        nombres = os.listdir(directorio)
    except FileNotFoundError:
        mensaje = f"Directorio no encontrado: {directorio}"
        print(mensaje)
        return {
            "success": False,
            "directory": directorio,
            "files": [],
            "inventory": None,
            "error": {"type": "FileNotFoundError", "message": mensaje},
        }

    archivos = []
    print(f"Archivos JSON y CSV en {directorio}:")
    for nombre in nombres:
        ruta = os.path.join(directorio, nombre)
        extension = os.path.splitext(nombre)[1].lower()
        if extension not in EXTENSIONES_PERMITIDAS or not os.path.isfile(ruta):
            continue

        tamano_kb = os.path.getsize(ruta) / 1024
        fecha_modificacion = os.path.getmtime(ruta)
        metadatos = {
            "name": nombre,
            "path": ruta,
            "extension": extension,
            "size_kb": round(tamano_kb, 2),
            "last_modified": datetime.fromtimestamp(
                fecha_modificacion
            ).astimezone().isoformat(timespec="seconds"),
        }
        archivos.append(metadatos)
        print(
            f" - {nombre} | {metadatos['size_kb']} KB | "
            f"{metadatos['last_modified']}"
        )

    ruta_inventario = os.path.join(directorio, ARCHIVO_INVENTARIO)
    inventario = None
    if os.path.isfile(ruta_inventario):
        try:
            with open(ruta_inventario, "r", encoding="utf-8") as archivo:
                inventario = _validar_registros_inventario(json.load(archivo))
        except (json.JSONDecodeError, ValueError) as error:
            mensaje = f"Inventario invalido: {error}"
            print(mensaje)
            return {
                "success": False,
                "directory": directorio,
                "files": archivos,
                "inventory": None,
                "error": {"type": type(error).__name__, "message": mensaje},
            }

        print(f"Inventario valido: {len(inventario)} registros.")
    else:
        print(f"No se encontró {ARCHIVO_INVENTARIO}; se omite su parseo.")

    return {
        "success": True,
        "directory": directorio,
        "files": archivos,
        "inventory": inventario,
        "error": None,
    }


def mount_google_drive() -> None:
    """Monta Google Drive; disponible al ejecutar en un cuaderno de Colab."""
    try:
        from google.colab import drive
    except ImportError as error:
        raise RuntimeError(
            "El montaje de Google Drive solo está disponible en Google Colab."
        ) from error

    drive.mount("/content/drive")


if __name__ == "__main__":
    mount_google_drive()
    resultado = list_files_in_directory(DIRECTORIO)
    if not resultado["success"]:
        raise SystemExit(1)
