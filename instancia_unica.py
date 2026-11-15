
import ctypes
from ctypes import wintypes

ERROR_ALREADY_EXISTS = 183

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

kernel32.CreateMutexW.argtypes = [
    ctypes.c_void_p,
    wintypes.BOOL,
    wintypes.LPCWSTR
]
kernel32.CreateMutexW.restype = wintypes.HANDLE

kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL


def obtener_instancia_unica():
    nombre = "Local\\DataCleanPro_InstanciaPrincipal"

    manejador = kernel32.CreateMutexW(
        None,
        False,
        nombre
    )

    if not manejador:
        raise ctypes.WinError(ctypes.get_last_error())

    if ctypes.get_last_error() == ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(manejador)
        return None

    return manejador


def liberar_instancia(manejador):
    if manejador:
        kernel32.CloseHandle(manejador)
