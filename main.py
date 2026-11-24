"""
=============================================================================
SEGURIDAD SOS - KIVYMD (TAMAÑO ESCRITORIO / MÓVIL)
=============================================================================
Interfaz migrada a KivyMD 2.0.0: MDButton, MDNavigationBar, MDNavigationDrawer
y componentes MD3. La paleta usa tokens coherentes Primary/Secondary/Surface/
Error con sus colores "On-*".

Tamaños disponibles:
  - Escritorio/web: 1280x800 (por defecto en main.py)
  - Móvil:          414x896  (por defecto en mobile/main.py)
Se puede cambiar en caliente con F9 o con --desktop / --mobile.
"""

import os
import sys
import traceback

# Kivy parsea sys.argv durante la importación; quitamos nuestros flags antes.
_CUSTOM_VIEW_FLAGS = ("--desktop", "--mobile")
CLI_VIEW = next((flag[2:] for flag in sys.argv[1:] if flag in _CUSTOM_VIEW_FLAGS), None)
sys.argv = [arg for arg in sys.argv if arg not in _CUSTOM_VIEW_FLAGS]

import db_manager
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.screenmanager import CardTransition
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex, platform
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogButtonContainer,
    MDDialogHeadlineText,
    MDDialogSupportingText,
)
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.navigationbar import MDNavigationItem
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText


class BottomNavItem(MDNavigationItem):
    """Item de MDNavigationBar con pantalla asociada y acción opcional."""

    screen_name = StringProperty("nav_home")
    icon_name = StringProperty("home")
    label_text = StringProperty("Inicio")
    action_name = StringProperty("")

    def on_release(self):
        super().on_release()
        if self.action_name == "sos":
            app = MDApp.get_running_app()
            if app:
                app.activate_sos_overlay()


Factory.register("BottomNavItem", cls=BottomNavItem)


DESKTOP_WINDOW_SIZE = (1280, 800)
MOBILE_WINDOW_SIZE = (414, 896)
DEFAULT_VIEW_MODE = "desktop"


def resolve_view_mode(default):
    """Permite elegir tamaño por argumento, variable de entorno o valor por defecto."""
    if CLI_VIEW:
        return CLI_VIEW

    env_mode = os.getenv("VIGIA_VIEW", "").strip().lower()
    if env_mode in ("desktop", "web", "web-escritorio"):
        return "desktop"
    if env_mode in ("mobile", "movil", "phone"):
        return "mobile"
    return default


VIEW_MODE = resolve_view_mode(DEFAULT_VIEW_MODE)
WINDOW_SIZE = DESKTOP_WINDOW_SIZE if VIEW_MODE == "desktop" else MOBILE_WINDOW_SIZE

if platform in ("win", "linux", "macosx"):
    Window.size = WINDOW_SIZE


