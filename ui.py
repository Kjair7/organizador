# organizador_inteligente/ui.py
# -------------------------------------------------------------
# Interfaz de usuario con Flet (versión rediseñada para mayor intuición y atractivo)
# - Diseño moderno con navegación lateral, cards y secciones claras.
# - Explicaciones integradas para guiar al usuario.
# - Funciones simplificadas y modulares para fácil comprensión.
# -------------------------------------------------------------

import flet as ft
from pathlib import Path
from typing import List, Optional

from config import APP_NOMBRE, ruta_bd, EXCLUSIONES_POR_DEFECTO
from models import ReglaClasificacion
from repositories import RepositorioHistorial
from services import ServicioReglas, ServicioClasificacion, ServicioCarpetas, CoordinadorTareas
from auth import AuthManager

class AppUI:
    """Clase principal para la interfaz de usuario intuitiva y atractiva."""
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = f"{APP_NOMBRE} – Organizador de Archivos"
        self.page.window_width = 1000
        self.page.window_height = 700
        self.page.window_min_width = 900
        self.page.window_min_height = 600
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.colors.INDIGO_600,
                primary_container=ft.colors.INDIGO_100,
                secondary=ft.colors.TEAL_600,
                secondary_container=ft.colors.TEAL_100,
                background=ft.colors.GREY_50,
                surface=ft.colors.WHITE,
            ),
            visual_density=ft.ThemeVisualDensity.COMPACT,
            font_family="Segoe UI",
            use_material3=True,
        )
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

        # Servicios (se inicializarán después del login)
        self.repo = None
        self.servicio_clasif = None
        self.servicio_carpetas = None
        self.servicio_reglas = None
        self.coordinador = CoordinadorTareas()

        # Estado
        self.carpeta_fuente: Optional[Path] = None
        self.carpeta_destino: Optional[Path] = None
        self.reglas: List[ReglaClasificacion] = []
        self._carpetas_vacias_detectadas: List[Path] = []
        self.current_user = None

        # Selectores de archivos
        self.selector_fuente = ft.FilePicker(on_result=self._elegir_fuente)
        self.selector_destino = ft.FilePicker(on_result=self._elegir_destino)
        self.page.overlay.extend([self.selector_fuente, self.selector_destino])

        # Barra de progreso global
        self.barra_progreso = ft.ProgressBar(value=0, color=ft.colors.INDIGO_600, visible=False, height=4)

        # No iniciar con autenticación aquí, se maneja en main.py

    def _on_login_success(self):
        """Callback tras login exitoso: construye UI principal."""
        self.current_user = self.auth_manager.current_user
        
        # Inicializar servicios con el ID del usuario
        user_id = self.current_user['id_usuario']
        self.repo = RepositorioHistorial(user_id)
        self.servicio_clasif = ServicioClasificacion(self.repo)
        self.servicio_carpetas = ServicioCarpetas(self.repo)
        self.servicio_reglas = ServicioReglas(user_id)
        
        # Cargar reglas del usuario
        self.reglas = self.servicio_reglas.cargar()
        
        self.page.clean()
        self._construir_ui_principal()
        self.page.update()

    def _construir_ui_principal(self):
        """Construye el diseño principal con navegación lateral."""
        # Header con información del usuario
        self.header = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.icons.PERSON, color=ft.colors.INDIGO_600, size=20),
                                ft.Text(
                                    f"Bienvenido, {self.current_user['nombre_usuario'] if self.current_user else 'Usuario'}",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.INDIGO_700
                                ),
                            ],
                            spacing=8,
                        ),
                        bgcolor=ft.colors.INDIGO_50,
                        padding=12,
                        border_radius=20,
                    ),
                    ft.Container(expand=True),
                    ft.IconButton(
                        ft.icons.LOGOUT,
                        tooltip="Cerrar sesión",
                        on_click=self._cerrar_sesion,
                        bgcolor=ft.colors.RED_50,
                        icon_color=ft.colors.RED_600,
                        icon_size=20,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=ft.colors.WHITE,
            padding=15,
            border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.GREY_200)),
        )

        # Navegación lateral
        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=80,
            min_extended_width=180,
            extended=True,
            destinations=[
                ft.NavigationRailDestination(icon=ft.icons.HOME, label="Inicio"),
                ft.NavigationRailDestination(icon=ft.icons.SORT, label="Clasificar"),
                ft.NavigationRailDestination(icon=ft.icons.SETTINGS, label="Reglas"),
                ft.NavigationRailDestination(icon=ft.icons.FOLDER_OPEN, label="Carpetas Vacías"),
                ft.NavigationRailDestination(icon=ft.icons.HISTORY, label="Historial"),
                ft.NavigationRailDestination(icon=ft.icons.STAR, label="Premium"),
            ],
            on_change=self._cambiar_seccion,
        )

        # Construir secciones
        self.seccion_inicio = self._build_seccion_inicio()
        self.seccion_clasificar = self._build_seccion_clasificar()
        self.seccion_reglas = self._build_seccion_reglas()
        self.seccion_vacias = self._build_seccion_vacias()
        self.seccion_historial = self._build_seccion_historial()
        self.seccion_premium = self._build_seccion_premium()

        # Contenedor de secciones
        self.contenedor_secciones = ft.Stack(
            [
                self.seccion_inicio,
                self.seccion_clasificar,
                self.seccion_reglas,
                self.seccion_vacias,
                self.seccion_historial,
                self.seccion_premium,
            ],
            expand=True
        )

        # Mostrar solo la primera sección
        self._mostrar_seccion(0)

        # Layout principal
        layout = ft.Column(
            [
                self.header,
                self.barra_progreso,
                ft.Row(
                    [
                        self.rail,
                        ft.VerticalDivider(width=1),
                        self.contenedor_secciones,
                    ],
                    expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            expand=True,
            spacing=0,
        )
        self.page.add(layout)

    def _cambiar_seccion(self, e):
        """Cambia la sección visible."""
        index = e.control.selected_index
        self._mostrar_seccion(index)

    def _mostrar_seccion(self, index: int):
        """Muestra solo la sección seleccionada."""
        for i, seccion in enumerate(self.contenedor_secciones.controls):
            seccion.visible = (i == index)
        self.page.update()

    # ----- Secciones -----
    def _build_seccion_inicio(self) -> ft.Container:
        """Sección de bienvenida."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.icons.FOLDER_SPECIAL, size=80, color=ft.colors.INDIGO_600),
                                ft.Text("Organizador Inteligente", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_700),
                                ft.Text("Organiza tus archivos de forma profesional y automática", size=18, color=ft.colors.GREY_600),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                        ),
                        alignment=ft.alignment.center,
                        padding=30,
                    ),
                    ft.Container(height=20),
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Icon(ft.icons.SORT, size=32, color=ft.colors.TEAL_600),
                                        ft.Text("Clasificación Inteligente", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text("Organiza archivos por tipo, tamaño, fecha o reglas personalizadas", size=12, text_align=ft.TextAlign.CENTER),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=8,
                                ),
                                bgcolor=ft.colors.TEAL_50,
                                padding=20,
                                border_radius=12,
                                width=200,
                                height=140,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Icon(ft.icons.FOLDER_OPEN, size=32, color=ft.colors.ORANGE_600),
                                        ft.Text("Carpetas Vacías", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text("Encuentra y elimina carpetas sin contenido automáticamente", size=12, text_align=ft.TextAlign.CENTER),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=8,
                                ),
                                bgcolor=ft.colors.ORANGE_50,
                                padding=20,
                                border_radius=12,
                                width=200,
                                height=140,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Icon(ft.icons.HISTORY, size=32, color=ft.colors.PURPLE_600),
                                        ft.Text("Historial Completo", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text("Revisa y restaura cualquier acción realizada anteriormente", size=12, text_align=ft.TextAlign.CENTER),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=8,
                                ),
                                bgcolor=ft.colors.PURPLE_50,
                                padding=20,
                                border_radius=12,
                                width=200,
                                height=140,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=15,
                    ),
                    ft.Container(height=25),
                    ft.ElevatedButton(
                        "Comenzar a Organizar",
                        icon=ft.icons.ARROW_FORWARD,
                        bgcolor=ft.colors.INDIGO_600,
                        color=ft.colors.WHITE,
                        style=ft.ButtonStyle(
                            padding=20,
                            shape=ft.RoundedRectangleBorder(radius=12),
                        ),
                        on_click=lambda e: self._mostrar_seccion(1),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=25,
            bgcolor=ft.colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.BLACK12),
            margin=15,
            expand=True,
            visible=False,
        )

    def _build_seccion_clasificar(self) -> ft.Container:
        """Sección de clasificación."""
        self.txt_fuente = ft.TextField(
            label="Carpeta Fuente", 
            read_only=True, 
            expand=True, 
            border_radius=12,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            prefix_icon=ft.icons.FOLDER,
        )
        self.txt_destino = ft.TextField(
            label="Carpeta Destino (Opcional)", 
            read_only=True, 
            expand=True, 
            border_radius=12,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            prefix_icon=ft.icons.FOLDER_SPECIAL,
        )
        self.btn_clasificar_basico = ft.ElevatedButton(
            "Clasificación Básica",
            icon=ft.icons.SORT,
            bgcolor=ft.colors.INDIGO_600,
            color=ft.colors.WHITE,
            style=ft.ButtonStyle(
                padding=15,
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
            on_click=self._accion_clasificar_basico
        )
        self.btn_clasificar_avanzado = ft.ElevatedButton(
            "Clasificación Avanzada",
            icon=ft.icons.SETTINGS,
            bgcolor=ft.colors.TEAL_600,
            color=ft.colors.WHITE,
            style=ft.ButtonStyle(
                padding=15,
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
            on_click=self._accion_clasificar_avanzado
        )
        
        # Crear txt_estado primero
        self.txt_estado = ft.Text("Listo para organizar archivos", italic=True, color=ft.colors.GREY_700, size=14)
        
        card_seleccion = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.icons.FOLDER_OPEN, color=ft.colors.INDIGO_600, size=28),
                                ft.Text("Seleccionar Carpetas", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_700),
                            ],
                            spacing=10,
                        ),
                        ft.Text("Elige dónde están tus archivos y dónde organizarlos", size=14, color=ft.colors.GREY_600),
                        ft.Container(height=20),
                        ft.Row([
                            self.txt_fuente, 
                            ft.IconButton(
                                ft.icons.FOLDER_OPEN, 
                                on_click=lambda e: self.selector_fuente.get_directory_path(),
                                tooltip="Seleccionar carpeta fuente",
                                bgcolor=ft.colors.INDIGO_50,
                                icon_color=ft.colors.INDIGO_600,
                            )
                        ], spacing=10),
                        ft.Row([
                            self.txt_destino, 
                            ft.IconButton(
                                ft.icons.FOLDER_SPECIAL, 
                                on_click=lambda e: self.selector_destino.get_directory_path(),
                                tooltip="Seleccionar carpeta destino",
                                bgcolor=ft.colors.TEAL_50,
                                icon_color=ft.colors.TEAL_600,
                            )
                        ], spacing=10),
                    ],
                    spacing=15,
                ),
                padding=25,
            ),
            elevation=6,
            margin=10,
        )
        
        card_acciones = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.icons.SORT, color=ft.colors.TEAL_600, size=28),
                                ft.Text("Clasificar Archivos", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.TEAL_700),
                            ],
                            spacing=10,
                        ),
                        ft.Text("Organiza por tipo o con reglas personalizadas", size=14, color=ft.colors.GREY_600),
                        ft.Container(height=20),
                        ft.Row(
                            [
                                self.btn_clasificar_basico,
                                self.btn_clasificar_avanzado,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
                        ),
                        ft.Container(height=15),
                        self.txt_estado
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=25,
            ),
            elevation=6,
            margin=10,
        )
        
        return ft.Container(
            content=ft.Column([card_seleccion, card_acciones], spacing=15),
            padding=25,
            expand=True,
            visible=False,
        )

    def _build_seccion_reglas(self) -> ft.Container:
        """Sección de reglas personalizadas."""
        self.tabla_reglas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Destino", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Extensiones", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tamaño Mín (KB)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tamaño Máx (KB)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Desde", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Hasta", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=12,
            heading_row_color=ft.colors.INDIGO_50,
        )
        self._refrescar_tabla_reglas()
        
        card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.icons.RULE, color=ft.colors.INDIGO_600, size=28),
                                ft.Text("Reglas Personalizadas", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_700),
                            ],
                            spacing=10,
                        ),
                        ft.Text("Define cómo clasificar tus archivos automáticamente con reglas avanzadas", size=14, color=ft.colors.GREY_600),
                        ft.Container(height=20),
                        ft.Container(
                            content=self.tabla_reglas, 
                            height=350, 
                            padding=15,
                            bgcolor=ft.colors.WHITE,
                            border_radius=8,
                        ),
                        ft.Container(height=15),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Nueva Regla", 
                                    icon=ft.icons.ADD_CIRCLE,
                                    bgcolor=ft.colors.GREEN_600,
                                    color=ft.colors.WHITE,
                                    style=ft.ButtonStyle(
                                        padding=15,
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                    on_click=self._agregar_regla
                                ),
                                ft.ElevatedButton(
                                    "Guardar Reglas", 
                                    icon=ft.icons.SAVE,
                                    bgcolor=ft.colors.INDIGO_600,
                                    color=ft.colors.WHITE,
                                    style=ft.ButtonStyle(
                                        padding=15,
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                    on_click=self._guardar_reglas
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=15,
                        ),
                    ],
                    spacing=15,
                ),
                padding=25,
            ),
            elevation=6,
            margin=10,
        )
        return ft.Container(content=card, padding=25, expand=True, visible=False)

    def _build_seccion_vacias(self) -> ft.Container:
        """Sección de carpetas vacías."""
        self.txt_exclusiones = ft.TextField(
            label="Excluir Carpetas (separadas por coma)",
            value=", ".join(EXCLUSIONES_POR_DEFECTO),
            expand=True,
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            prefix_icon=ft.icons.BLOCK,
            hint_text="Ej: .git, node_modules, __pycache__"
        )
        self.lista_vacias = ft.ListView(expand=True, spacing=5)
        self.btn_detectar_vacias = ft.ElevatedButton(
            "Detectar Carpetas Vacías",
            icon=ft.icons.SEARCH,
            bgcolor=ft.colors.INDIGO_600,
            color=ft.colors.WHITE,
            style=ft.ButtonStyle(
                padding=15,
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            on_click=self._accion_detectar_vacias
        )
        self.btn_eliminar_vacias = ft.ElevatedButton(
            "Eliminar Seleccionadas",
            icon=ft.icons.DELETE_FOREVER,
            bgcolor=ft.colors.RED_600,
            color=ft.colors.WHITE,
            style=ft.ButtonStyle(
                padding=15,
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            on_click=self._accion_eliminar_vacias,
            disabled=True
        )
        
        card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.icons.FOLDER_OPEN, color=ft.colors.ORANGE_600, size=28),
                                ft.Text("Carpetas Vacías", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.ORANGE_700),
                            ],
                            spacing=10,
                        ),
                        ft.Text("Encuentra y elimina carpetas sin contenido para liberar espacio", size=14, color=ft.colors.GREY_600),
                        ft.Container(height=20),
                        ft.Text("Configuración de Exclusión:", size=16, weight=ft.FontWeight.BOLD),
                        self.txt_exclusiones,
                        ft.Container(height=20),
                        ft.Row(
                            [
                                self.btn_detectar_vacias,
                                self.btn_eliminar_vacias,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
                        ),
                        ft.Container(height=15),
                        ft.Text("Carpetas Vacías Encontradas:", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=self.lista_vacias,
                            height=200,
                            padding=10,
                            bgcolor=ft.colors.GREY_50,
                            border_radius=8,
                        ),
                    ],
                    spacing=15,
                ),
                padding=25,
            ),
            elevation=6,
            margin=10,
        )
        return ft.Container(content=card, padding=25, expand=True, visible=False)

    def _build_seccion_historial(self) -> ft.Container:
        """Sección de historial."""
        self.lista_historial = ft.ListView(expand=True, spacing=10)
        self._cargar_historial()
        
        card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.icons.HISTORY, color=ft.colors.PURPLE_600, size=28),
                                ft.Text("Historial de Acciones", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.PURPLE_700),
                            ],
                            spacing=10,
                        ),
                        ft.Text("Revisa y restaura acciones realizadas anteriormente", size=14, color=ft.colors.GREY_600),
                        ft.Container(height=20),
                        ft.Container(
                            content=self.lista_historial,
                            height=400,
                            padding=15,
                            bgcolor=ft.colors.GREY_50,
                            border_radius=8,
                        ),
                        ft.Container(height=15),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Actualizar Historial",
                                    icon=ft.icons.REFRESH,
                                    bgcolor=ft.colors.INDIGO_600,
                                    color=ft.colors.WHITE,
                                    style=ft.ButtonStyle(
                                        padding=15,
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                    on_click=lambda e: self._cargar_historial()
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=15,
                ),
                padding=25,
            ),
            elevation=6,
            margin=10,
        )
        return ft.Container(content=card, padding=25, expand=True, visible=False)

    # ----- Funciones de la interfaz -----
    def _elegir_fuente(self, e: ft.FilePickerResultEvent):
        """Maneja selección de carpeta fuente."""
        if e.path:
            self.carpeta_fuente = Path(e.path)
            self.txt_fuente.value = str(self.carpeta_fuente)
            self.page.update()

    def _elegir_destino(self, e: ft.FilePickerResultEvent):
        """Maneja selección de carpeta destino."""
        if e.path:
            self.carpeta_destino = Path(e.path)
            self.txt_destino.value = str(self.carpeta_destino)
            self.page.update()

    def _anunciar(self, mensaje: str):
        """Muestra mensajes en snackbar."""
        self.txt_estado.value = "Listo"
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text(mensaje), duration=3000))
        self.page.update()

    def _actualizar_progreso(self, valor: float):
        """Actualiza barra de progreso."""
        self.barra_progreso.value = valor
        self.barra_progreso.visible = (valor > 0)
        self.page.update()

    def _congelar_controles(self, congelar: bool):
        """Habilita/deshabilita controles durante operaciones."""
        self.btn_clasificar_basico.disabled = congelar
        self.btn_clasificar_avanzado.disabled = congelar
        self.btn_detectar_vacias.disabled = congelar
        self.btn_eliminar_vacias.disabled = congelar if not self._carpetas_vacias_detectadas else False
        self.page.update()

    def _accion_clasificar_basico(self, e):
        """Clasifica archivos por tipo."""
        if not self.carpeta_fuente:
            self._anunciar("Selecciona una carpeta fuente")
            return
        if self.coordinador.en_ejecucion():
            self._anunciar("Tarea en ejecución, espera a que termine")
            return

        def tarea():
            try:
                self._congelar_controles(True)
                self._actualizar_progreso(0.01)
                detalle = self.servicio_clasif.clasificar_basico(
                    self.carpeta_fuente, self.carpeta_destino, progreso_cb=self._actualizar_progreso
                )
                self._anunciar(f"Clasificación básica completada: {detalle['archivos_movidos']} archivos movidos")
            finally:
                self._congelar_controles(False)
                self._actualizar_progreso(0.0)
                self._cargar_historial()

        self.coordinador.ejecutar(tarea)

    def _accion_clasificar_avanzado(self, e):
        """Clasifica archivos con reglas personalizadas."""
        if not self.carpeta_fuente:
            self._anunciar("Selecciona una carpeta fuente")
            return
        if self.coordinador.en_ejecucion():
            self._anunciar("Tarea en ejecución, espera a que termine")
            return

        def tarea():
            try:
                self._congelar_controles(True)
                self._actualizar_progreso(0.01)
                detalle = self.servicio_clasif.clasificar_avanzado(
                    self.carpeta_fuente, self.reglas, self.carpeta_destino, progreso_cb=self._actualizar_progreso
                )
                self._anunciar(f"Clasificación avanzada completada: {detalle['archivos_movidos']} archivos movidos")
            finally:
                self._congelar_controles(False)
                self._actualizar_progreso(0.0)
                self._cargar_historial()

        self.coordinador.ejecutar(tarea)

    def _accion_detectar_vacias(self, e):
        """Detecta carpetas vacías."""
        if not self.carpeta_fuente:
            self._anunciar("Selecciona una carpeta fuente primero")
            return
        
        exclusiones = [x.strip() for x in self.txt_exclusiones.value.split(",") if x.strip()]
        self._carpetas_vacias_detectadas = self.servicio_carpetas.detectar_vacias(self.carpeta_fuente, exclusiones)
        
        # Crear lista con checkboxes para selección
        self.lista_vacias.controls = []
        for i, carpeta in enumerate(self._carpetas_vacias_detectadas):
            checkbox = ft.Checkbox(
                value=True,  # Seleccionado por defecto
                on_change=lambda e, idx=i: self._toggle_carpeta_seleccion(idx, e.control.value)
            )
            self.lista_vacias.controls.append(
                ft.ListTile(
                    leading=checkbox,
                    title=ft.Text(str(carpeta), size=12),
                    subtitle=ft.Text(f"Ruta: {carpeta.parent}", size=10, color=ft.colors.GREY_600),
                    trailing=ft.Icon(ft.icons.FOLDER_OPEN, color=ft.colors.ORANGE_600, size=20),
                )
            )
        
        self.btn_eliminar_vacias.disabled = len(self._carpetas_vacias_detectadas) == 0
        self._anunciar(f"Detectadas {len(self._carpetas_vacias_detectadas)} carpetas vacías")
        self.page.update()

    def _accion_eliminar_vacias(self, e):
        """Elimina carpetas vacías seleccionadas."""
        if not self._carpetas_vacias_detectadas:
            self._anunciar("No hay carpetas vacías para eliminar")
            return
        if self.coordinador.en_ejecucion():
            self._anunciar("Tarea en ejecución, espera a que termine")
            return

        # Obtener carpetas seleccionadas
        carpetas_seleccionadas = []
        for i, control in enumerate(self.lista_vacias.controls):
            if hasattr(control, 'leading') and hasattr(control.leading, 'value') and control.leading.value:
                carpetas_seleccionadas.append(self._carpetas_vacias_detectadas[i])

        if not carpetas_seleccionadas:
            self._anunciar("Selecciona al menos una carpeta para eliminar")
            return

        def tarea():
            try:
                self._congelar_controles(True)
                self._actualizar_progreso(0.01)
                eliminadas = self.servicio_carpetas.eliminar_vacias(
                    carpetas_seleccionadas, progreso_cb=self._actualizar_progreso
                )
                self._anunciar(f"Eliminadas {len(eliminadas)} carpetas vacías")
                
                # Actualizar la lista removiendo las eliminadas
                carpetas_restantes = [c for c in self._carpetas_vacias_detectadas if c not in eliminadas]
                self._carpetas_vacias_detectadas = carpetas_restantes
                
                if carpetas_restantes:
                    # Recrear la lista con las carpetas restantes
                    self.lista_vacias.controls = []
                    for i, carpeta in enumerate(carpetas_restantes):
                        checkbox = ft.Checkbox(
                            value=True,
                            on_change=lambda e, idx=i: self._toggle_carpeta_seleccion(idx, e.control.value)
                        )
                        self.lista_vacias.controls.append(
                            ft.ListTile(
                                leading=checkbox,
                                title=ft.Text(str(carpeta), size=12),
                                subtitle=ft.Text(f"Ruta: {carpeta.parent}", size=10, color=ft.colors.GREY_600),
                                trailing=ft.Icon(ft.icons.FOLDER_OPEN, color=ft.colors.ORANGE_600, size=20),
                            )
                        )
                else:
                    self.lista_vacias.controls.clear()
                    self.btn_eliminar_vacias.disabled = True
                    
            finally:
                self._congelar_controles(False)
                self._actualizar_progreso(0.0)
                self._cargar_historial()
                self.page.update()

        self.coordinador.ejecutar(tarea)

    def _refrescar_tabla_reglas(self):
        """Actualiza la tabla de reglas."""
        self.tabla_reglas.rows.clear()
        for i, regla in enumerate(self.reglas):
            self.tabla_reglas.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(regla.nombre)),
                        ft.DataCell(ft.Text(regla.destino_subcarpeta)),
                        ft.DataCell(ft.Text(", ".join(regla.extensiones))),
                        ft.DataCell(ft.Text(str(regla.tam_min_kb or ""))),
                        ft.DataCell(ft.Text(str(regla.tam_max_kb or ""))),
                        ft.DataCell(ft.Text(regla.fecha_desde or "")),
                        ft.DataCell(ft.Text(regla.fecha_hasta or "")),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(ft.icons.EDIT, on_click=lambda e, idx=i: self._editar_regla(idx)),
                                ft.IconButton(ft.icons.DELETE, on_click=lambda e, idx=i: self._eliminar_regla(idx)),
                            ])
                        ),
                    ]
                )
            )

    def _agregar_regla(self, e):
        """Abre diálogo para agregar nueva regla."""
        nombre = ft.TextField(
            label="Nombre de la regla", 
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            prefix_icon=ft.icons.TITLE,
            hint_text="Ej: Documentos PDF grandes"
        )
        destino = ft.TextField(
            label="Subcarpeta Destino", 
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            prefix_icon=ft.icons.FOLDER,
            hint_text="Ej: Documentos_PDF"
        )
        extensiones = ft.TextField(
            label="Extensiones (separadas por coma)", 
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            prefix_icon=ft.icons.EXTENSION,
            hint_text="Ej: pdf, doc, docx"
        )
        tam_min = ft.TextField(
            label="Tamaño Mínimo (KB)", 
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]"), 
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            prefix_icon=ft.icons.SIZE_SMALL,
            hint_text="Opcional"
        )
        tam_max = ft.TextField(
            label="Tamaño Máximo (KB)", 
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]"), 
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            prefix_icon=ft.icons.SIZE_LARGE,
            hint_text="Opcional"
        )
        fecha_desde = ft.TextField(
            label="Desde (YYYY-MM-DD)", 
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            prefix_icon=ft.icons.CALENDAR_TODAY,
            hint_text="Opcional"
        )
        fecha_hasta = ft.TextField(
            label="Hasta (YYYY-MM-DD)", 
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            prefix_icon=ft.icons.CALENDAR_TODAY,
            hint_text="Opcional"
        )

        def guardar(e):
            if not nombre.value.strip():
                self.page.show_snack_bar(ft.SnackBar(
                    content=ft.Text("El nombre de la regla es obligatorio"),
                    bgcolor=ft.colors.RED
                ))
                return
                
            if not destino.value.strip():
                self.page.show_snack_bar(ft.SnackBar(
                    content=ft.Text("La subcarpeta destino es obligatoria"),
                    bgcolor=ft.colors.RED
                ))
                return
                
            if not extensiones.value.strip():
                self.page.show_snack_bar(ft.SnackBar(
                    content=ft.Text("Las extensiones son obligatorias"),
                    bgcolor=ft.colors.RED
                ))
                return

            nueva_regla = ReglaClasificacion(
                nombre=nombre.value.strip(),
                destino_subcarpeta=destino.value.strip(),
                extensiones=[ext.strip() for ext in extensiones.value.split(",") if ext.strip()],
                tam_min_kb=int(tam_min.value) if tam_min.value else None,
                tam_max_kb=int(tam_max.value) if tam_max.value else None,
                fecha_desde=fecha_desde.value.strip() or None,
                fecha_hasta=fecha_hasta.value.strip() or None,
            )
            self.reglas.append(nueva_regla)
            self._refrescar_tabla_reglas()
            self.page.dialog.open = False
            self.page.update()
            
            # Registrar en historial
            if self.repo:
                self.repo.registrar("clasificacion", {
                    "accion": "agregar_regla",
                    "nombre_regla": nueva_regla.nombre,
                    "extensiones": nueva_regla.extensiones
                })

        dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.icons.ADD_CIRCLE, color=ft.colors.GREEN_600),
                    ft.Text("Nueva Regla de Clasificación", size=18, weight=ft.FontWeight.BOLD)
                ],
                spacing=10
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Configura una nueva regla para clasificar archivos automáticamente", size=14, color=ft.colors.GREY_600),
                        ft.Container(height=15),
                        nombre, 
                        destino, 
                        extensiones, 
                        tam_min, 
                        tam_max, 
                        fecha_desde, 
                        fecha_hasta
                    ],
                    spacing=12,
                    tight=True
                ),
                width=400,
                padding=10
            ),
            actions=[
                ft.TextButton(
                    "Cancelar", 
                    on_click=lambda e: setattr(self.page.dialog, "open", False),
                    style=ft.ButtonStyle(color=ft.colors.GREY_600)
                ),
                ft.ElevatedButton(
                    "Guardar Regla", 
                    on_click=guardar,
                    bgcolor=ft.colors.GREEN_600,
                    color=ft.colors.WHITE,
                    icon=ft.icons.SAVE
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _editar_regla(self, index: int):
        """Abre diálogo para editar regla existente."""
        regla = self.reglas[index]
        nombre = ft.TextField(label="Nombre", value=regla.nombre, border_radius=8)
        destino = ft.TextField(label="Subcarpeta Destino", value=regla.destino_subcarpeta, border_radius=8)
        extensiones = ft.TextField(label="Extensiones (separadas por coma)", value=", ".join(regla.extensiones), border_radius=8)
        tam_min = ft.TextField(label="Tamaño Mínimo (KB)", value=str(regla.tam_min_kb or ""), input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]"), border_radius=8)
        tam_max = ft.TextField(label="Tamaño Máximo (KB)", value=str(regla.tam_max_kb or ""), input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]"), border_radius=8)
        fecha_desde = ft.TextField(label="Desde (YYYY-MM-DD)", value=regla.fecha_desde or "", border_radius=8)
        fecha_hasta = ft.TextField(label="Hasta (YYYY-MM-DD)", value=regla.fecha_hasta or "", border_radius=8)

        def guardar(e):
            self.reglas[index] = ReglaClasificacion(
                nombre=nombre.value or "Nueva Regla",
                destino_subcarpeta=destino.value or "Destino",
                extensiones=[ext.strip() for ext in extensiones.value.split(",") if ext.strip()],
                tam_min_kb=int(tam_min.value) if tam_min.value else None,
                tam_max_kb=int(tam_max.value) if tam_max.value else None,
                fecha_desde=fecha_desde.value or None,
                fecha_hasta=fecha_hasta.value or None,
            )
            self._refrescar_tabla_reglas()
            self.page.dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Editar Regla"),
            content=ft.Column(
                [nombre, destino, extensiones, tam_min, tam_max, fecha_desde, fecha_hasta],
                spacing=10,
                tight=True
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(self.page.dialog, "open", False)),
                ft.ElevatedButton("Guardar", on_click=guardar),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _eliminar_regla(self, index: int):
        """Elimina una regla."""
        self.reglas.pop(index)
        self._refrescar_tabla_reglas()
        self.page.update()

    def _guardar_reglas(self, e):
        """Guarda todas las reglas."""
        self.servicio_reglas.guardar(self.reglas)
        self._anunciar("Reglas guardadas correctamente")

    def _cargar_historial(self):
        """Carga el historial de acciones."""
        if not self.repo:
            return
            
        self.lista_historial.controls.clear()
        historial = self.repo.listar()
        
        if not historial:
            self.lista_historial.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.icons.HISTORY, size=50, color=ft.colors.GREY_400),
                            ft.Text("No hay historial disponible", size=16, color=ft.colors.GREY_600),
                            ft.Text("Las acciones realizadas aparecerán aquí", size=14, color=ft.colors.GREY_500),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    alignment=ft.alignment.center,
                    padding=50,
                )
            )
        else:
            for item in historial:
                detalle = item['detalle']
                
                # Determinar el icono según el tipo de acción
                if item['tipo'] == "clasificacion":
                    icono = ft.icons.SORT
                    color_icono = ft.colors.TEAL_600
                    if detalle.get('accion') == 'agregar_regla':
                        icono = ft.icons.RULE
                        color_icono = ft.colors.GREEN_600
                        texto_detalle = f"Regla agregada: {detalle.get('nombre_regla', 'N/A')}"
                    else:
                        texto_detalle = f"Archivos movidos: {detalle.get('archivos_movidos', 0)}"
                else:
                    icono = ft.icons.FOLDER_OPEN
                    color_icono = ft.colors.ORANGE_600
                    texto_detalle = f"Carpetas eliminadas: {detalle.get('carpetas_eliminadas', 0)}"
                
                # Determinar si se puede restaurar
                puede_restaurar = bool(item.get("ruta_cuarentena"))
                
                fila = ft.Card(
                    content=ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(icono, color=color_icono, size=24),
                            title=ft.Text(
                                f"{item['tipo'].replace('_', ' ').title()}",
                                size=16,
                                weight=ft.FontWeight.BOLD
                            ),
                            subtitle=ft.Column(
                                [
                                    ft.Text(f"Fecha: {item['fecha']}", size=12, color=ft.colors.GREY_600),
                                    ft.Text(texto_detalle, size=12, color=ft.colors.GREY_700),
                                ],
                                spacing=2,
                            ),
                            trailing=ft.ElevatedButton(
                                "Restaurar",
                                icon=ft.icons.UNDO,
                                bgcolor=ft.colors.GREEN_600 if puede_restaurar else ft.colors.GREY_400,
                                color=ft.colors.WHITE,
                                style=ft.ButtonStyle(
                                    padding=10,
                                    shape=ft.RoundedRectangleBorder(radius=6),
                                ),
                                disabled=not puede_restaurar,
                                on_click=lambda e, r=item.get("ruta_cuarentena"): self._restaurar_desde_historial(r),
                            ),
                        ),
                        padding=10,
                    ),
                    elevation=2,
                    margin=ft.Margin(0, 5, 0, 5),
                )
                self.lista_historial.controls.append(fila)
        
        self.page.update()

    def _restaurar_desde_historial(self, ruta_cuarentena: Optional[str]):
        """Restaura una carpeta desde el historial."""
        if not ruta_cuarentena:
            self._anunciar("No hay carpeta para restaurar")
            return
            
        p = Path(ruta_cuarentena)
        if not p.exists():
            self._anunciar("No se encontró la carpeta en cuarentena")
            return
            
        if not self.carpeta_fuente:
            self._anunciar("Selecciona una carpeta fuente para restaurar")
            return

        # Mostrar diálogo de confirmación
        def confirmar_restauracion(e):
            self.page.dialog.open = False
            self.page.update()
            
            # Ejecutar restauración
            try:
                ok = self.servicio_carpetas.restaurar(p, self.carpeta_fuente)
                if ok:
                    self._anunciar("✅ Carpeta restaurada exitosamente")
                    # Registrar la restauración en el historial
                    if self.repo:
                        self.repo.registrar("clasificacion", {
                            "accion": "restaurar_carpeta",
                            "ruta_restaurada": str(p),
                            "destino": str(self.carpeta_fuente)
                        })
                else:
                    self._anunciar("❌ Error al restaurar la carpeta")
            except Exception as ex:
                self._anunciar(f"❌ Error al restaurar: {str(ex)}")
            
            self._cargar_historial()

        dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.icons.UNDO, color=ft.colors.GREEN_600),
                    ft.Text("Confirmar Restauración", size=18, weight=ft.FontWeight.BOLD)
                ],
                spacing=10
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("¿Estás seguro de que quieres restaurar esta carpeta?", size=14),
                        ft.Container(height=10),
                        ft.Text(f"Carpeta: {p.name}", size=12, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Desde: {p}", size=11, color=ft.colors.GREY_600),
                        ft.Text(f"Hacia: {self.carpeta_fuente}", size=11, color=ft.colors.GREY_600),
                    ],
                    spacing=8,
                    tight=True
                ),
                width=350,
                padding=10
            ),
            actions=[
                ft.TextButton(
                    "Cancelar", 
                    on_click=lambda e: setattr(self.page.dialog, "open", False),
                    style=ft.ButtonStyle(color=ft.colors.GREY_600)
                ),
                ft.ElevatedButton(
                    "Restaurar", 
                    on_click=confirmar_restauracion,
                    bgcolor=ft.colors.GREEN_600,
                    color=ft.colors.WHITE,
                    icon=ft.icons.UNDO
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _toggle_carpeta_seleccion(self, index: int, selected: bool):
        """Maneja la selección/deselección de carpetas vacías."""
        # Aquí podrías implementar lógica adicional si necesitas
        # Por ahora solo actualizamos la interfaz
        self.page.update()

    def _build_seccion_premium(self) -> ft.Container:
        """Sección de versión premium."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.icons.STAR, size=80, color=ft.colors.AMBER_600),
                                ft.Text("Versión Premium", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_700),
                                ft.Text("Funciones avanzadas próximamente", size=18, color=ft.colors.GREY_600),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                        ),
                        alignment=ft.alignment.center,
                        padding=30,
                    ),
                    ft.Container(height=30),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.icons.CONSTRUCTION, size=60, color=ft.colors.ORANGE_600),
                                ft.Text("En Desarrollo", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.ORANGE_700),
                                ft.Text("Estamos trabajando en funciones más avanzadas para mejorar tu experiencia de organización de archivos.", size=16, text_align=ft.TextAlign.CENTER),
                                ft.Container(height=20),
                                ft.Text("Funciones que vendrán:", size=18, weight=ft.FontWeight.BOLD),
                                ft.ListView(
                                    [
                                        ft.ListTile(leading=ft.Icon(ft.icons.CLOUD_UPLOAD), title=ft.Text("Sincronización en la nube")),
                                        ft.ListTile(leading=ft.Icon(ft.icons.SMART_TOY), title=ft.Text("IA para clasificación automática")),
                                        ft.ListTile(leading=ft.Icon(ft.icons.ANALYTICS), title=ft.Text("Análisis de uso de archivos")),
                                        ft.ListTile(leading=ft.Icon(ft.icons.SCHEDULE), title=ft.Text("Organización programada")),
                                        ft.ListTile(leading=ft.Icon(ft.icons.SECURITY), title=ft.Text("Encriptación de archivos")),
                                    ],
                                    spacing=5,
                                    height=250,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                        ),
                        bgcolor=ft.colors.AMBER_50,
                        padding=30,
                        border_radius=15,
                        width=500,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=25,
            bgcolor=ft.colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.BLACK12),
            margin=15,
            expand=True,
            visible=False,
        )

    def _cerrar_sesion(self, e):
        """Cierra la sesión y regresa a la pantalla de login."""
        self.page.clean()
        self.auth_manager = AuthManager(self.page, self._on_login_success)
        self.page.add(self.auth_manager.build_auth_view())
        self.page.update()
