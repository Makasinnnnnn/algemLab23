import math
import sys

import numpy as np

try:
    import pygame
    from pygame.locals import (
        DOUBLEBUF,
        K_a,
        K_d,
        K_DOWN,
        K_e,
        K_ESCAPE,
        K_LEFT,
        K_q,
        K_r,
        K_RIGHT,
        K_s,
        K_SPACE,
        K_UP,
        K_w,
        MOUSEWHEEL,
        OPENGL,
        QUIT,
        RESIZABLE,
        VIDEORESIZE,
    )
    from OpenGL.GL import *
    from OpenGL.GLU import *
except ModuleNotFoundError as error:
    print("Не найдена зависимость:", error.name)
    print("Установите зависимости командой:")
    print("pip install pygame PyOpenGL PyOpenGL_accelerate numpy")
    raise SystemExit(1)


class Dice3DApp:
    """Интерактивное 3D-приложение для отображения шестигранного кубика."""

    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.width = 1200
        self.height = 800
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            DOUBLEBUF | OPENGL | RESIZABLE,
        )
        pygame.display.set_caption("Лабораторная работа №4 — 3D кубик")

        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("Segoe UI", 18)
        self.small_font = pygame.font.SysFont("Segoe UI", 15)

        self.vertices = np.array(
            [
                (-1, -1, -1),
                (1, -1, -1),
                (1, 1, -1),
                (-1, 1, -1),
                (-1, -1, 1),
                (1, -1, 1),
                (1, 1, 1),
                (-1, 1, 1),
            ],
            dtype=float,
        )

        self.faces = [
            {
                "id": 1,
                "name": "front",
                "indices": (4, 5, 6, 7),
                "normal": (0, 0, 1),
                "color": (0.94, 0.26, 0.31),
            },
            {
                "id": 2,
                "name": "back",
                "indices": (1, 0, 3, 2),
                "normal": (0, 0, -1),
                "color": (0.20, 0.63, 0.96),
            },
            {
                "id": 3,
                "name": "left",
                "indices": (0, 4, 7, 3),
                "normal": (-1, 0, 0),
                "color": (0.22, 0.78, 0.42),
            },
            {
                "id": 4,
                "name": "right",
                "indices": (5, 1, 2, 6),
                "normal": (1, 0, 0),
                "color": (0.98, 0.70, 0.22),
            },
            {
                "id": 5,
                "name": "top",
                "indices": (3, 7, 6, 2),
                "normal": (0, 1, 0),
                "color": (0.61, 0.45, 0.96),
            },
            {
                "id": 6,
                "name": "bottom",
                "indices": (0, 1, 5, 4),
                "normal": (0, -1, 0),
                "color": (0.16, 0.82, 0.77),
            },
        ]

        self.edges = (
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7),
        )

        self.reset_view()
        self.setup_opengl()

    def run(self):
        """Запускает главный цикл приложения."""
        while self.running:
            delta_time = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(delta_time)
            self.render()

        pygame.quit()

    def handle_events(self):
        """Обрабатывает клавиши, колесо мыши, изменение размера и выход."""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == VIDEORESIZE:
                self.resize_window(event.w, event.h)
            elif event.type == MOUSEWHEEL:
                self.camera_distance += event.y * 0.35
                self.camera_distance = min(-2.6, max(-14.0, self.camera_distance))
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_SPACE:
                    self.auto_rotate = not self.auto_rotate
                elif event.key == K_r:
                    self.reset_view()

    def update(self, delta_time):
        """Обновляет углы поворота и автоповорот."""
        keys = pygame.key.get_pressed()
        rotation_speed = 85.0 * delta_time

        if keys[K_w] or keys[K_UP]:
            self.angle_x += rotation_speed
        if keys[K_s] or keys[K_DOWN]:
            self.angle_x -= rotation_speed
        if keys[K_a] or keys[K_LEFT]:
            self.angle_y -= rotation_speed
        if keys[K_d] or keys[K_RIGHT]:
            self.angle_y += rotation_speed
        if keys[K_q]:
            self.angle_z -= rotation_speed
        if keys[K_e]:
            self.angle_z += rotation_speed

        if self.auto_rotate:
            self.angle_x += 8.0 * delta_time
            self.angle_y += 24.0 * delta_time
            self.angle_z += 10.0 * delta_time

        self.angle_x %= 360
        self.angle_y %= 360
        self.angle_z %= 360

    def render(self):
        """Выполняет полную отрисовку 3D-сцены и 2D-интерфейса."""
        glViewport(0, 0, self.width, self.height)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, self.width / max(self.height, 1), 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, self.camera_distance)
        glRotatef(self.angle_x, 1.0, 0.0, 0.0)
        glRotatef(self.angle_y, 0.0, 1.0, 0.0)
        glRotatef(self.angle_z, 0.0, 0.0, 1.0)

        self.draw_grid()
        self.draw_cube()
        self.draw_cube_edges()
        self.draw_face_markers()
        self.draw_ui_text()

        pygame.display.flip()

    def setup_opengl(self):
        """Настраивает OpenGL: перспективу, глубину, сглаживание и свет."""
        glViewport(0, 0, self.width, self.height)
        glClearColor(0.035, 0.045, 0.065, 1.0)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glShadeModel(GL_SMOOTH)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        glLightfv(GL_LIGHT0, GL_POSITION, (3.5, 4.0, 5.0, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.95, 0.95, 0.88, 1.0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (0.55, 0.55, 0.55, 1.0))

        glLightfv(GL_LIGHT1, GL_POSITION, (-4.0, 2.5, -3.0, 1.0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.22, 0.30, 0.45, 1.0))

        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.35, 0.35, 0.35, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 32.0)

    def draw_cube(self):
        """Рисует цветные грани куба по индексам вершин."""
        glEnable(GL_LIGHTING)
        glBegin(GL_QUADS)

        for face in self.faces:
            glColor3f(*face["color"])
            glNormal3f(*face["normal"])
            for vertex_index in face["indices"]:
                glVertex3f(*self.vertices[vertex_index])

        glEnd()

    def draw_cube_edges(self):
        """Рисует тёмные контуры рёбер кубика."""
        glDisable(GL_LIGHTING)
        glColor3f(0.015, 0.018, 0.024)
        glLineWidth(4.0)

        glBegin(GL_LINES)
        for start, end in self.edges:
            glVertex3f(*self.vertices[start])
            glVertex3f(*self.vertices[end])
        glEnd()

        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    def draw_face_markers(self):
        """Рисует метки на всех гранях куба."""
        glDisable(GL_LIGHTING)
        glDisable(GL_CULL_FACE)
        glColor3f(0.02, 0.025, 0.035)

        for face in self.faces:
            self.draw_marker_for_face(face["id"])

        glEnable(GL_LIGHTING)

    def draw_marker_for_face(self, face_id):
        """Поворачивает локальную плоскость и рисует метку конкретной грани."""
        transforms = {
            1: ((0.0, 0.0, 1.015), (0.0, 0.0, 0.0, 1.0)),
            2: ((0.0, 0.0, -1.015), (180.0, 0.0, 1.0, 0.0)),
            3: ((-1.015, 0.0, 0.0), (-90.0, 0.0, 1.0, 0.0)),
            4: ((1.015, 0.0, 0.0), (90.0, 0.0, 1.0, 0.0)),
            5: ((0.0, 1.015, 0.0), (-90.0, 1.0, 0.0, 0.0)),
            6: ((0.0, -1.015, 0.0), (90.0, 1.0, 0.0, 0.0)),
        }

        translation, rotation = transforms[face_id]
        glPushMatrix()
        glTranslatef(*translation)
        glRotatef(*rotation)

        if face_id == 1:
            self.draw_pips(1)
        elif face_id == 2:
            self.draw_pips(2)
        elif face_id == 3:
            self.draw_triangle_2d(0.0, 0.0, 1.05)
        elif face_id == 4:
            self.draw_square_2d(0.0, 0.0, 0.85)
        elif face_id == 5:
            self.draw_cross_2d(0.0, 0.0, 0.82)
        elif face_id == 6:
            self.draw_pips(6)

        glPopMatrix()

    def draw_grid(self):
        """Рисует вспомогательную сетку под кубом."""
        glDisable(GL_LIGHTING)
        glColor4f(0.26, 0.34, 0.46, 0.38)
        glLineWidth(1.0)

        grid_size = 5
        step = 1.0
        y = -1.45

        glBegin(GL_LINES)
        for i in range(-grid_size, grid_size + 1):
            value = i * step
            glVertex3f(-grid_size, y, value)
            glVertex3f(grid_size, y, value)
            glVertex3f(value, y, -grid_size)
            glVertex3f(value, y, grid_size)
        glEnd()

        glEnable(GL_LIGHTING)

    def draw_ui_text(self):
        """Рисует подсказку и текущие параметры поверх 3D-сцены."""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.draw_panel_2d(18, 18, 375, 238)
        lines = [
            ("Лабораторная работа №4 — 3D кубик", True),
            ("W/S или ↑/↓ — поворот по X", False),
            ("A/D или ←/→ — поворот по Y", False),
            ("Q/E — поворот по Z", False),
            ("Mouse Wheel — zoom", False),
            ("Space — автоповорот", False),
            ("R — сброс вида, Esc — выход", False),
            (
                f"X: {self.angle_x:6.1f}°   Y: {self.angle_y:6.1f}°   Z: {self.angle_z:6.1f}°",
                False,
            ),
            (
                f"Zoom: {abs(self.camera_distance):.2f}   Auto rotate: {'ON' if self.auto_rotate else 'OFF'}",
                False,
            ),
            (f"FPS: {self.clock.get_fps():.0f}", False),
        ]

        y = 32
        for text, is_title in lines:
            font = self.font if is_title else self.small_font
            color = (245, 247, 250) if is_title else (200, 210, 225)
            self.draw_text_2d(text, 32, y, font=font, color=color)
            y += 25 if is_title else 21

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def reset_view(self):
        """Сбрасывает углы обзора и расстояние камеры."""
        self.angle_x = 25.0
        self.angle_y = -35.0
        self.angle_z = 0.0
        self.camera_distance = -6.0
        self.auto_rotate = True

    def draw_text_2d(self, text, x, y, font=None, color=(230, 235, 245)):
        """Рисует 2D-текст через Pygame Surface, превращённый в OpenGL texture."""
        if font is None:
            font = self.font

        surface = font.render(text, True, color)
        text_width, text_height = surface.get_size()
        texture_data = pygame.image.tostring(surface, "RGBA", True)
        texture_id = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            text_width,
            text_height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            texture_data,
        )

        glEnable(GL_TEXTURE_2D)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(x, y)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(x + text_width, y)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(x + text_width, y + text_height)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(x, y + text_height)
        glEnd()
        glDisable(GL_TEXTURE_2D)

        glDeleteTextures([texture_id])

    def draw_panel_2d(self, x, y, width, height):
        """Рисует полупрозрачную подложку для текста."""
        glDisable(GL_TEXTURE_2D)
        glColor4f(0.035, 0.045, 0.065, 0.76)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()

        glColor4f(0.28, 0.38, 0.52, 0.65)
        glLineWidth(1.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()

    def draw_circle_2d(self, x, y, radius, segments=40):
        """Рисует круг в текущей локальной 2D-плоскости грани."""
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(x, y, 0.0)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            glVertex3f(
                x + math.cos(angle) * radius,
                y + math.sin(angle) * radius,
                0.0,
            )
        glEnd()

    def draw_square_2d(self, x, y, size):
        """Рисует залитый квадрат на грани."""
        half = size / 2.0
        glBegin(GL_QUADS)
        glVertex3f(x - half, y - half, 0.0)
        glVertex3f(x + half, y - half, 0.0)
        glVertex3f(x + half, y + half, 0.0)
        glVertex3f(x - half, y + half, 0.0)
        glEnd()

    def draw_triangle_2d(self, x, y, size):
        """Рисует залитый треугольник на грани."""
        radius = size / 2.0
        glBegin(GL_TRIANGLES)
        for i in range(3):
            angle = math.radians(90 + i * 120)
            glVertex3f(
                x + math.cos(angle) * radius,
                y + math.sin(angle) * radius,
                0.0,
            )
        glEnd()

    def draw_cross_2d(self, x, y, size):
        """Рисует крест из двух толстых линий."""
        half = size / 2.0
        glLineWidth(10.0)
        glBegin(GL_LINES)
        glVertex3f(x - half, y - half, 0.0)
        glVertex3f(x + half, y + half, 0.0)
        glVertex3f(x - half, y + half, 0.0)
        glVertex3f(x + half, y - half, 0.0)
        glEnd()
        glLineWidth(1.0)

    def draw_pips(self, count):
        """Рисует точки как на игровой кости."""
        positions = {
            1: [(0.0, 0.0)],
            2: [(-0.36, 0.36), (0.36, -0.36)],
            6: [
                (-0.42, 0.48),
                (-0.42, 0.0),
                (-0.42, -0.48),
                (0.42, 0.48),
                (0.42, 0.0),
                (0.42, -0.48),
            ],
        }

        for x, y in positions.get(count, []):
            self.draw_circle_2d(x, y, 0.16)

    def resize_window(self, width, height):
        """Корректно обрабатывает изменение размера окна."""
        self.width = max(640, width)
        self.height = max(480, height)
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            DOUBLEBUF | OPENGL | RESIZABLE,
        )
        self.setup_opengl()


if __name__ == "__main__":
    app = Dice3DApp()
    app.run()
