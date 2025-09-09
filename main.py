# organizador_inteligente/main.py
# -------------------------------------------------------------
# Punto de entrada principal
# -------------------------------------------------------------

from __future__ import annotations
import flet as ft
import os
import sys

# Ajustar PYTHONPATH para resolver importaciones relativas
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ui import AppUI
from auth import AuthManager

def main(page: ft.Page):
    """Inicia la aplicación con la interfaz gráfica."""
    page.title = "Organizador Inteligente"
    page.window_width = 1000
    page.window_height = 700
    page.window_min_width = 800
    page.window_min_height = 600
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 0
    
    def on_login_success():
        """Callback cuando el login es exitoso."""
        page.clean()
        app_ui = AppUI(page)
        app_ui.auth_manager = auth_manager
        app_ui._on_login_success()
        page.update()
    
    # Iniciar con autenticación
    auth_manager = AuthManager(page, on_login_success)
    auth_view = auth_manager.build_auth_view()
    auth_manager.setup_event_handlers()
    
    page.add(
        ft.Container(
            content=auth_view,
            alignment=ft.alignment.center,
            expand=True,
            bgcolor=ft.colors.GREY_100,
            padding=20
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
