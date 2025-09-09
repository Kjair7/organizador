# organizador_inteligente/auth.py
# -------------------------------------------------------------
# Módulo de autenticación con pantallas de login y registro
# -------------------------------------------------------------

import flet as ft
from pathlib import Path
import json
import hashlib
import re
from database import db_manager

class AuthManager:
    """Clase para manejar autenticación y pantallas de login/registro."""
    def __init__(self, page: ft.Page, on_login_success):
        self.page = page
        self.on_login_success = on_login_success
        self.current_view = None
        self.is_login_view = True
        self.is_recovery_view = False
        self.current_user = None
        
        # Conectar a la base de datos
        if not db_manager.connect():
            self.page.show_snack_bar(ft.SnackBar(
                content=ft.Text("Error al conectar con la base de datos"),
                bgcolor=ft.colors.RED
            ))

    def _hash_password(self, password: str) -> str:
        """Encripta la contraseña usando hashlib."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _validate_email(self, email: str) -> bool:
        """Valida el formato del correo electrónico."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _validate_cedula(self, cedula: str) -> bool:
        """Valida que la cédula contenga solo dígitos y tenga una longitud razonable."""
        return cedula.isdigit() and 7 <= len(cedula) <= 12

    def _check_password_strength(self, password: str) -> str:
        """Evalúa la fuerza de la contraseña."""
        if len(password) < 8:
            return "Débil"
        if re.search(r"[A-Z]", password) and re.search(r"[0-9]", password) and re.search(r"[^A-Za-z0-9]", password):
            return "Fuerte"
        if re.search(r"[A-Z]", password) or re.search(r"[0-9]", password):
            return "Medio"
        return "Débil"

    def build_auth_view(self):
        """Construye la vista de autenticación (login/registro)."""
        # Campos comunes
        self.email_field = ft.TextField(
            label="Correo electrónico",
            prefix_icon=ft.icons.EMAIL,
            border_radius=8,
            width=280,
            height=45,
            text_size=13,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            border_color=ft.colors.GREY_300,
            focused_border_color=ft.colors.INDIGO_600,
        )
        
        self.password_field = ft.TextField(
            label="Contraseña",
            prefix_icon=ft.icons.LOCK,
            border_radius=8,
            password=True,
            can_reveal_password=True,
            width=280,
            height=45,
            text_size=13,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            border_color=ft.colors.GREY_300,
            focused_border_color=ft.colors.INDIGO_600,
        )

        # Campos específicos de registro
        self.username_field = ft.TextField(
            label="Nombre de usuario",
            prefix_icon=ft.icons.PERSON,
            border_radius=8,
            width=280,
            height=45,
            text_size=13,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            border_color=ft.colors.GREY_300,
            focused_border_color=ft.colors.INDIGO_600,
            visible=False
        )
        
        self.cedula_field = ft.TextField(
            label="Cédula",
            prefix_icon=ft.icons.BADGE,
            border_radius=8,
            width=280,
            height=45,
            text_size=13,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            border_color=ft.colors.GREY_300,
            focused_border_color=ft.colors.INDIGO_600,
            visible=False
        )
        
        self.confirm_password_field = ft.TextField(
            label="Confirmar contraseña",
            prefix_icon=ft.icons.LOCK,
            border_radius=8,
            password=True,
            can_reveal_password=True,
            width=280,
            height=45,
            text_size=13,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            border_color=ft.colors.GREY_300,
            focused_border_color=ft.colors.INDIGO_600,
            visible=False
        )

        # Campos para recuperación de contraseña
        self.recovery_email_field = ft.TextField(
            label="Correo electrónico",
            prefix_icon=ft.icons.EMAIL,
            border_radius=8,
            width=280,
            height=45,
            text_size=13,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            border_color=ft.colors.GREY_300,
            focused_border_color=ft.colors.INDIGO_600,
            visible=False
        )
        
        self.recovery_cedula_field = ft.TextField(
            label="Cédula",
            prefix_icon=ft.icons.BADGE,
            border_radius=8,
            width=280,
            height=45,
            text_size=13,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            border_color=ft.colors.GREY_300,
            focused_border_color=ft.colors.INDIGO_600,
            visible=False
        )
        
        self.recovery_new_password_field = ft.TextField(
            label="Nueva contraseña",
            prefix_icon=ft.icons.LOCK,
            border_radius=8,
            password=True,
            can_reveal_password=True,
            width=280,
            height=45,
            text_size=13,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            border_color=ft.colors.GREY_300,
            focused_border_color=ft.colors.INDIGO_600,
            visible=False
        )
        
        self.recovery_confirm_password_field = ft.TextField(
            label="Confirmar nueva contraseña",
            prefix_icon=ft.icons.LOCK,
            border_radius=8,
            password=True,
            can_reveal_password=True,
            width=280,
            height=45,
            text_size=13,
            filled=True,
            bgcolor=ft.colors.GREY_50,
            border_color=ft.colors.GREY_300,
            focused_border_color=ft.colors.INDIGO_600,
            visible=False
        )

        # Indicadores y mensajes
        self.strength_indicator = ft.Text("", size=11, color=ft.colors.GREY_600, visible=False)
        self.message_text = ft.Text("", size=13, text_align=ft.TextAlign.CENTER)

        # Botones
        self.action_button = ft.ElevatedButton(
            "Iniciar sesión",
            icon=ft.icons.LOGIN,
            on_click=self._handle_auth_action,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.INDIGO_600,
                color=ft.colors.WHITE,
                padding=15,
                shape=ft.RoundedRectangleBorder(radius=8),
                elevation=2,
            ),
            width=200,
            height=40,
        )
        
        self.switch_button = ft.TextButton(
            "¿No tienes cuenta? Regístrate aquí",
            on_click=self._switch_view,
            style=ft.ButtonStyle(
                padding=8,
                color=ft.colors.INDIGO_600,
            ),
        )

        # Botón de recuperación de contraseña
        self.recovery_button = ft.TextButton(
            "¿Olvidaste tu contraseña?",
            on_click=self._show_recovery,
            style=ft.ButtonStyle(
                padding=8,
                color=ft.colors.ORANGE_600,
            ),
        )

        # Botón de regresar (solo visible en registro)
        self.back_button = ft.IconButton(
            ft.icons.ARROW_BACK,
            tooltip="Regresar al login",
            on_click=self._switch_view,
            bgcolor=ft.colors.GREY_100,
            icon_color=ft.colors.GREY_600,
            visible=False,
        )

        # Construir la vista
        self.current_view = ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=20),
                    ft.Row(
                        [
                            self.back_button,
                            ft.Container(expand=True),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Icon(ft.icons.FOLDER_SPECIAL, size=50, color=ft.colors.INDIGO_600),
                        bgcolor=ft.colors.INDIGO_50,
                        border_radius=40,
                        padding=15,
                    ),
                    ft.Container(height=15),
                    ft.Text("Organizador Inteligente", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_700),
                    ft.Text("Gestión profesional de archivos", size=14, color=ft.colors.GREY_600),
                    ft.Container(height=25),
                    
                    self.username_field,
                    self.cedula_field,
                    self.email_field,
                    self.password_field,
                    self.confirm_password_field,
                    self.strength_indicator,
                    
                    # Campos de recuperación
                    self.recovery_email_field,
                    self.recovery_cedula_field,
                    self.recovery_new_password_field,
                    self.recovery_confirm_password_field,
                    
                    ft.Container(height=20),
                    self.action_button,
                    ft.Container(height=10),
                    self.switch_button,
                    self.recovery_button,
                    ft.Container(height=15),
                    self.message_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
            alignment=ft.alignment.center,
            padding=30,
            width=380,
            bgcolor=ft.colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.colors.BLACK12),
        )
        
        return self.current_view

    def _handle_auth_action(self, e):
        """Maneja la acción de login, registro o recuperación."""
        if self.is_recovery_view:
            self._recover_password()
        elif self.is_login_view:
            self._login()
        else:
            self._register()

    def _login(self):
        """Maneja el inicio de sesión."""
        email = self.email_field.value.strip()
        password = self.password_field.value.strip()

        if not self._validate_email(email):
            self.message_text.value = "❌ Correo electrónico inválido"
            self.message_text.color = ft.colors.RED
            self.page.update()
            return
        
        if not password:
            self.message_text.value = "❌ La contraseña es requerida"
            self.message_text.color = ft.colors.RED
            self.page.update()
            return

        # Autenticar con la base de datos
        user = db_manager.authenticate_user(email, password)
        if user:
            self.message_text.value = "✅ Inicio de sesión exitoso"
            self.message_text.color = ft.colors.GREEN
            self.page.update()
            
            # Pequeña pausa para mostrar el mensaje de éxito
            import time
            time.sleep(1)
            
            self.current_user = user
            self.page.clean()
            self.on_login_success()
        else:
            self.message_text.value = "❌ Credenciales incorrectas"
            self.message_text.color = ft.colors.RED
            self.page.update()

    def _register(self):
        """Maneja el registro de un nuevo usuario."""
        email = self.email_field.value.strip()
        password = self.password_field.value.strip()
        confirm_password = self.confirm_password_field.value.strip()
        username = self.username_field.value.strip()
        cedula = self.cedula_field.value.strip()

        # Validaciones
        if not all([username, email, cedula, password, confirm_password]):
            self.message_text.value = "❌ Todos los campos son obligatorios"
            self.message_text.color = ft.colors.RED
            self.page.update()
            return
        
        if not self._validate_email(email):
            self.message_text.value = "❌ Formato de correo inválido"
            self.message_text.color = ft.colors.RED
            self.page.update()
            return
        
        if not self._validate_cedula(cedula):
            self.message_text.value = "❌ Cédula inválida (solo números, 7-12 dígitos)"
            self.message_text.color = ft.colors.RED
            self.page.update()
            return
        
        if len(password) < 8:
            self.message_text.value = "❌ La contraseña debe tener al menos 8 caracteres"
            self.message_text.color = ft.colors.RED
            self.page.update()
            return
        
        if password != confirm_password:
            self.message_text.value = "❌ Las contraseñas no coinciden"
            self.message_text.color = ft.colors.RED
            self.page.update()
            return

        # Verificar si el usuario ya existe
        existing_user = db_manager.get_user_by_email(email)
        if existing_user:
            self.message_text.value = "❌ Este correo ya está registrado"
            self.message_text.color = ft.colors.RED
            self.page.update()
            return

        # Registrar usuario en la base de datos
        if db_manager.create_user(username, cedula, email, password):
            self.message_text.value = "✅ Registro exitoso. Redirigiendo..."
            self.message_text.color = ft.colors.GREEN
            self.page.update()
            
            # Cambiar a vista de login después de registro exitoso
            import time
            time.sleep(1)
            self._switch_view(None)
        else:
            self.message_text.value = "❌ Error al registrar usuario"
            self.message_text.color = ft.colors.RED
            self.page.update()

    def _recover_password(self):
        """Maneja la recuperación de contraseña."""
        email = self.recovery_email_field.value.strip()
        cedula = self.recovery_cedula_field.value.strip()
        new_password = self.recovery_new_password_field.value.strip()
        confirm_password = self.recovery_confirm_password_field.value.strip()

        # Validaciones
        if not all([email, cedula, new_password, confirm_password]):
            self.message_text.value = "❌ Todos los campos son obligatorios"
            self.message_text.color = ft.colors.RED
            self.page.update()
            return
        
        if not self._validate_email(email):
            self.message_text.value = "❌ Formato de correo inválido"
            self.message_text.color = ft.colors.RED
            self.page.update()
            return
        
        if not self._validate_cedula(cedula):
            self.message_text.value = "❌ Cédula inválida (solo números, 7-12 dígitos)"
            self.message_text.color = ft.colors.RED
            self.page.update()
            return
        
        if len(new_password) < 8:
            self.message_text.value = "❌ La nueva contraseña debe tener al menos 8 caracteres"
            self.message_text.color = ft.colors.RED
            self.page.update()
            return
        
        if new_password != confirm_password:
            self.message_text.value = "❌ Las contraseñas no coinciden"
            self.message_text.color = ft.colors.RED
            self.page.update()
            return

        # Verificar que el usuario existe y la cédula coincide
        user = db_manager.get_user_by_email(email)
        if not user:
            self.message_text.value = "❌ No se encontró un usuario con ese correo"
            self.message_text.color = ft.colors.RED
            self.page.update()
            return
        
        if user['cedula'] != cedula:
            self.message_text.value = "❌ La cédula no coincide con el usuario registrado"
            self.message_text.color = ft.colors.RED
            self.page.update()
            return

        # Actualizar contraseña
        hashed_password = self._hash_password(new_password)
        query = "UPDATE Usuarios SET contrasena_hash = %s WHERE id_usuario = %s"
        if db_manager.execute_query(query, (hashed_password, user['id_usuario'])):
            self.message_text.value = "✅ Contraseña actualizada exitosamente. Redirigiendo al login..."
            self.message_text.color = ft.colors.GREEN
            self.page.update()
            
            # Cambiar a vista de login después de recuperación exitosa
            import time
            time.sleep(2)
            self._switch_to_login()
        else:
            self.message_text.value = "❌ Error al actualizar la contraseña"
            self.message_text.color = ft.colors.RED
            self.page.update()

    def _show_recovery(self, e):
        """Muestra la vista de recuperación de contraseña."""
        self.is_recovery_view = True
        self.is_login_view = False
        
        # Configurar botones y campos
        self.action_button.text = "Recuperar Contraseña"
        self.action_button.icon = ft.icons.LOCK_RESET
        self.switch_button.text = "¿Ya tienes cuenta? Inicia sesión aquí"
        self.recovery_button.text = "Volver al login"
        self.recovery_button.on_click = self._switch_to_login
        
        # Ocultar campos de login/registro
        self.username_field.visible = False
        self.cedula_field.visible = False
        self.email_field.visible = False
        self.password_field.visible = False
        self.confirm_password_field.visible = False
        self.strength_indicator.visible = False
        self.back_button.visible = False
        
        # Mostrar campos de recuperación
        self.recovery_email_field.visible = True
        self.recovery_cedula_field.visible = True
        self.recovery_new_password_field.visible = True
        self.recovery_confirm_password_field.visible = True
        
        # Limpiar mensajes
        self.message_text.value = ""
        self.page.update()

    def _switch_to_login(self, e=None):
        """Cambia a la vista de login."""
        self.is_recovery_view = False
        self.is_login_view = True
        
        # Configurar botones y campos
        self.action_button.text = "Iniciar sesión"
        self.action_button.icon = ft.icons.LOGIN
        self.switch_button.text = "¿No tienes cuenta? Regístrate aquí"
        self.recovery_button.text = "¿Olvidaste tu contraseña?"
        self.recovery_button.on_click = self._show_recovery
        
        # Mostrar campos de login
        self.email_field.visible = True
        self.password_field.visible = True
        
        # Ocultar otros campos
        self.username_field.visible = False
        self.cedula_field.visible = False
        self.confirm_password_field.visible = False
        self.strength_indicator.visible = False
        self.back_button.visible = False
        self.recovery_email_field.visible = False
        self.recovery_cedula_field.visible = False
        self.recovery_new_password_field.visible = False
        self.recovery_confirm_password_field.visible = False
        
        # Limpiar mensajes
        self.message_text.value = ""
        self.page.update()

    def _switch_view(self, e):
        """Cambia entre login y registro."""
        if self.is_recovery_view:
            self._switch_to_login()
            return
            
        self.is_login_view = not self.is_login_view
        
        if self.is_login_view:
            # Cambiar a login
            self.action_button.text = "Iniciar sesión"
            self.action_button.icon = ft.icons.LOGIN
            self.switch_button.text = "¿No tienes cuenta? Regístrate aquí"
            
            # Ocultar campos de registro
            self.username_field.visible = False
            self.cedula_field.visible = False
            self.confirm_password_field.visible = False
            self.strength_indicator.visible = False
            self.back_button.visible = False
            
            # Mostrar campos de login
            self.email_field.visible = True
            self.password_field.visible = True
            
        else:
            # Cambiar a registro
            self.action_button.text = "Registrarse"
            self.action_button.icon = ft.icons.PERSON_ADD
            self.switch_button.text = "¿Ya tienes cuenta? Inicia sesión aquí"
            
            # Mostrar campos de registro
            self.username_field.visible = True
            self.cedula_field.visible = True
            self.confirm_password_field.visible = True
            self.strength_indicator.visible = True
            self.back_button.visible = True
            
            # Mostrar campos de login también
            self.email_field.visible = True
            self.password_field.visible = True
        
        # Limpiar mensajes
        self.message_text.value = ""
        self.page.update()

    def _update_password_strength(self, e):
        """Actualiza el indicador de fuerza de contraseña."""
        password = self.password_field.value
        strength = self._check_password_strength(password)
        
        if strength == "Débil":
            color = ft.colors.RED
        elif strength == "Medio":
            color = ft.colors.ORANGE
        else:
            color = ft.colors.GREEN
            
        self.strength_indicator.value = f"Fuerza: {strength}"
        self.strength_indicator.color = color
        self.page.update()

    def setup_event_handlers(self):
        """Configura los manejadores de eventos."""
        self.password_field.on_change = self._update_password_strength