KV = '''
#:import dp kivy.metrics.dp

MDScreenManager:
    id: screen_manager
    AuthScreen:
        id: auth_screen
        name: "auth"
    MainScreen:
        id: main_screen
        name: "main"
    CamerasScreen:
        id: cameras_screen
        name: "cameras"

# ==========================================================================
# DRAWER M3: incluye SIEMPRE la acción de alerta SOS
# ==========================================================================
<AppNavigationDrawer@MDNavigationDrawer>:
    id: drawer
    radius: 0, dp(16), dp(16), 0
    width: dp(288)
    size_hint_y: None
    height: self.parent.height if self.parent else dp(600)
    theme_bg_color: "Custom"
    background_color: [0.09, 0.12, 0.24, 1]
    md_bg_color: [0.09, 0.12, 0.24, 1]
    elevation: 0

    MDBoxLayout:
        orientation: "vertical"
        size_hint: 1, 1
        padding: dp(16)
        spacing: dp(12)
        theme_bg_color: "Custom"
        md_bg_color: [0.09, 0.12, 0.24, 1]

        MDLabel:
            text: "VIGÍA SOS"
            bold: True
            size_hint_y: None
            height: dp(40)
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1

        MDLabel:
            text: app.user_name + " · " + app.user_phone_display
            font_size: '12sp'
            size_hint_y: None
            height: dp(24)
            theme_text_color: "Custom"
            text_color: app.text_secondary

        MDButton:
            id: drawer_sos_item
            style: "filled"
            theme_bg_color: "Custom"
            theme_width: "Custom"
            md_bg_color: [0.85, 0.15, 0.2, 1]
            size_hint_x: 1
            size_hint_y: None
            height: dp(52)
            on_release: app.drawer_sos()

            MDButtonIcon:
                icon: "alert-circle"
                theme_icon_color: "Custom"
                icon_color: 1, 1, 1, 1

            MDButtonText:
                text: "ENVIAR ALERTA SOS"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1

        MDButton:
            id: drawer_home_item
            style: "tonal"
            theme_width: "Custom"
            size_hint_x: 1
            size_hint_y: None
            height: dp(48)
            on_release: app.drawer_navigate("main", "nav_home")

            MDButtonText:
                text: "Inicio"
                theme_text_color: "Custom"
                text_color: app.text_primary

        MDButton:
            id: drawer_contacts_item
            style: "tonal"
            theme_width: "Custom"
            size_hint_x: 1
            size_hint_y: None
            height: dp(48)
            on_release: app.drawer_navigate("main", "nav_contacts")

            MDButtonText:
                text: "Contactos/Emergencias"
                theme_text_color: "Custom"
                text_color: app.text_primary

        MDButton:
            id: drawer_cameras_item
            style: "tonal"
            theme_width: "Custom"
            size_hint_x: 1
            size_hint_y: None
            height: dp(48)
            on_release: app.drawer_navigate("cameras")

            MDButtonText:
                text: "Cámaras"
                theme_text_color: "Custom"
                text_color: app.text_primary

        MDButton:
            id: drawer_history_item
            style: "tonal"
            theme_width: "Custom"
            size_hint_x: 1
            size_hint_y: None
            height: dp(48)
            on_release: app.drawer_navigate("main", "nav_sos")

            MDButtonText:
                text: "Historial de Alertas"
                theme_text_color: "Custom"
                text_color: app.text_primary

        MDButton:
            id: drawer_logout_item
            style: "tonal"
            theme_width: "Custom"
            size_hint_x: 1
            size_hint_y: None
            height: dp(48)
            on_release: app.close_nav_drawer(); app.logout()

            MDButtonText:
                text: "Cerrar Sesión"
                theme_text_color: "Custom"
                text_color: app.text_primary

        Widget:
            size_hint_y: 1

# ==========================================================================
# AUTENTICACIÓN
# ==========================================================================
<AuthScreen@MDScreen>:
    md_bg_color: app.bg_main

    MDBoxLayout:
        orientation: "vertical"
        padding: ['20dp', '28dp', '20dp', '16dp']
        spacing: '14dp'

        MDBoxLayout:
            adaptive_height: True
            orientation: "vertical"
            spacing: '6dp'
            padding: [0, '14dp', 0, '8dp']

            MDBoxLayout:
                adaptive_height: True
                pos_hint: {'center_x': .5}
                spacing: '10dp'

                MDIcon:
                    icon: "shield_check"
                    theme_text_color: "Custom"
                    text_color: app.btn_primary
                    font_size: '34sp'

                MDLabel:
                    text: "SEGURIDAD SOS"
                    font_style: "Title"
                    role: "large"
                    adaptive_size: True
                    theme_text_color: "Custom"
                    text_color: app.text_primary
                    pos_hint: {'center_y': .5}

            MDLabel:
                text: "Tu tranquilidad empieza aquí"
                halign: 'center'
                theme_text_color: "Custom"
                text_color: app.text_secondary
                font_style: "Body"
                role: "medium"

        MDBoxLayout:
            adaptive_height: True
            spacing: '10dp'
            padding: [0, '4dp', 0, '8dp']

            MDButton:
                id: tab_login
                style: "filled" if app.auth_tab == 'login' else "tonal"
                theme_bg_color: "Custom"
                theme_width: "Custom"
                md_bg_color: app.btn_primary if app.auth_tab == 'login' else app.bg_card
                size_hint_x: .5
                size_hint_y: None
                height: '48dp'
                on_release: app.set_auth_tab('login')

                MDButtonText:
                    text: "INICIAR SESIÓN"
                    font_size: '13sp'
                    theme_text_color: "Custom"
                    text_color: app.md3_on_primary if app.auth_tab == 'login' else app.text_primary

            MDButton:
                id: tab_register
                style: "filled" if app.auth_tab == 'register' else "tonal"
                theme_bg_color: "Custom"
                theme_width: "Custom"
                md_bg_color: app.btn_primary if app.auth_tab == 'register' else app.bg_card
                size_hint_x: .5
                size_hint_y: None
                height: '48dp'
                on_release: app.set_auth_tab('register')

                MDButtonText:
                    text: "CREAR CUENTA"
                    font_size: '13sp'
                    theme_text_color: "Custom"
                    text_color: app.md3_on_primary if app.auth_tab == 'register' else app.text_primary

        MDScrollView:
            do_scroll_x: False

            MDBoxLayout:
                orientation: 'vertical'
                spacing: '14dp'
                adaptive_height: True
                padding: [0, '8dp', 0, '20dp']

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: '12dp'
                    adaptive_height: True
                    opacity: 1 if app.auth_tab == 'login' else 0
                    disabled: app.auth_tab != 'login'
                    size_hint_y: None
                    height: self.minimum_height if app.auth_tab == 'login' else 0

                    MDLabel:
                        text: "Bienvenido de nuevo"
                        font_style: "Title"
                        role: "large"
                        adaptive_height: True
                        theme_text_color: "Custom"
                        text_color: app.text_primary

                    MDLabel:
                        text: "Ingresa con tu correo y contraseña registrados"
                        font_style: "Body"
                        role: "medium"
                        adaptive_height: True
                        theme_text_color: "Custom"
                        text_color: app.text_secondary

                    MDTextField:
                        id: login_email
                        mode: "filled"
                        password: False
                        theme_text_color: "Custom"
                        text_color_normal: app.text_primary
                        text_color_focus: app.text_primary
                        theme_line_color: "Custom"
                        line_color_normal: app.border_input
                        line_color_focus: app.accent_cyan
                        theme_bg_color: "Custom"
                        fill_color_normal: app.bg_input_nav
                        fill_color_focus: app.bg_input_nav
                        radius: [14, 14, 0, 0]

                        MDTextFieldHintText:
                            text: "Correo Electrónico"
                            theme_text_color: "Custom"
                            text_color_normal: app.text_secondary
                            text_color_focus: app.accent_cyan

                        MDTextFieldLeadingIcon:
                            icon: "mail"
                            theme_icon_color: "Custom"
                            icon_color_normal: app.accent_cyan
                            icon_color_focus: app.accent_cyan

                    MDTextField:
                        id: login_password
                        mode: "filled"
                        password: True
                        theme_text_color: "Custom"
                        text_color_normal: app.text_primary
                        text_color_focus: app.text_primary
                        theme_line_color: "Custom"
                        line_color_normal: app.border_input
                        line_color_focus: app.accent_cyan
                        theme_bg_color: "Custom"
                        fill_color_normal: app.bg_input_nav
                        fill_color_focus: app.bg_input_nav
                        radius: [14, 14, 0, 0]

                        MDTextFieldHintText:
                            text: "Contraseña"
                            theme_text_color: "Custom"
                            text_color_normal: app.text_secondary
                            text_color_focus: app.accent_cyan

                        MDTextFieldLeadingIcon:
                            icon: "lock"
                            theme_icon_color: "Custom"
                            icon_color_normal: app.accent_cyan
                            icon_color_focus: app.accent_cyan

                    MDButton:
                        style: "filled"
                        theme_bg_color: "Custom"
                        theme_width: "Custom"
                        md_bg_color: app.btn_primary
                        size_hint_x: 1
                        size_hint_y: None
                        height: '52dp'
                        radius: [100, 100, 100, 100]
                        on_release: app.process_auth_submit()

                        MDButtonText:
                            text: "INICIAR SESIÓN"
                            font_size: '15sp'
                            theme_text_color: "Custom"
                            text_color: app.md3_on_primary

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: '12dp'
                    adaptive_height: True
                    opacity: 1 if app.auth_tab == 'register' else 0
                    disabled: app.auth_tab != 'register'
                    size_hint_y: None
                    height: self.minimum_height if app.auth_tab == 'register' else 0

                    MDLabel:
                        text: "Crea tu cuenta SOS"
                        font_style: "Title"
                        role: "large"
                        adaptive_height: True
                        theme_text_color: "Custom"
                        text_color: app.text_primary

                    MDLabel:
                        text: "Protege a tu familia y comunidad las 24 horas"
                        font_style: "Body"
                        role: "medium"
                        adaptive_height: True
                        theme_text_color: "Custom"
                        text_color: app.text_secondary

                    MDTextField:
                        id: reg_name
                        mode: "filled"
                        theme_text_color: "Custom"
                        text_color_normal: app.text_primary
                        text_color_focus: app.text_primary
                        theme_line_color: "Custom"
                        line_color_normal: app.border_input
                        line_color_focus: app.accent_cyan
                        theme_bg_color: "Custom"
                        fill_color_normal: app.bg_input_nav
                        fill_color_focus: app.bg_input_nav
                        radius: [14, 14, 0, 0]

                        MDTextFieldHintText:
                            text: "Nombre Completo"
                            theme_text_color: "Custom"
                            text_color_normal: app.text_secondary
                            text_color_focus: app.accent_cyan

                        MDTextFieldLeadingIcon:
                            icon: "person"
                            theme_icon_color: "Custom"
                            icon_color_normal: app.accent_cyan
                            icon_color_focus: app.accent_cyan

                    MDTextField:
                        id: reg_phone
                        mode: "filled"
                        theme_text_color: "Custom"
                        text_color_normal: app.text_primary
                        text_color_focus: app.text_primary
                        theme_line_color: "Custom"
                        line_color_normal: app.border_input
                        line_color_focus: app.accent_cyan
                        theme_bg_color: "Custom"
                        fill_color_normal: app.bg_input_nav
                        fill_color_focus: app.bg_input_nav
                        radius: [14, 14, 0, 0]

                        MDTextFieldHintText:
                            text: "Teléfono Móvil"
                            theme_text_color: "Custom"
                            text_color_normal: app.text_secondary
                            text_color_focus: app.accent_cyan

                        MDTextFieldLeadingIcon:
                            icon: "smartphone"
                            theme_icon_color: "Custom"
                            icon_color_normal: app.accent_cyan
                            icon_color_focus: app.accent_cyan

                    MDTextField:
                        id: reg_email
                        mode: "filled"
                        theme_text_color: "Custom"
                        text_color_normal: app.text_primary
                        text_color_focus: app.text_primary
                        theme_line_color: "Custom"
                        line_color_normal: app.border_input
                        line_color_focus: app.accent_cyan
                        theme_bg_color: "Custom"
                        fill_color_normal: app.bg_input_nav
                        fill_color_focus: app.bg_input_nav
                        radius: [14, 14, 0, 0]

                        MDTextFieldHintText:
                            text: "Correo Electrónico"
                            theme_text_color: "Custom"
                            text_color_normal: app.text_secondary
                            text_color_focus: app.accent_cyan

                        MDTextFieldLeadingIcon:
                            icon: "mail"
                            theme_icon_color: "Custom"
                            icon_color_normal: app.accent_cyan
                            icon_color_focus: app.accent_cyan

                    MDTextField:
                        id: reg_password
                        mode: "filled"
                        password: True
                        theme_text_color: "Custom"
                        text_color_normal: app.text_primary
                        text_color_focus: app.text_primary
                        theme_line_color: "Custom"
                        line_color_normal: app.border_input
                        line_color_focus: app.accent_cyan
                        theme_bg_color: "Custom"
                        fill_color_normal: app.bg_input_nav
                        fill_color_focus: app.bg_input_nav
                        radius: [14, 14, 0, 0]

                        MDTextFieldHintText:
                            text: "Contraseña de seguridad"
                            theme_text_color: "Custom"
                            text_color_normal: app.text_secondary
                            text_color_focus: app.accent_cyan

                        MDTextFieldLeadingIcon:
                            icon: "lock"
                            theme_icon_color: "Custom"
                            icon_color_normal: app.accent_cyan
                            icon_color_focus: app.accent_cyan

                    MDButton:
                        style: "filled"
                        theme_bg_color: "Custom"
                        theme_width: "Custom"
                        md_bg_color: app.btn_primary
                        size_hint_x: 1
                        size_hint_y: None
                        height: '52dp'
                        radius: [100, 100, 100, 100]
                        on_release: app.process_auth_submit()

                        MDButtonText:
                            text: "CREAR MI CUENTA SOS"
                            font_size: '15sp'
                            theme_text_color: "Custom"
                            text_color: app.md3_on_primary

# ==========================================================================
# PANTALLA PRINCIPAL: DRAWER + NAVEGACIÓN INFERIOR + OVERLAY SOS
# ==========================================================================
<MainScreen@MDScreen>:
    md_bg_color: app.bg_main

    MDNavigationLayout:
        id: main_nav_layout
        size_hint: None, None
        size: self.parent.size if self.parent else (dp(1), dp(1))

        MDScreenManager:
            id: main_tabs

            MDScreen:
                name: "nav_home"

                MDScrollView:
                    do_scroll_x: False

                    MDBoxLayout:
                        orientation: 'vertical'
                        padding: ['20dp', '16dp', '20dp', '96dp']
                        spacing: '12dp'
                        adaptive_height: True
                        theme_bg_color: "Custom"
                        md_bg_color: app.bg_main

                        MDBoxLayout:
                            adaptive_height: True
                            spacing: '8dp'

                            MDIconButton:
                                icon: "menu"
                                style: "standard"
                                theme_icon_color: "Custom"
                                icon_color: app.text_primary
                                on_release: app.open_nav_drawer()

                            MDBoxLayout:
                                orientation: 'vertical'
                                adaptive_height: True
                                padding: ['4dp', 0, 0, 0]

                                MDBoxLayout:
                                    adaptive_height: True
                                    spacing: '8dp'
                                    MDIcon:
                                        icon: "shield_check"
                                        theme_text_color: "Custom"
                                        text_color: app.btn_primary
                                        font_size: '24sp'
                                    MDLabel:
                                        text: "SEGURIDAD SOS"
                                        font_style: "Title"
                                        role: "medium"
                                        adaptive_size: True
                                        theme_text_color: "Custom"
                                        text_color: app.text_primary

                                MDLabel:
                                    text: "Sistema de protección activo 24/7"
                                    font_style: "Body"
                                    role: "small"
                                    adaptive_height: True
                                    theme_text_color: "Custom"
                                    text_color: app.text_secondary

                            Widget:
                                size_hint_x: 1

                        MDLabel:
                            text: "Hola, " + app.user_name
                            font_style: "Headline"
                            role: "small"
                            adaptive_height: True
                            theme_text_color: "Custom"
                            text_color: app.text_primary

                        MDCard:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: '265dp'
                            theme_bg_color: "Custom"
                            md_bg_color: app.zone_alert
                            radius: [24, 24, 24, 24]
                            padding: '16dp'
                            spacing: '8dp'

                            MDFloatLayout:
                                Widget:
                                    size_hint: None, None
                                    size: "196dp", "196dp"
                                    pos_hint: {"center_x": .5, "center_y": .54}
                                    canvas.before:
                                        Color:
                                            rgba: 1, 1, 1, 0.25
                                        Line:
                                            circle: (self.center_x, self.center_y, dp(90 * app.sos_scale))
                                            width: dp(4)
                                        Color:
                                            rgba: app.accent_cyan
                                        Line:
                                            circle: (self.center_x, self.center_y, dp(90 * app.sos_scale), 0, app.sos_progress * 360)
                                            width: dp(5)

                                MDButton:
                                    id: sos_hold_button
                                    style: "filled"
                                    theme_bg_color: "Custom"
                                    theme_width: "Custom"
                                    md_bg_color: app.sos_red
                                    size_hint: None, None
                                    size: (dp(162 * app.sos_scale), dp(162 * app.sos_scale))
                                    pos_hint: {"center_x": .5, "center_y": .54}
                                    radius: [dp(81 * app.sos_scale), dp(81 * app.sos_scale), dp(81 * app.sos_scale), dp(81 * app.sos_scale)]
                                    on_press: app.start_sos_hold()
                                    on_release: app.cancel_sos_hold()

                                    MDButtonText:
                                        id: sos_hold_text
                                        text: "SOS\\nPEDIR AYUDA"
                                        halign: "center"
                                        font_size: '24sp'
                                        theme_text_color: "Custom"
                                        text_color: app.md3_on_sos
                                        pos_hint: {"center_x": .5, "center_y": .5}
                                        size_hint: None, None
                                        size: '150dp', '90dp'

                            MDLabel:
                                text: app.sos_status_text
                                halign: "center"
                                font_style: "Label"
                                role: "large"
                                adaptive_height: True
                                theme_text_color: "Custom"
                                text_color: app.md3_on_error_container

                        MDLabel:
                            text: "ACCESOS RÁPIDOS"
                            font_style: "Label"
                            role: "large"
                            adaptive_height: True
                            theme_text_color: "Custom"
                            text_color: app.accent_cyan

                        MDGridLayout:
                            cols: 2
                            spacing: '12dp'
                            size_hint_y: None
                            height: '96dp'

                            MDCard:
                                orientation: 'vertical'
                                padding: '14dp'
                                spacing: '8dp'
                                theme_bg_color: "Custom"
                                md_bg_color: app.action_blue
                                radius: [16, 16, 16, 16]
                                ripple_behavior: True
                                on_release: app.show_snackbar("Llamando al 911...")

                                MDIcon:
                                    icon: "phone_in_talk"
                                    font_size: '28sp'
                                    size_hint_y: None
                                    height: '28dp'
                                    theme_text_color: "Custom"
                                    text_color: app.accent_cyan

                                MDLabel:
                                    text: "Llamar al 911"
                                    font_style: "Body"
                                    role: "medium"
                                    theme_text_color: "Custom"
                                    text_color: app.text_primary

                            MDCard:
                                orientation: 'vertical'
                                padding: '14dp'
                                spacing: '8dp'
                                theme_bg_color: "Custom"
                                md_bg_color: app.action_blue
                                radius: [16, 16, 16, 16]
                                ripple_behavior: True
                                on_release: app.show_snackbar("Ubicación GPS compartida")

                                MDIcon:
                                    icon: "share_location"
                                    font_size: '28sp'
                                    size_hint_y: None
                                    height: '28dp'
                                    theme_text_color: "Custom"
                                    text_color: app.accent_cyan

                                MDLabel:
                                    text: "Compartir ubicación"
                                    font_style: "Body"
                                    role: "medium"
                                    theme_text_color: "Custom"
                                    text_color: app.text_primary

                        MDCard:
                            adaptive_height: True
                            padding: '16dp'
                            theme_bg_color: "Custom"
                            md_bg_color: app.bg_card
                            radius: [20, 20, 20, 20]
                            ripple_behavior: True
                            on_release: app.navigate_to('cameras', 'left')

                            MDIcon:
                                icon: "linked_camera"
                                theme_text_color: "Custom"
                                text_color: app.accent_cyan
                                font_size: '28sp'
                                size_hint: None, None
                                size: '28dp', '28dp'
                                pos_hint: {'center_y': .5}

                            MDBoxLayout:
                                orientation: 'vertical'
                                adaptive_height: True
                                padding: ['12dp', 0, 0, 0]

                                MDLabel:
                                    text: "Ver cámaras"
                                    font_style: "Title"
                                    role: "medium"
                                    adaptive_height: True
                                    theme_text_color: "Custom"
                                    text_color: app.text_primary

                                MDLabel:
                                    text: "3 dispositivos conectados"
                                    font_style: "Body"
                                    role: "small"
                                    adaptive_height: True
                                    theme_text_color: "Custom"
                                    text_color: app.text_secondary

                            MDIcon:
                                icon: "chevron_right"
                                theme_text_color: "Custom"
                                text_color: app.accent_cyan
                                pos_hint: {'center_y': .5}

            MDScreen:
                name: "nav_sos"

                MDBoxLayout:
                    orientation: 'vertical'
                    padding: ['24dp', '24dp', '24dp', '96dp']
                    spacing: '18dp'
                    theme_bg_color: "Custom"
                    md_bg_color: app.bg_main

                    MDLabel:
                        text: "CENTRAL DE EMERGENCIA SOS"
                        font_style: "Title"
                        role: "large"
                        halign: 'center'
                        adaptive_height: True
                        theme_text_color: "Custom"
                        text_color: app.accent_cyan

                    MDButton:
                        style: "filled"
                        theme_bg_color: "Custom"
                        theme_width: "Custom"
                        md_bg_color: app.sos_red
                        size_hint: (1, None)
                        height: '140dp'
                        radius: [28, 28, 28, 28]
                        on_release: app.activate_sos_overlay()

                        MDButtonText:
                            text: "DISPARAR ALERTA INMEDIATA"
                            font_size: '18sp'
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: app.md3_on_sos
                            pos_hint: {"center_x": .5, "center_y": .5}
                            size_hint: None, None
                            size: '260dp', '80dp'

                    MDLabel:
                        text: "Envía coordenadas GPS en tiempo real a la patrulla policial y a tus contactos de emergencia."
                        halign: 'center'
                        font_style: "Body"
                        role: "medium"
                        adaptive_height: True
                        theme_text_color: "Custom"
                        text_color: app.text_secondary

                    Widget:

            MDScreen:
                name: "nav_contacts"

                MDScrollView:
                    do_scroll_x: False

                    MDBoxLayout:
                        orientation: 'vertical'
                        padding: ['20dp', '16dp', '20dp', '96dp']
                        spacing: '14dp'
                        adaptive_height: True
                        theme_bg_color: "Custom"
                        md_bg_color: app.bg_main

                        MDBoxLayout:
                            adaptive_height: True
                            spacing: '10dp'

                            MDIcon:
                                icon: "contacts"
                                theme_text_color: "Custom"
                                text_color: app.accent_cyan
                                font_size: '30sp'

                            MDBoxLayout:
                                orientation: 'vertical'
                                adaptive_height: True

                                MDLabel:
                                    text: "Contactos de Emergencia"
                                    font_style: "Title"
                                    role: "medium"
                                    adaptive_height: True
                                    theme_text_color: "Custom"
                                    text_color: app.text_primary

                                MDLabel:
                                    text: "Personas y organismos que reciben tus alertas SOS"
                                    font_style: "Body"
                                    role: "small"
                                    adaptive_height: True
                                    theme_text_color: "Custom"
                                    text_color: app.text_secondary

                        MDCard:
                            id: contacts_list_card
                            orientation: 'vertical'
                            adaptive_height: True
                            padding: '16dp'
                            spacing: '10dp'
                            theme_bg_color: "Custom"
                            md_bg_color: app.bg_card
                            radius: [20, 20, 20, 20]

                            MDLabel:
                                id: contacts_list_title
                                text: "Contactos registrados"
                                font_style: "Title"
                                role: "small"
                                adaptive_height: True
                                theme_text_color: "Custom"
                                text_color: app.text_primary

                            MDBoxLayout:
                                id: contacts_list
                                orientation: 'vertical'
                                adaptive_height: True
                                spacing: '8dp'

                        MDCard:
                            orientation: 'vertical'
                            adaptive_height: True
                            padding: '16dp'
                            spacing: '12dp'
                            theme_bg_color: "Custom"
                            md_bg_color: app.bg_card
                            radius: [20, 20, 20, 20]

                            MDLabel:
                                text: "Agregar contacto"
                                font_style: "Title"
                                role: "small"
                                adaptive_height: True
                                theme_text_color: "Custom"
                                text_color: app.text_primary

                            MDTextField:
                                id: contact_name
                                mode: "filled"
                                theme_text_color: "Custom"
                                text_color_normal: app.text_primary
                                text_color_focus: app.text_primary
                                theme_line_color: "Custom"
                                line_color_normal: app.border_input
                                line_color_focus: app.accent_cyan
                                theme_bg_color: "Custom"
                                fill_color_normal: app.bg_input_nav
                                fill_color_focus: app.bg_input_nav
                                radius: [14, 14, 0, 0]

                                MDTextFieldHintText:
                                    text: "Nombre del contacto"
                                    theme_text_color: "Custom"
                                    text_color_normal: app.text_secondary
                                    text_color_focus: app.accent_cyan

                                MDTextFieldLeadingIcon:
                                    icon: "account"
                                    theme_icon_color: "Custom"
                                    icon_color_normal: app.accent_cyan
                                    icon_color_focus: app.accent_cyan

                            MDTextField:
                                id: contact_phone
                                mode: "filled"
                                theme_text_color: "Custom"
                                text_color_normal: app.text_primary
                                text_color_focus: app.text_primary
                                theme_line_color: "Custom"
                                line_color_normal: app.border_input
                                line_color_focus: app.accent_cyan
                                theme_bg_color: "Custom"
                                fill_color_normal: app.bg_input_nav
                                fill_color_focus: app.bg_input_nav
                                radius: [14, 14, 0, 0]

                                MDTextFieldHintText:
                                    text: "Teléfono"
                                    theme_text_color: "Custom"
                                    text_color_normal: app.text_secondary
                                    text_color_focus: app.accent_cyan

                                MDTextFieldLeadingIcon:
                                    icon: "phone"
                                    theme_icon_color: "Custom"
                                    icon_color_normal: app.accent_cyan
                                    icon_color_focus: app.accent_cyan

                            MDLabel:
                                text: "Tipo de contacto"
                                font_style: "Body"
                                role: "small"
                                adaptive_height: True
                                theme_text_color: "Custom"
                                text_color: app.text_secondary

                            MDBoxLayout:
                                adaptive_height: True
                                spacing: '8dp'

                                MDButton:
                                    style: "filled" if app.new_contact_type == 'police' else "tonal"
                                    theme_bg_color: "Custom"
                                    theme_width: "Custom"
                                    md_bg_color: app.btn_primary if app.new_contact_type == 'police' else app.bg_input_nav
                                    size_hint_x: .25
                                    size_hint_y: None
                                    height: dp(40)
                                    on_release: app.set_new_contact_type('police')

                                    MDButtonText:
                                        text: "Policía"
                                        font_size: '11sp'
                                        theme_text_color: "Custom"
                                        text_color: app.md3_on_primary if app.new_contact_type == 'police' else app.text_primary

                                MDButton:
                                    style: "filled" if app.new_contact_type == 'firefighter' else "tonal"
                                    theme_bg_color: "Custom"
                                    theme_width: "Custom"
                                    md_bg_color: app.btn_primary if app.new_contact_type == 'firefighter' else app.bg_input_nav
                                    size_hint_x: .25
                                    size_hint_y: None
                                    height: dp(40)
                                    on_release: app.set_new_contact_type('firefighter')

                                    MDButtonText:
                                        text: "Bomberos"
                                        font_size: '11sp'
                                        theme_text_color: "Custom"
                                        text_color: app.md3_on_primary if app.new_contact_type == 'firefighter' else app.text_primary

                                MDButton:
                                    style: "filled" if app.new_contact_type == 'medical' else "tonal"
                                    theme_bg_color: "Custom"
                                    theme_width: "Custom"
                                    md_bg_color: app.btn_primary if app.new_contact_type == 'medical' else app.bg_input_nav
                                    size_hint_x: .25
                                    size_hint_y: None
                                    height: dp(40)
                                    on_release: app.set_new_contact_type('medical')

                                    MDButtonText:
                                        text: "Médico"
                                        font_size: '11sp'
                                        theme_text_color: "Custom"
                                        text_color: app.md3_on_primary if app.new_contact_type == 'medical' else app.text_primary

                                MDButton:
                                    style: "filled" if app.new_contact_type == 'other' else "tonal"
                                    theme_bg_color: "Custom"
                                    theme_width: "Custom"
                                    md_bg_color: app.btn_primary if app.new_contact_type == 'other' else app.bg_input_nav
                                    size_hint_x: .25
                                    size_hint_y: None
                                    height: dp(40)
                                    on_release: app.set_new_contact_type('other')

                                    MDButtonText:
                                        text: "Otro"
                                        font_size: '11sp'
                                        theme_text_color: "Custom"
                                        text_color: app.md3_on_primary if app.new_contact_type == 'other' else app.text_primary

                            MDButton:
                                style: "filled"
                                theme_bg_color: "Custom"
                                theme_width: "Custom"
                                md_bg_color: app.action_blue
                                size_hint_x: 1
                                size_hint_y: None
                                height: dp(48)
                                radius: [100, 100, 100, 100]
                                on_release: app.add_emergency_contact_from_form()

                                MDButtonText:
                                    text: "GUARDAR CONTACTO"
                                    theme_text_color: "Custom"
                                    text_color: 1, 1, 1, 1

            MDScreen:
                name: "nav_profile"

                MDBoxLayout:
                    orientation: 'vertical'
                    padding: ['20dp', '16dp', '20dp', '96dp']
                    spacing: '14dp'
                    theme_bg_color: "Custom"
                    md_bg_color: app.bg_main

                    MDLabel:
                        text: "Mi perfil"
                        font_style: "Headline"
                        role: "small"
                        adaptive_height: True
                        theme_text_color: "Custom"
                        text_color: app.text_primary

                    MDLabel:
                        text: "Gestión de cuenta y configuración de seguridad"
                        font_style: "Body"
                        role: "medium"
                        adaptive_height: True
                        theme_text_color: "Custom"
                        text_color: app.text_secondary

                    MDCard:
                        orientation: 'vertical'
                        adaptive_height: True
                        padding: '16dp'
                        spacing: '14dp'
                        theme_bg_color: "Custom"
                        md_bg_color: app.bg_card
                        radius: [20, 20, 20, 20]

                        MDBoxLayout:
                            adaptive_height: True
                            spacing: '14dp'
                            MDIcon:
                                icon: "person"
                                theme_text_color: "Custom"
                                text_color: app.accent_cyan
                                font_size: '28sp'
                            MDBoxLayout:
                                orientation: 'vertical'
                                adaptive_height: True
                                MDLabel:
                                    text: app.user_name
                                    font_style: "Title"
                                    role: "medium"
                                    adaptive_height: True
                                    theme_text_color: "Custom"
                                    text_color: app.text_primary
                                MDLabel:
                                    text: "Titular de la cuenta SOS"
                                    font_style: "Body"
                                    role: "small"
                                    adaptive_height: True
                                    theme_text_color: "Custom"
                                    text_color: app.text_secondary

                        MDDivider:
                            theme_divider_color: "Custom"
                            color: app.border_input

                        MDBoxLayout:
                            adaptive_height: True
                            spacing: '14dp'
                            MDIcon:
                                icon: "smartphone"
                                theme_text_color: "Custom"
                                text_color: app.accent_cyan
                                font_size: '26sp'
                            MDBoxLayout:
                                orientation: 'vertical'
                                adaptive_height: True
                                MDLabel:
                                    text: app.user_phone_display
                                    font_style: "Title"
                                    role: "medium"
                                    adaptive_height: True
                                    theme_text_color: "Custom"
                                    text_color: app.text_primary
                                MDLabel:
                                    text: "Teléfono registrado para alertas"
                                    font_style: "Body"
                                    role: "small"
                                    adaptive_height: True
                                    theme_text_color: "Custom"
                                    text_color: app.text_secondary

                        MDDivider:
                            theme_divider_color: "Custom"
                            color: app.border_input

                        MDBoxLayout:
                            adaptive_height: True
                            spacing: '14dp'
                            MDIcon:
                                icon: "shield_check"
                                theme_text_color: "Custom"
                                text_color: app.accent_cyan
                                font_size: '26sp'
                            MDBoxLayout:
                                orientation: 'vertical'
                                adaptive_height: True
                                MDLabel:
                                    text: "Protección Satelital GPS"
                                    font_style: "Title"
                                    role: "medium"
                                    adaptive_height: True
                                    theme_text_color: "Custom"
                                    text_color: app.text_primary
                                MDLabel:
                                    text: "Activa (Precisión: 3 metros)"
                                    font_style: "Body"
                                    role: "small"
                                    adaptive_height: True
                                    theme_text_color: "Custom"
                                    text_color: app.accent_cyan

                    Widget:

                    MDButton:
                        style: "outlined"
                        theme_bg_color: "Custom"
                        theme_width: "Custom"
                        md_bg_color: app.bg_card
                        size_hint_x: 1
                        size_hint_y: None
                        height: '48dp'
                        radius: [100, 100, 100, 100]
                        on_release: app.logout()

                        MDButtonText:
                            text: "CERRAR SESIÓN"
                            font_size: '14sp'
                            theme_text_color: "Custom"
                            text_color: app.accent_cyan

        AppNavigationDrawer:
            id: main_drawer

    MDNavigationBar:
        id: bottom_nav
        size_hint: 1, None
        height: '80dp'
        pos_hint: {"x": 0, "y": 0}
        padding: [0, '4dp', 0, '8dp']
        theme_bg_color: "Custom"
        md_bg_color: app.bg_input_nav
        on_switch_tabs: app.on_main_tab_switched(*args)

        BottomNavItem:
            id: nav_home_item
            screen_name: "nav_home"
            icon_name: "home"
            label_text: "Inicio"
            active: True
            indicator_color: app.btn_primary

            MDNavigationItemIcon:
                icon: nav_home_item.icon_name
                icon_color_active: app.btn_primary
                icon_color_normal: app.text_secondary
            MDNavigationItemLabel:
                text: nav_home_item.label_text
                font_size: '12sp'
                text_color_active: app.btn_primary
                text_color_normal: app.text_secondary

        BottomNavItem:
            id: nav_contacts_item
            screen_name: "nav_contacts"
            icon_name: "contacts"
            label_text: "Contactos"
            indicator_color: app.btn_primary

            MDNavigationItemIcon:
                icon: nav_contacts_item.icon_name
                icon_color_active: app.btn_primary
                icon_color_normal: app.text_secondary
            MDNavigationItemLabel:
                text: nav_contacts_item.label_text
                font_size: '12sp'
                text_color_active: app.btn_primary
                text_color_normal: app.text_secondary

        BottomNavItem:
            id: nav_sos_item
            screen_name: "nav_sos"
            icon_name: "sos"
            label_text: "SOS"
            action_name: "sos"
            indicator_color: app.sos_red

            MDNavigationItemIcon:
                icon: nav_sos_item.icon_name
                icon_color_active: app.md3_error
                icon_color_normal: app.text_secondary
            MDNavigationItemLabel:
                text: nav_sos_item.label_text
                font_size: '12sp'
                text_color_active: app.md3_error
                text_color_normal: app.text_secondary

        BottomNavItem:
            id: nav_profile_item
            screen_name: "nav_profile"
            icon_name: "settings"
            label_text: "Ajustes"
            indicator_color: app.btn_primary

            MDNavigationItemIcon:
                icon: nav_profile_item.icon_name
                icon_color_active: app.btn_primary
                icon_color_normal: app.text_secondary
            MDNavigationItemLabel:
                text: nav_profile_item.label_text
                font_size: '12sp'
                text_color_active: app.btn_primary
                text_color_normal: app.text_secondary

    MDFloatLayout:
        id: sos_overlay
        theme_bg_color: "Custom"
        md_bg_color: app.sos_red
        opacity: 1 if app.sos_alert_active else 0
        disabled: not app.sos_alert_active
        size_hint: (1, 1) if app.sos_alert_active else (0, 0)
        pos_hint: {"x": 0, "y": 0}

        MDIcon:
            icon: "notifications_active"
            halign: "center"
            font_size: '72sp'
            theme_text_color: "Custom"
            text_color: app.md3_on_sos
            pos_hint: {"center_x": .5, "center_y": .82}

        MDLabel:
            text: "¡ALERTA SOS TRANSMITIDA!"
            halign: "center"
            font_style: "Headline"
            role: "small"
            adaptive_height: True
            theme_text_color: "Custom"
            text_color: app.md3_on_sos
            size_hint_x: .9
            pos_hint: {"center_x": .5, "center_y": .66}

        MDLabel:
            text: "Coordenadas GPS enviadas a la patrulla policial y a tus contactos de emergencia."
            halign: "center"
            font_style: "Body"
            role: "medium"
            adaptive_height: True
            theme_text_color: "Custom"
            text_color: app.md3_on_sos
            size_hint_x: .9
            pos_hint: {"center_x": .5, "center_y": .54}

        MDButton:
            style: "filled"
            theme_bg_color: "Custom"
            theme_width: "Custom"
            md_bg_color: app.md3_on_sos
            size_hint: .8, None
            height: '52dp'
            pos_hint: {"center_x": .5, "center_y": .34}
            radius: [100, 100, 100, 100]
            on_release: app.confirm_cancel_sos_alert()

            MDButtonText:
                text: "DESACTIVAR ALERTA SOS"
                theme_text_color: "Custom"
                text_color: app.md3_sos

# ==========================================================================
# CÁMARAS
# ==========================================================================
<CamerasScreen@MDScreen>:
    md_bg_color: app.bg_main

    MDNavigationLayout:
        id: camera_nav_layout
        size_hint: None, None
        size: self.parent.size if self.parent else (dp(1), dp(1))

        MDScreenManager:
            id: camera_content_manager

            MDScreen:
                name: "cameras_content"

                MDBoxLayout:
                    orientation: 'vertical'

                    MDTopAppBar:
                        type: "small"
                        md_bg_color: app.bg_main
                        theme_bg_color: "Custom"
                        elevation: 0

                        MDTopAppBarLeadingButtonContainer:
                            MDActionTopAppBarButton:
                                icon: "menu"
                                theme_icon_color: "Custom"
                                icon_color: app.text_primary
                                on_release: app.open_nav_drawer()

                        MDTopAppBarTitle:
                            text: "Mis cámaras"
                            theme_text_color: "Custom"
                            text_color: app.text_primary

                        MDTopAppBarTrailingButtonContainer:
                            MDActionTopAppBarButton:
                                icon: "warning"
                                theme_icon_color: "Custom"
                                icon_color: app.md3_error
                                on_release: app.drawer_sos()

                    MDScrollView:
                        do_scroll_x: False

                        MDBoxLayout:
                            orientation: 'vertical'
                            padding: ['20dp', '20dp', '20dp', '28dp']
                            spacing: '14dp'
                            adaptive_height: True

                            MDBoxLayout:
                                adaptive_height: True
                                spacing: '8dp'

                                MDButton:
                                    style: "filled" if app.camera_filter == 'all' else "tonal"
                                    theme_bg_color: "Custom"
                                    theme_width: "Custom"
                                    md_bg_color: app.btn_primary if app.camera_filter == 'all' else app.bg_card
                                    size_hint_x: 1/3
                                    size_hint_y: None
                                    height: '44dp'
                                    on_release: app.set_camera_filter('all')

                                    MDButtonText:
                                        text: "Todas (3)"
                                        font_size: '12sp'
                                        theme_text_color: "Custom"
                                        text_color: app.md3_on_primary if app.camera_filter == 'all' else app.text_primary

                                MDButton:
                                    style: "filled" if app.camera_filter == 'online' else "tonal"
                                    theme_bg_color: "Custom"
                                    theme_width: "Custom"
                                    md_bg_color: app.btn_primary if app.camera_filter == 'online' else app.bg_card
                                    size_hint_x: 1/3
                                    size_hint_y: None
                                    height: '44dp'
                                    on_release: app.set_camera_filter('online')

                                    MDButtonText:
                                        text: "En línea (2)"
                                        font_size: '12sp'
                                        theme_text_color: "Custom"
                                        text_color: app.md3_on_primary if app.camera_filter == 'online' else app.text_primary

                                MDButton:
                                    style: "filled" if app.camera_filter == 'recording' else "tonal"
                                    theme_bg_color: "Custom"
                                    theme_width: "Custom"
                                    md_bg_color: app.btn_primary if app.camera_filter == 'recording' else app.bg_card
                                    size_hint_x: 1/3
                                    size_hint_y: None
                                    height: '44dp'
                                    on_release: app.set_camera_filter('recording')

                                    MDButtonText:
                                        text: "Grabando (1)"
                                        font_size: '12sp'
                                        theme_text_color: "Custom"
                                        text_color: app.md3_on_primary if app.camera_filter == 'recording' else app.text_primary

                            MDCard:
                                orientation: 'vertical'
                                size_hint_y: None
                                height: dp(205) if app.camera_filter in ('all', 'online') else 0
                                opacity: 1 if app.camera_filter in ('all', 'online') else 0
                                disabled: app.camera_filter not in ('all', 'online')
                                theme_bg_color: "Custom"
                                md_bg_color: app.bg_card
                                radius: [20, 20, 20, 20]
                                padding: '12dp' if app.camera_filter in ('all', 'online') else 0
                                spacing: '8dp'

                                MDBoxLayout:
                                    orientation: 'vertical'
                                    theme_bg_color: "Custom"
                                    md_bg_color: app.bg_input_nav
                                    radius: [14, 14, 14, 14]
                                    padding: '10dp'
                                    MDLabel:
                                        text: "EN LÍNEA • CAM 01"
                                        font_style: "Label"
                                        role: "large"
                                        adaptive_height: True
                                        theme_text_color: "Custom"
                                        text_color: app.accent_cyan
                                    MDIcon:
                                        icon: "videocam"
                                        halign: "center"
                                        font_size: '42sp'
                                        theme_text_color: "Custom"
                                        text_color: app.border_input

                                MDBoxLayout:
                                    adaptive_height: True
                                    MDBoxLayout:
                                        orientation: 'vertical'
                                        adaptive_height: True
                                        MDLabel:
                                            text: "Entrada principal"
                                            font_style: "Title"
                                            role: "medium"
                                            adaptive_height: True
                                            theme_text_color: "Custom"
                                            text_color: app.text_primary
                                        MDLabel:
                                            text: "Resolución 1080p • 30fps"
                                            font_style: "Body"
                                            role: "small"
                                            adaptive_height: True
                                            theme_text_color: "Custom"
                                            text_color: app.text_secondary
                                    MDIconButton:
                                        icon: "fullscreen"
                                        theme_icon_color: "Custom"
                                        icon_color: app.accent_cyan
                                        on_release: app.show_snackbar("Maximizando Entrada Principal")

                            MDCard:
                                orientation: 'vertical'
                                size_hint_y: None
                                height: dp(205) if app.camera_filter in ('all', 'online') else 0
                                opacity: 1 if app.camera_filter in ('all', 'online') else 0
                                disabled: app.camera_filter not in ('all', 'online')
                                theme_bg_color: "Custom"
                                md_bg_color: app.bg_card
                                radius: [20, 20, 20, 20]
                                padding: '12dp' if app.camera_filter in ('all', 'online') else 0
                                spacing: '8dp'

                                MDBoxLayout:
                                    orientation: 'vertical'
                                    theme_bg_color: "Custom"
                                    md_bg_color: app.bg_input_nav
                                    radius: [14, 14, 14, 14]
                                    padding: '10dp'
                                    MDLabel:
                                        text: "EN LÍNEA • CAM 02"
                                        font_style: "Label"
                                        role: "large"
                                        adaptive_height: True
                                        theme_text_color: "Custom"
                                        text_color: app.accent_cyan
                                    MDIcon:
                                        icon: "park"
                                        halign: "center"
                                        font_size: '42sp'
                                        theme_text_color: "Custom"
                                        text_color: app.border_input

                                MDBoxLayout:
                                    adaptive_height: True
                                    MDBoxLayout:
                                        orientation: 'vertical'
                                        adaptive_height: True
                                        MDLabel:
                                            text: "Patio trasero"
                                            font_style: "Title"
                                            role: "medium"
                                            adaptive_height: True
                                            theme_text_color: "Custom"
                                            text_color: app.text_primary
                                        MDLabel:
                                            text: "Visión nocturna infrarroja activa"
                                            font_style: "Body"
                                            role: "small"
                                            adaptive_height: True
                                            theme_text_color: "Custom"
                                            text_color: app.text_secondary
                                    MDIconButton:
                                        icon: "fullscreen"
                                        theme_icon_color: "Custom"
                                        icon_color: app.accent_cyan
                                        on_release: app.show_snackbar("Maximizando Patio Trasero")

                            MDCard:
                                orientation: 'vertical'
                                size_hint_y: None
                                height: dp(205) if app.camera_filter in ('all', 'recording') else 0
                                opacity: 1 if app.camera_filter in ('all', 'recording') else 0
                                disabled: app.camera_filter not in ('all', 'recording')
                                theme_bg_color: "Custom"
                                md_bg_color: app.bg_card
                                radius: [20, 20, 20, 20]
                                padding: '12dp' if app.camera_filter in ('all', 'recording') else 0
                                spacing: '8dp'

                                MDBoxLayout:
                                    orientation: 'vertical'
                                    theme_bg_color: "Custom"
                                    md_bg_color: app.bg_input_nav
                                    radius: [14, 14, 14, 14]
                                    padding: '10dp'
                                    MDLabel:
                                        text: "REC • CAM 03 • GRABANDO"
                                        font_style: "Label"
                                        role: "large"
                                        adaptive_height: True
                                        theme_text_color: "Custom"
                                        text_color: app.md3_error
                                    MDIcon:
                                        icon: "garage"
                                        halign: "center"
                                        font_size: '42sp'
                                        theme_text_color: "Custom"
                                        text_color: app.border_input

                                MDBoxLayout:
                                    adaptive_height: True
                                    MDBoxLayout:
                                        orientation: 'vertical'
                                        adaptive_height: True
                                        MDLabel:
                                            text: "Garaje vehicular"
                                            font_style: "Title"
                                            role: "medium"
                                            adaptive_height: True
                                            theme_text_color: "Custom"
                                            text_color: app.text_primary
                                        MDLabel:
                                            text: "Detección de movimiento activada"
                                            font_style: "Body"
                                            role: "small"
                                            adaptive_height: True
                                            theme_text_color: "Custom"
                                            text_color: app.text_secondary
                                    MDIconButton:
                                        icon: "fullscreen"
                                        theme_icon_color: "Custom"
                                        icon_color: app.accent_cyan
                                        on_release: app.show_snackbar("Maximizando Garaje")

                            MDButton:
                                style: "filled"
                                theme_bg_color: "Custom"
                                theme_width: "Custom"
                                md_bg_color: app.btn_primary
                                size_hint_x: 1
                                size_hint_y: None
                                height: '52dp'
                                radius: [100, 100, 100, 100]
                                on_release: app.show_snackbar("Buscando cámaras en la red Wi-Fi...")

                                MDButtonText:
                                    text: "+ AÑADIR CÁMARA"
                                    theme_text_color: "Custom"
                                    text_color: app.md3_on_primary

        AppNavigationDrawer:
            id: camera_drawer
'''


class ExpressiveApp(MDApp):
    """Aplicación M3 con autenticación, SOS y cámaras."""

    # Paleta original VIGÍA SOS restaurada (rojos vívidos y cian/azul originales).
    # Los tokens M3 se conservan para los componentes KivyMD 2.0.0, pero apuntan
    # exactamente a los colores que tenía la app antes de la migración.
    md3_primary = ColorProperty(get_color_from_hex('#D32F2F'))
    md3_on_primary = ColorProperty(get_color_from_hex('#FFFFFF'))
    md3_primary_container = ColorProperty(get_color_from_hex('#4D0008'))
    md3_on_primary_container = ColorProperty(get_color_from_hex('#FFFFFF'))
    md3_secondary = ColorProperty(get_color_from_hex('#00F2FE'))
    md3_on_secondary = ColorProperty(get_color_from_hex('#0A0E24'))
    md3_secondary_container = ColorProperty(get_color_from_hex('#141A38'))
    md3_on_secondary_container = ColorProperty(get_color_from_hex('#00F2FE'))
    md3_tertiary = ColorProperty(get_color_from_hex('#2563EB'))
    md3_on_tertiary = ColorProperty(get_color_from_hex('#FFFFFF'))
    md3_tertiary_container = ColorProperty(get_color_from_hex('#2563EB'))
    md3_on_tertiary_container = ColorProperty(get_color_from_hex('#FFFFFF'))
    md3_background = ColorProperty(get_color_from_hex('#0A0E24'))
    md3_on_background = ColorProperty(get_color_from_hex('#FFFFFF'))
    md3_surface = ColorProperty(get_color_from_hex('#1E2750'))
    md3_on_surface = ColorProperty(get_color_from_hex('#FFFFFF'))
    md3_surface_variant = ColorProperty(get_color_from_hex('#141A38'))
    md3_on_surface_variant = ColorProperty(get_color_from_hex('#A0B0D8'))
    md3_surface_container = ColorProperty(get_color_from_hex('#1E2750'))
    md3_outline = ColorProperty(get_color_from_hex('#384878'))
    md3_error = ColorProperty(get_color_from_hex('#FF2D55'))
    md3_on_error = ColorProperty(get_color_from_hex('#FFFFFF'))
    md3_error_container = ColorProperty(get_color_from_hex('#431D78'))
    md3_on_error_container = ColorProperty(get_color_from_hex('#00F2FE'))
    md3_sos = ColorProperty(get_color_from_hex('#FF2D55'))
    md3_on_sos = ColorProperty(get_color_from_hex('#FFFFFF'))

    # Alias originales usados por el KV
    bg_main = ColorProperty(get_color_from_hex('#0A0E24'))
    bg_input_nav = ColorProperty(get_color_from_hex('#141A38'))
    bg_card = ColorProperty(get_color_from_hex('#1E2750'))
    border_input = ColorProperty(get_color_from_hex('#384878'))
    text_primary = ColorProperty(get_color_from_hex('#FFFFFF'))
    text_secondary = ColorProperty(get_color_from_hex('#A0B0D8'))
    accent_cyan = ColorProperty(get_color_from_hex('#00F2FE'))
    btn_primary = ColorProperty(get_color_from_hex('#FF2D55'))
    zone_alert = ColorProperty(get_color_from_hex('#431D78'))
    sos_red = ColorProperty(get_color_from_hex('#FF2D55'))
    action_blue = ColorProperty(get_color_from_hex('#2563EB'))

    auth_tab = StringProperty('login')
    user_name = StringProperty('Usuario')
    user_phone_display = StringProperty('Sin registrar')
    camera_filter = StringProperty('all')
    new_contact_type = StringProperty('other')
    current_user_id = NumericProperty(0)
    current_user_email = StringProperty('')
    current_user_role = StringProperty('')

    sos_progress = NumericProperty(0.0)
    sos_status_text = StringProperty('Mantén pulsado 3 segundos')
    sos_alert_active = BooleanProperty(False)
    sos_scale = NumericProperty(1.0)
    live_beacon_alpha = NumericProperty(1.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._sos_event = None
        self._sos_elapsed = 0.0
        self._deactivate_dialog = None

    def build(self):
        self.title = "Seguridad SOS - Material Design 3 (Vigía DB)"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Pink"
        Window.bind(on_keyboard=self.on_back_key)
        print(
            f"[Vigía vista] {'Escritorio/Web' if VIEW_MODE == 'desktop' else 'Móvil'} "
            f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]} (F9 cambia el tamaño)"
        )

        try:
            ok, msg = db_manager.test_db_connection()
            print(f"[Vigía PostgreSQL] {msg}" if ok else f"[Vigía PostgreSQL Aviso] {msg}")
        except Exception as e:
            print(f"[Vigía PostgreSQL Error]: {e}")

        root = Builder.load_string(KV)
        root.transition = CardTransition(direction='left', mode='push', duration=0.36)
        root.bind(size=lambda *args: self.sync_screen_sizes())
        Clock.schedule_once(lambda dt: self.sync_screen_sizes(), 0)
        return root

    def sync_screen_sizes(self, *args):
        """Mantiene cada MDScreen a tamaño completo para que el drawer mida bien."""
        if not self.root:
            return
        target = self.root.size
        for screen in self.root.screens:
            if tuple(screen.size) != tuple(target):
                screen.size = target

    def on_start(self):
        sos_breathing = (
            Animation(sos_scale=1.03, duration=1.6, t='in_out_sine') +
            Animation(sos_scale=1.0, duration=1.6, t='in_out_sine')
        )
        sos_breathing.repeat = True
        sos_breathing.start(self)

        beacon_breathing = (
            Animation(live_beacon_alpha=0.35, duration=1.0, t='in_out_quad') +
            Animation(live_beacon_alpha=1.0, duration=1.0, t='in_out_quad')
        )
        beacon_breathing.repeat = True
        beacon_breathing.start(self)

    # ------------------------------------------------------------------ nav
    def navigate_to(self, screen_name, direction='left'):
        if not self.root or self.root.current == screen_name:
            return
        mode = 'push' if direction == 'left' else 'pop'
        self.root.transition = CardTransition(direction=direction, mode=mode, duration=0.36)
        self.root.current = screen_name

    def open_nav_drawer(self):
        if not self.root:
            return
        screen = self.root.get_screen(self.root.current)
        drawer = screen.ids.get('main_drawer') or screen.ids.get('camera_drawer')
        if drawer:
            drawer.set_state('open')

    def close_nav_drawer(self):
        if not self.root:
            return
        for screen_name in ('main', 'cameras'):
            screen = self.root.get_screen(screen_name)
            drawer = screen.ids.get('main_drawer') or screen.ids.get('camera_drawer')
            if drawer and drawer.state == 'open':
                drawer.set_state('close')

    def is_drawer_open(self):
        if not self.root:
            return False
        for screen_name in ('main', 'cameras'):
            screen = self.root.get_screen(screen_name)
            drawer = screen.ids.get('main_drawer') or screen.ids.get('camera_drawer')
            if drawer and drawer.state == 'open':
                return True
        return False

    def drawer_navigate(self, screen_name, tab_name=None):
        self.close_nav_drawer()
        if tab_name:
            self.switch_main_tab(tab_name)
        self.navigate_to(screen_name)

    def drawer_sos(self):
        # Cierre inmediato para que el overlay de alerta nunca quede tapado.
        if self.root:
            for screen_name in ('main', 'cameras'):
                screen = self.root.get_screen(screen_name)
                drawer = screen.ids.get('main_drawer') or screen.ids.get('camera_drawer')
                if drawer:
                    drawer.set_state('close', animation=False)
        self.switch_main_tab('nav_sos')
        self.navigate_to('main')
        self.activate_sos_overlay()

    def switch_main_tab(self, tab_name):
        if not self.root:
            return
        main_screen = self.root.get_screen('main')
        main_screen.ids.main_tabs.current = tab_name
        bar = main_screen.ids.bottom_nav
        for item in bar.children:
            if getattr(item, 'screen_name', None) == tab_name:
                bar.set_active_item(item)
                break

    def on_main_tab_switched(self, bar, item, item_icon, item_text):
        tab_name = getattr(item, 'screen_name', None)
        if tab_name and self.root:
            self.root.get_screen('main').ids.main_tabs.current = tab_name
            if tab_name == 'nav_contacts':
                Clock.schedule_once(lambda dt: self.refresh_emergency_contacts(), 0)

    def set_new_contact_type(self, contact_type):
        self.new_contact_type = contact_type

    @staticmethod
    def contact_type_icon(contact_type):
        return {
            'police': 'police-badge',
            'firefighter': 'fire-truck',
            'medical': 'medical-bag',
        }.get(contact_type, 'account')

    @staticmethod
    def contact_type_label(contact_type):
        return {
            'police': 'Policía',
            'firefighter': 'Bomberos',
            'medical': 'Médico',
            'other': 'Otro',
        }.get(contact_type, 'Otro')

    def refresh_emergency_contacts(self, *args):
        """Pinta los contactos reales guardados en PostgreSQL."""
        if not self.root:
            return
        main_screen = self.root.get_screen('main')
        if 'contacts_list' not in main_screen.ids:
            return

        container = main_screen.ids.contacts_list
        container.clear_widgets()
        try:
            contacts = db_manager.get_emergency_contacts()
        except Exception:
            traceback.print_exc()
            contacts = []

        main_screen.ids.contacts_list_title.text = (
            f"Contactos registrados ({len(contacts)})"
        )

        if not contacts:
            container.add_widget(MDLabel(
                text="Aún no hay contactos configurados. Agrega el primero abajo.",
                font_style="Body",
                role="small",
                adaptive_height=True,
                theme_text_color="Custom",
                text_color=self.text_secondary,
            ))
            return

        for contact in contacts:
            contact_type = contact.get('contact_type') or 'other'
            row = MDBoxLayout(
                orientation="horizontal",
                adaptive_height=True,
                spacing=dp(12),
                padding=(0, dp(6)),
            )
            row.add_widget(MDIcon(
                icon=self.contact_type_icon(contact_type),
                theme_text_color="Custom",
                text_color=self.accent_cyan,
            ))

            info = MDBoxLayout(orientation="vertical", adaptive_height=True)
            info.add_widget(MDLabel(
                text=contact.get('name') or 'Sin nombre',
                bold=True,
                adaptive_height=True,
                theme_text_color="Custom",
                text_color=self.text_primary,
            ))
            phone = contact.get('phone') or 'Sin teléfono'
            info.add_widget(MDLabel(
                text=f"{self.contact_type_label(contact_type)} · {phone}",
                font_style="Body",
                role="small",
                adaptive_height=True,
                theme_text_color="Custom",
                text_color=self.text_secondary,
            ))
            row.add_widget(info)
            container.add_widget(row)

    def add_emergency_contact_from_form(self):
        if not self.root:
            return
        main_screen = self.root.get_screen('main')
        name = main_screen.ids.contact_name.text.strip()
        phone = main_screen.ids.contact_phone.text.strip()

        if not name or not phone:
            self.show_snackbar("Completa el nombre y el teléfono del contacto.")
            return

        try:
            ok, msg = db_manager.add_emergency_contact(
                name, self.new_contact_type, phone
            )
        except Exception:
            traceback.print_exc()
            self.show_snackbar("No se pudo guardar el contacto.")
            return

        self.show_snackbar(msg)
        if ok:
            main_screen.ids.contact_name.text = ""
            main_screen.ids.contact_phone.text = ""
            self.refresh_emergency_contacts()

    def set_view_mode(self, mode):
        """Cambia entre tamaño escritorio y móvil en caliente."""
        global VIEW_MODE, WINDOW_SIZE
        VIEW_MODE = "desktop" if str(mode).lower() in ("desktop", "web") else "mobile"
        WINDOW_SIZE = DESKTOP_WINDOW_SIZE if VIEW_MODE == "desktop" else MOBILE_WINDOW_SIZE

        if platform in ("win", "linux", "macosx"):
            Window.size = WINDOW_SIZE

        etiqueta = "Escritorio/Web" if VIEW_MODE == "desktop" else "Móvil"
        self.show_snackbar(f"Vista {etiqueta}: {WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")

    def on_back_key(self, window, key, *args):
        if key == 290:  # F9: alternar tamaño escritorio/móvil
            self.set_view_mode("mobile" if VIEW_MODE == "desktop" else "desktop")
            return True
        if key != 27:
            return False
        if self.is_drawer_open():
            self.close_nav_drawer()
            return True
        if self.sos_alert_active:
            self.cancel_sos_alert()
            return True
        current = self.root.current if self.root else None
        if current == 'cameras':
            self.navigate_to('main', direction='right')
            return True
        if current == 'main':
            self.switch_main_tab('nav_home')
            return True
        return False

    # -------------------------------------------------------------- feedback
    def show_snackbar(self, message, bg_color=None):
        Clock.schedule_once(lambda dt: self._open_snackbar(message, bg_color), 0.15)

    def _open_snackbar(self, message, bg_color=None):
        color = bg_color if bg_color is not None else self.md3_error_container
        try:
            MDSnackbar(
                MDSnackbarText(
                    text=message,
                    theme_text_color="Custom",
                    text_color=self.md3_on_error_container,
                ),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.9,
                background_color=color,
            ).open()
        except Exception as e:
            print(f"[Aviso]: {message} ({e})")

    # ------------------------------------------------------------------ auth
    def set_auth_tab(self, tab):
        self.auth_tab = tab

    def set_camera_filter(self, filter_name):
        self.camera_filter = filter_name

    def process_auth_submit(self):
        auth_screen = self.root.get_screen('auth')

        try:
            if self.auth_tab == 'register':
                name = auth_screen.ids.reg_name.text.strip()
                phone = auth_screen.ids.reg_phone.text.strip()
                email = auth_screen.ids.reg_email.text.strip()
                password = auth_screen.ids.reg_password.text.strip()

                if not name:
                    self.show_snackbar("Por favor escribe tu nombre completo.")
                    return
                if not phone:
                    self.show_snackbar("Por favor escribe tu teléfono móvil.")
                    return
                if not email:
                    self.show_snackbar("Por favor escribe tu correo electrónico.")
                    return
                if not password:
                    self.show_snackbar("Por favor ingresa una contraseña.")
                    return

                success, message, user_data = db_manager.register_user(name, email, phone, password)
                if not success:
                    self.show_snackbar(message)
                    return

                self.current_user_id = user_data['id']
                self.user_name = user_data['name']
                self.user_phone_display = user_data.get('phone') or user_data.get('email')
                self.current_user_email = user_data.get('email', '')
                self.current_user_role = user_data.get('role', 'viewer')
                auth_screen.ids.reg_password.text = ""
            else:
                email = auth_screen.ids.login_email.text.strip()
                password = auth_screen.ids.login_password.text.strip()

                if not email:
                    self.show_snackbar("Por favor escribe tu correo electrónico.")
                    return
                if not password:
                    self.show_snackbar("Por favor ingresa tu contraseña.")
                    return

                success, message, user_data = db_manager.login_user(email, password)
                if not success:
                    self.show_snackbar(message)
                    return

                self.current_user_id = user_data['id']
                self.user_name = user_data['name']
                self.user_phone_display = user_data.get('phone') or user_data.get('email')
                self.current_user_email = user_data.get('email', '')
                self.current_user_role = user_data.get('role', 'viewer')
                auth_screen.ids.login_password.text = ""

            self.switch_main_tab('nav_home')
            self.navigate_to('main', direction='left')
            self.show_snackbar(message)
        except Exception:
            traceback.print_exc()
            self.show_snackbar("Error de conexión con la base de datos.")

    # ------------------------------------------------------------------- SOS
    def start_sos_hold(self):
        self.cancel_sos_hold()
        self._sos_elapsed = 0.0
        self.sos_progress = 0.0
        self.sos_scale = 0.95
        self.sos_status_text = "¡ENVIANDO ALERTA EN 3s!"
        self._sos_event = Clock.schedule_interval(self._update_sos_hold, 0.05)

    def _update_sos_hold(self, dt):
        self._sos_elapsed += dt
        self.sos_progress = min(self._sos_elapsed / 3.0, 1.0)
        remaining = max(1, int(3 - self._sos_elapsed) + 1)
        self.sos_status_text = f"¡ENVIANDO ALERTA EN {remaining}s!"
        if self._sos_elapsed >= 3.0:
            self.cancel_sos_hold()
            self.activate_sos_overlay()

    def cancel_sos_hold(self):
        if self._sos_event is not None:
            self._sos_event.cancel()
            self._sos_event = None
        self._sos_elapsed = 0.0
        self.sos_progress = 0.0
        self.sos_scale = 1.0
        self.sos_status_text = "Mantén pulsado 3 segundos"

    def activate_sos_overlay(self):
        self.cancel_sos_hold()
        self.sos_alert_active = True
        try:
            if self.current_user_id:
                db_manager.record_sos_alert(self.current_user_id)
        except Exception:
            traceback.print_exc()
        self.show_snackbar("Alerta SOS transmitida a emergencias.")

    def confirm_cancel_sos_alert(self):
        """Pide confirmación antes de dar por terminada la alerta SOS."""
        if self._deactivate_dialog is None:
            dialog = MDDialog(
                MDDialogHeadlineText(
                    text="¿Desactivar la alerta SOS?",
                    theme_text_color="Custom",
                    text_color=self.text_primary,
                ),
                MDDialogSupportingText(
                    text="La alerta dejará de transmitirse a emergencias.",
                    theme_text_color="Custom",
                    text_color=self.text_secondary,
                ),
                MDDialogButtonContainer(
                    Widget(),
                    MDButton(
                        MDButtonText(text="Cancelar"),
                        style="text",
                        on_release=lambda *args: dialog.dismiss(),
                    ),
                    MDButton(
                        MDButtonText(
                            text="Desactivar",
                            theme_text_color="Custom",
                            text_color=self.md3_on_sos,
                        ),
                        style="filled",
                        theme_bg_color="Custom",
                        md_bg_color=self.sos_red,
                        on_release=lambda *args: self._confirm_deactivate_sos(dialog),
                    ),
                    spacing="8dp",
                ),
                theme_bg_color="Custom",
                md_bg_color=self.bg_card,
            )
            self._deactivate_dialog = dialog

        if not self._deactivate_dialog._is_open:
            self._deactivate_dialog.open()

    def _confirm_deactivate_sos(self, dialog):
        dialog.dismiss()
        self.cancel_sos_alert()

    def cancel_sos_alert(self):
        self.sos_alert_active = False
        self.show_snackbar("Alerta SOS desactivada.")

    def logout(self):
        self.cancel_sos_hold()
        self.sos_alert_active = False
        self.current_user_id = 0
        self.current_user_email = ""
        self.current_user_role = ""
        self.user_name = "Usuario"
        self.user_phone_display = "Sin registrar"
        self.new_contact_type = 'other'
        auth_screen = self.root.get_screen('auth')
        if 'login_password' in auth_screen.ids:
            auth_screen.ids.login_password.text = ""
        self.switch_main_tab('nav_home')
        self.navigate_to('auth', direction='right')
        self.show_snackbar("Has cerrado sesión con éxito.")


if __name__ == '__main__':
    ExpressiveApp().run()
