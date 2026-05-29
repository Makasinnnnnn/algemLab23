import math
import tkinter as tk
from tkinter import ttk

import numpy as np


class PolygonTransformEditor:
    """Мини-графический редактор для преобразования многоугольника."""

    DEFAULT_VALUES = {
        "dx": "50",
        "dy": "50",
        "sx": "1.2",
        "sy": "1.2",
        "cx": "500",
        "cy": "350",
        "angle": "30",
    }

    BG_COLOR = "#151820"
    PANEL_COLOR = "#20242f"
    PANEL_DARK = "#171b24"
    CANVAS_COLOR = "#0b0f16"
    TEXT_COLOR = "#e5e7eb"
    MUTED_TEXT = "#9ca3af"
    LINE_COLOR = "#38bdf8"
    FILL_COLOR = "#123047"
    POINT_COLOR = "#fb923c"
    POINT_OUTLINE = "#fed7aa"
    CENTER_COLOR = "#facc15"
    AXIS_COLOR = "#64748b"
    GRID_COLOR = "#18202d"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Лабораторная работа №3 — Преобразование многоугольника")
        self.root.geometry("1200x750")
        self.root.minsize(980, 620)
        self.root.configure(bg=self.BG_COLOR)

        self.points = []
        self.is_closed = False
        self.history = []
        self.entries = {}
        self.view_scale = 1.0
        self.view_offset_x = 0.0
        self.view_offset_y = 0.0

        self.show_grid = tk.BooleanVar(value=True)
        self.show_fill = tk.BooleanVar(value=True)
        self.show_numbers = tk.BooleanVar(value=True)

        self.last_operation = tk.StringVar(value="Операция не выполнялась")
        self.vertex_count_text = tk.StringVar(value="Вершин: 0")
        self.closed_state_text = tk.StringVar(value="Состояние: не замкнут")
        self.mouse_position_text = tk.StringVar(value="Координаты: x=0, y=0")
        self.bounds_text = tk.StringVar(value="Границы: —")
        self.view_text = tk.StringVar(value="Вид: 100%, сдвиг (0, 0)")

        self.setup_styles()
        self.create_widgets()
        self.draw_scene()

    def run(self):
        """Запускает главный цикл приложения."""
        self.root.mainloop()

    def setup_styles(self):
        """Настраивает тёмные стили ttk."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Root.TFrame", background=self.BG_COLOR)
        style.configure("Panel.TFrame", background=self.PANEL_COLOR)
        style.configure("Section.TFrame", background=self.PANEL_COLOR)

        style.configure(
            "Title.TLabel",
            background=self.PANEL_COLOR,
            foreground=self.TEXT_COLOR,
            font=("Segoe UI", 15, "bold"),
        )
        style.configure(
            "Section.TLabel",
            background=self.PANEL_COLOR,
            foreground="#bfdbfe",
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "Hint.TLabel",
            background=self.PANEL_COLOR,
            foreground=self.MUTED_TEXT,
            font=("Segoe UI", 9),
            wraplength=260,
        )
        style.configure(
            "Info.TLabel",
            background=self.PANEL_COLOR,
            foreground=self.TEXT_COLOR,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Field.TLabel",
            background=self.PANEL_COLOR,
            foreground=self.TEXT_COLOR,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Status.TLabel",
            background=self.BG_COLOR,
            foreground=self.TEXT_COLOR,
            font=("Segoe UI", 10),
        )

        style.configure(
            "Dark.TEntry",
            fieldbackground="#111827",
            background="#111827",
            foreground=self.TEXT_COLOR,
            insertcolor=self.TEXT_COLOR,
            bordercolor="#374151",
            lightcolor="#374151",
            darkcolor="#374151",
            padding=5,
        )

        style.configure(
            "Dark.TButton",
            background="#2f3746",
            foreground=self.TEXT_COLOR,
            bordercolor="#4b5563",
            focusthickness=1,
            focuscolor="#60a5fa",
            padding=(9, 6),
            font=("Segoe UI", 9),
        )
        style.map(
            "Dark.TButton",
            background=[("active", "#3b4556"), ("pressed", "#1f2937")],
            foreground=[("disabled", "#6b7280")],
        )

        style.configure(
            "Accent.TButton",
            background="#2563eb",
            foreground="#ffffff",
            bordercolor="#1d4ed8",
            padding=(9, 7),
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#1d4ed8"), ("pressed", "#1e40af")],
        )

        style.configure(
            "Dark.TCheckbutton",
            background=self.PANEL_COLOR,
            foreground=self.TEXT_COLOR,
            font=("Segoe UI", 9),
        )
        style.map(
            "Dark.TCheckbutton",
            background=[("active", self.PANEL_COLOR)],
            foreground=[("active", self.TEXT_COLOR)],
        )

    def create_widgets(self):
        """Создаёт прокручиваемую панель управления и Canvas."""
        self.root.columnconfigure(0, minsize=320)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        panel_outer = ttk.Frame(self.root, width=320, style="Panel.TFrame")
        panel_outer.grid(row=0, column=0, sticky="ns")
        panel_outer.grid_propagate(False)
        panel_outer.rowconfigure(0, weight=1)
        panel_outer.columnconfigure(0, weight=1)

        self.panel_canvas = tk.Canvas(
            panel_outer,
            bg=self.PANEL_COLOR,
            highlightthickness=0,
            bd=0,
        )
        panel_scroll = ttk.Scrollbar(
            panel_outer,
            orient="vertical",
            command=self.panel_canvas.yview,
        )
        self.panel_canvas.configure(yscrollcommand=panel_scroll.set)
        self.panel_canvas.grid(row=0, column=0, sticky="nsew")
        panel_scroll.grid(row=0, column=1, sticky="ns")

        self.control_panel = ttk.Frame(
            self.panel_canvas,
            padding=(16, 16),
            style="Panel.TFrame",
        )
        self.panel_window = self.panel_canvas.create_window(
            (0, 0),
            window=self.control_panel,
            anchor="nw",
            width=300,
        )
        self.control_panel.bind("<Configure>", self._update_panel_scroll_region)
        self.panel_canvas.bind("<Configure>", self._resize_panel_window)
        self.panel_canvas.bind_all("<MouseWheel>", self._scroll_panel)

        drawing_area = ttk.Frame(self.root, padding=(14, 14), style="Root.TFrame")
        drawing_area.grid(row=0, column=1, sticky="nsew")
        drawing_area.columnconfigure(0, weight=1)
        drawing_area.rowconfigure(0, weight=1)

        self._create_panel_content()

        self.canvas = tk.Canvas(
            drawing_area,
            bg=self.CANVAS_COLOR,
            highlightthickness=1,
            highlightbackground="#2d3748",
            cursor="crosshair",
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Button-1>", self.add_point)
        self.canvas.bind("<Double-Button-1>", self.close_polygon)
        self.canvas.bind("<Motion>", self.update_mouse_position)
        self.canvas.bind("<MouseWheel>", self.zoom_workspace_with_wheel)
        self.canvas.bind("<Configure>", self._redraw_canvas_on_resize)

        status_frame = ttk.Frame(drawing_area, style="Root.TFrame")
        status_frame.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        status_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(1, weight=1)

        ttk.Label(
            status_frame,
            textvariable=self.last_operation,
            style="Status.TLabel",
            anchor="w",
        ).grid(row=0, column=0, sticky="ew")

        ttk.Label(
            status_frame,
            textvariable=self.mouse_position_text,
            style="Status.TLabel",
            anchor="e",
        ).grid(row=0, column=1, sticky="ew")

    def _create_panel_content(self):
        """Наполняет левую панель заголовком, полями, кнопками и статусом."""
        ttk.Label(
            self.control_panel,
            text="Преобразование\nмногоугольника",
            style="Title.TLabel",
        ).pack(anchor="w")

        ttk.Label(
            self.control_panel,
            text=(
                "Кликайте по полю, чтобы добавить вершины. "
                "Нажмите \"Замкнуть\" или дважды кликните по полю."
            ),
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(8, 14))

        self._section("Параметры")
        self._create_parameter_fields()

        self._section("Построение")
        self._add_button("Замкнуть многоугольник", self.close_polygon, accent=True)
        self._add_button("Удалить последнюю вершину", self.delete_last_point)
        self._add_button("Пример многоугольника", self.create_demo_polygon)
        self._add_button("Отменить действие", self.undo_last_action)
        self._add_button("Очистить", self.clear_canvas)

        self._section("Преобразования по ТЗ")
        self._add_button("Сместить вправо и вниз", self.translate_polygon)
        self._add_button("Отразить относительно X (y = cy)", self.reflect_x)
        self._add_button("Отразить относительно Y (x = cx)", self.reflect_y)
        self._add_button("Масштаб по sx/sy", self.scale_polygon)
        self._add_button("Растянуть", self.stretch_polygon)
        self._add_button("Сжать", self.shrink_polygon)
        self._add_button(
            "Повернуть по часовой + увеличить",
            self.rotate_clockwise_and_scale_up,
        )
        self._add_button(
            "Повернуть против часовой + уменьшить",
            self.rotate_counterclockwise_and_scale_down,
        )

        self._section("Дополнительно")
        self._add_button("Отразить от OX (y = 0)", self.reflect_origin_x)
        self._add_button("Отразить от OY (x = 0)", self.reflect_origin_y)
        self._add_button("Повернуть по часовой", self.rotate_clockwise)
        self._add_button("Повернуть против часовой", self.rotate_counterclockwise)
        self._add_button("Увеличить от центра", self.scale_up_from_center)
        self._add_button("Уменьшить от центра", self.scale_down_from_center)
        self._add_button("Центр = центр фигуры", self.set_center_to_polygon_center)
        self._add_button("Вписать фигуру в окно", self.fit_polygon_to_canvas)
        self._add_button("Сбросить параметры", self.reset_parameters)

        self._section("Рабочая область")
        self._add_button("Приблизить", self.zoom_in_workspace)
        self._add_button("Отдалить", self.zoom_out_workspace)
        self._add_button("Сдвинуть влево", self.pan_workspace_left)
        self._add_button("Сдвинуть вправо", self.pan_workspace_right)
        self._add_button("Сдвинуть вверх", self.pan_workspace_up)
        self._add_button("Сдвинуть вниз", self.pan_workspace_down)
        self._add_button("Сбросить вид", self.reset_workspace_view)

        self._section("Отображение")
        self._add_checkbutton("Показывать сетку", self.show_grid)
        self._add_checkbutton("Заливка многоугольника", self.show_fill)
        self._add_checkbutton("Номера вершин", self.show_numbers)

        self._section("Информация")
        self._create_info_block()

    def _create_parameter_fields(self):
        """Создаёт поля ввода параметров преобразований."""
        fields_frame = ttk.Frame(self.control_panel, style="Section.TFrame")
        fields_frame.pack(fill="x", pady=(0, 8))
        fields_frame.columnconfigure(1, weight=1)

        labels = {
            "dx": "dx",
            "dy": "dy",
            "sx": "sx",
            "sy": "sy",
            "cx": "cx",
            "cy": "cy",
            "angle": "angle",
        }

        for row, (name, label_text) in enumerate(labels.items()):
            ttk.Label(
                fields_frame,
                text=label_text,
                style="Field.TLabel",
            ).grid(row=row, column=0, sticky="w", pady=3, padx=(0, 10))

            entry = ttk.Entry(fields_frame, style="Dark.TEntry")
            entry.insert(0, self.DEFAULT_VALUES[name])
            entry.grid(row=row, column=1, sticky="ew", pady=3)
            entry.bind("<KeyRelease>", self._redraw_center_on_input)
            entry.bind("<FocusOut>", self._redraw_center_on_input)
            self.entries[name] = entry

    def _create_info_block(self):
        """Создаёт информационную область состояния."""
        ttk.Label(
            self.control_panel,
            textvariable=self.vertex_count_text,
            style="Info.TLabel",
        ).pack(anchor="w", pady=2)

        ttk.Label(
            self.control_panel,
            textvariable=self.closed_state_text,
            style="Info.TLabel",
        ).pack(anchor="w", pady=2)

        ttk.Label(
            self.control_panel,
            textvariable=self.bounds_text,
            style="Info.TLabel",
        ).pack(anchor="w", pady=2)

        ttk.Label(
            self.control_panel,
            textvariable=self.view_text,
            style="Info.TLabel",
        ).pack(anchor="w", pady=2)

        ttk.Label(
            self.control_panel,
            text="Последняя операция:",
            style="Info.TLabel",
        ).pack(anchor="w", pady=(10, 2))

        ttk.Label(
            self.control_panel,
            textvariable=self.last_operation,
            style="Hint.TLabel",
        ).pack(anchor="w", fill="x")

    def add_point(self, event):
        """Добавляет вершину по клику мыши."""
        if self.is_closed:
            self.set_status("Многоугольник уже замкнут. Нажмите \"Очистить\".")
            return

        world_x, world_y = self.screen_to_world(event.x, event.y)
        self._save_history()
        self.points.append((world_x, world_y))
        self.set_status(f"Добавлена вершина {len(self.points)}")
        self.draw_scene()

    def update_mouse_position(self, event):
        """Обновляет координаты мыши под Canvas."""
        world_x, world_y = self.screen_to_world(event.x, event.y)
        self.mouse_position_text.set(
            f"Экран: x={event.x}, y={event.y} | Поле: x={world_x:.1f}, y={world_y:.1f}"
        )

    def close_polygon(self, _event=None):
        """Замыкает многоугольник, если задано минимум три вершины."""
        if self.is_closed:
            self.set_status("Многоугольник уже замкнут.")
            return

        if len(self.points) < 3:
            self.set_status("Для замыкания нужно минимум 3 вершины.")
            return

        self._save_history()
        self.is_closed = True
        self.set_status("Многоугольник замкнут")
        self.draw_scene()

    def draw_scene(self):
        """Полностью перерисовывает сцену."""
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_axes()
        self.draw_polygon()
        self.draw_points()
        self.draw_center_marker()
        self.update_info()

    def draw_grid(self):
        """Рисует вспомогательную сетку."""
        if not self.show_grid.get():
            return

        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        step = 50.0

        while step * self.view_scale < 28:
            step *= 2

        left, top = self.screen_to_world(0, 0)
        right, bottom = self.screen_to_world(width, height)
        start_x = math.floor(left / step) * step
        start_y = math.floor(top / step) * step

        x = start_x
        while x <= right:
            screen_x, _ = self.world_to_screen(x, 0)
            self.canvas.create_line(screen_x, 0, screen_x, height, fill=self.GRID_COLOR)
            x += step

        y = start_y
        while y <= bottom:
            _, screen_y = self.world_to_screen(0, y)
            self.canvas.create_line(0, screen_y, width, screen_y, fill=self.GRID_COLOR)
            y += step

    def draw_axes(self):
        """Рисует оси отражения x = cx и y = cy."""
        cx = self.get_float("cx", float(self.DEFAULT_VALUES["cx"]))
        cy = self.get_float("cy", float(self.DEFAULT_VALUES["cy"]))
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        screen_cx, screen_cy = self.world_to_screen(cx, cy)

        self.canvas.create_line(
            0,
            screen_cy,
            width,
            screen_cy,
            fill=self.AXIS_COLOR,
            dash=(6, 6),
            width=1,
        )
        self.canvas.create_line(
            screen_cx,
            0,
            screen_cx,
            height,
            fill=self.AXIS_COLOR,
            dash=(6, 6),
            width=1,
        )

    def draw_polygon(self):
        """Рисует ломаную или замкнутый многоугольник."""
        if len(self.points) < 2:
            return

        screen_points = self.points_to_screen(self.points)

        if self.is_closed:
            fill = self.FILL_COLOR if self.show_fill.get() else ""
            self.canvas.create_polygon(
                screen_points,
                outline=self.LINE_COLOR,
                fill=fill,
                width=2,
            )
        else:
            self.canvas.create_line(
                screen_points,
                fill=self.LINE_COLOR,
                width=2,
            )

    def draw_points(self):
        """Рисует вершины и номера вершин."""
        radius = 5

        for index, point in enumerate(self.points, start=1):
            x, y = self.world_to_screen(*point)
            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=self.POINT_COLOR,
                outline=self.POINT_OUTLINE,
                width=1,
            )

            if self.show_numbers.get():
                self.canvas.create_text(
                    x + 12,
                    y - 12,
                    text=str(index),
                    fill=self.TEXT_COLOR,
                    font=("Segoe UI", 10, "bold"),
                    anchor="w",
                )

    def draw_center_marker(self):
        """Рисует центр преобразований C(cx, cy)."""
        cx = self.get_float("cx", float(self.DEFAULT_VALUES["cx"]))
        cy = self.get_float("cy", float(self.DEFAULT_VALUES["cy"]))
        cx, cy = self.world_to_screen(cx, cy)
        size = 10

        self.canvas.create_line(
            cx - size,
            cy,
            cx + size,
            cy,
            fill=self.CENTER_COLOR,
            width=2,
        )
        self.canvas.create_line(
            cx,
            cy - size,
            cx,
            cy + size,
            fill=self.CENTER_COLOR,
            width=2,
        )
        self.canvas.create_oval(
            cx - 4,
            cy - 4,
            cx + 4,
            cy + 4,
            outline=self.CENTER_COLOR,
            width=2,
        )
        self.canvas.create_text(
            cx + 14,
            cy + 12,
            text="C",
            fill=self.CENTER_COLOR,
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        )

    def clear_canvas(self):
        """Очищает все вершины и состояние редактора."""
        self._save_history()
        self.points = []
        self.is_closed = False
        self.set_status("Поле очищено")
        self.draw_scene()

    def reset_parameters(self):
        """Сбрасывает параметры преобразований."""
        for name, value in self.DEFAULT_VALUES.items():
            entry = self.entries[name]
            entry.delete(0, tk.END)
            entry.insert(0, value)

        self.set_status("Параметры сброшены")
        self.draw_scene()

    def get_float(self, name, default):
        """Безопасно читает число из поля ввода."""
        try:
            return float(self.entries[name].get().replace(",", "."))
        except (KeyError, ValueError):
            return default

    def can_transform(self):
        """
        Проверяет, можно ли выполнять преобразование.

        Если пользователь уже поставил 3 вершины, но забыл нажать кнопку
        замыкания, фигура замыкается автоматически, чтобы кнопки не казались
        нерабочими.
        """
        if len(self.points) < 3:
            self.set_status("Нужно минимум 3 вершины.")
            return False

        if not self.is_closed:
            self.is_closed = True
            self.set_status("Многоугольник автоматически замкнут.")

        return True

    def translate_polygon(self):
        """Смещает многоугольник вправо и вниз."""
        if not self.can_transform():
            return

        dx = abs(self.get_float("dx", float(self.DEFAULT_VALUES["dx"])))
        dy = abs(self.get_float("dy", float(self.DEFAULT_VALUES["dy"])))
        vertices = np.array(self.points, dtype=float)
        vertices += np.array([dx, dy], dtype=float)

        self._apply_points(vertices, f"Смещение вправо и вниз: dx={dx:g}, dy={dy:g}")

    def reflect_x(self):
        """Отражает многоугольник относительно горизонтальной оси y = cy."""
        if not self.can_transform():
            return

        cy = self.get_float("cy", float(self.DEFAULT_VALUES["cy"]))
        vertices = np.array(self.points, dtype=float)
        vertices[:, 1] = 2 * cy - vertices[:, 1]

        self._apply_points(vertices, f"Отражение относительно X: y={cy:g}")

    def reflect_y(self):
        """Отражает многоугольник относительно вертикальной оси x = cx."""
        if not self.can_transform():
            return

        cx = self.get_float("cx", float(self.DEFAULT_VALUES["cx"]))
        vertices = np.array(self.points, dtype=float)
        vertices[:, 0] = 2 * cx - vertices[:, 0]

        self._apply_points(vertices, f"Отражение относительно Y: x={cx:g}")

    def scale_polygon(self):
        """Растягивает или сжимает многоугольник относительно точки C(cx, cy)."""
        if not self.can_transform():
            return

        sx = self.get_float("sx", float(self.DEFAULT_VALUES["sx"]))
        sy = self.get_float("sy", float(self.DEFAULT_VALUES["sy"]))
        cx, cy = self.get_center()
        vertices = self._scale_array(np.array(self.points, dtype=float), sx, sy, cx, cy)

        self._apply_points(vertices, f"Масштабирование: sx={sx:g}, sy={sy:g}")

    def stretch_polygon(self):
        """Растягивает многоугольник, используя коэффициенты больше 1."""
        if not self.can_transform():
            return

        sx = self.get_float("sx", float(self.DEFAULT_VALUES["sx"]))
        sy = self.get_float("sy", float(self.DEFAULT_VALUES["sy"]))
        scale_x = self._stretch_factor(sx)
        scale_y = self._stretch_factor(sy)
        cx, cy = self.get_center()
        vertices = self._scale_array(
            np.array(self.points, dtype=float),
            scale_x,
            scale_y,
            cx,
            cy,
        )
        self._apply_points(vertices, f"Растяжение: sx={scale_x:g}, sy={scale_y:g}")

    def shrink_polygon(self):
        """Сжимает многоугольник, используя коэффициенты меньше 1."""
        if not self.can_transform():
            return

        sx = self.get_float("sx", float(self.DEFAULT_VALUES["sx"]))
        sy = self.get_float("sy", float(self.DEFAULT_VALUES["sy"]))
        scale_x = self._shrink_factor(sx)
        scale_y = self._shrink_factor(sy)
        cx, cy = self.get_center()
        vertices = self._scale_array(
            np.array(self.points, dtype=float),
            scale_x,
            scale_y,
            cx,
            cy,
        )
        self._apply_points(vertices, f"Сжатие: sx={scale_x:g}, sy={scale_y:g}")

    def reflect_origin_x(self):
        """Дополнительная операция: отражение относительно экранной оси OX."""
        if not self.can_transform():
            return

        vertices = np.array(self.points, dtype=float)
        vertices[:, 1] = -vertices[:, 1]
        self._apply_points(vertices, "Отражение относительно экранной OX: y=0")

    def reflect_origin_y(self):
        """Дополнительная операция: отражение относительно экранной оси OY."""
        if not self.can_transform():
            return

        vertices = np.array(self.points, dtype=float)
        vertices[:, 0] = -vertices[:, 0]
        self._apply_points(vertices, "Отражение относительно экранной OY: x=0")

    def rotate_points(self, angle_degrees):
        """Поворачивает вершины относительно центра C(cx, cy)."""
        cx, cy = self.get_center()
        vertices = np.array(self.points, dtype=float)
        return self._rotate_array(vertices, angle_degrees, cx, cy)

    def rotate_clockwise_and_scale_up(self):
        """Поворачивает по часовой стрелке и увеличивает многоугольник."""
        if not self.can_transform():
            return

        angle = self.get_float("angle", float(self.DEFAULT_VALUES["angle"]))
        sx = self.get_float("sx", float(self.DEFAULT_VALUES["sx"]))
        sy = self.get_float("sy", float(self.DEFAULT_VALUES["sy"]))
        cx, cy = self.get_center()
        scale_x = self._stretch_factor(sx)
        scale_y = self._stretch_factor(sy)

        vertices = self._rotate_array(np.array(self.points, dtype=float), angle, cx, cy)
        vertices = self._scale_array(vertices, scale_x, scale_y, cx, cy)

        self._apply_points(
            vertices,
            f"Поворот по часовой {angle:g}° + увеличение ({scale_x:g}; {scale_y:g})",
        )

    def rotate_counterclockwise_and_scale_down(self):
        """Поворачивает против часовой стрелки и уменьшает многоугольник."""
        if not self.can_transform():
            return

        angle = self.get_float("angle", float(self.DEFAULT_VALUES["angle"]))
        sx = self.get_float("sx", float(self.DEFAULT_VALUES["sx"]))
        sy = self.get_float("sy", float(self.DEFAULT_VALUES["sy"]))
        cx, cy = self.get_center()
        scale_x = sx if 0 < sx < 1 else 0.9
        scale_y = sy if 0 < sy < 1 else 0.9

        vertices = self._rotate_array(np.array(self.points, dtype=float), -angle, cx, cy)
        vertices = self._scale_array(vertices, scale_x, scale_y, cx, cy)

        self._apply_points(
            vertices,
            f"Поворот против часовой {angle:g}° + уменьшение ({scale_x:g}; {scale_y:g})",
        )

    def rotate_clockwise(self):
        """Дополнительная операция: поворот по часовой без масштабирования."""
        if not self.can_transform():
            return

        angle = self.get_float("angle", float(self.DEFAULT_VALUES["angle"]))
        vertices = self.rotate_points(angle)
        self._apply_points(vertices, f"Поворот по часовой на {angle:g}°")

    def rotate_counterclockwise(self):
        """Дополнительная операция: поворот против часовой без масштабирования."""
        if not self.can_transform():
            return

        angle = self.get_float("angle", float(self.DEFAULT_VALUES["angle"]))
        vertices = self.rotate_points(-angle)
        self._apply_points(vertices, f"Поворот против часовой на {angle:g}°")

    def scale_up_from_center(self):
        """Дополнительная операция: увеличение относительно C."""
        if not self.can_transform():
            return

        sx = self.get_float("sx", float(self.DEFAULT_VALUES["sx"]))
        sy = self.get_float("sy", float(self.DEFAULT_VALUES["sy"]))
        cx, cy = self.get_center()
        scale_x = self._stretch_factor(sx)
        scale_y = self._stretch_factor(sy)
        vertices = self._scale_array(
            np.array(self.points, dtype=float),
            scale_x,
            scale_y,
            cx,
            cy,
        )
        self._apply_points(vertices, f"Увеличение ({scale_x:g}; {scale_y:g})")

    def scale_down_from_center(self):
        """Дополнительная операция: уменьшение относительно C."""
        if not self.can_transform():
            return

        sx = self.get_float("sx", float(self.DEFAULT_VALUES["sx"]))
        sy = self.get_float("sy", float(self.DEFAULT_VALUES["sy"]))
        cx, cy = self.get_center()
        scale_x = self._shrink_factor(sx)
        scale_y = self._shrink_factor(sy)
        vertices = self._scale_array(
            np.array(self.points, dtype=float),
            scale_x,
            scale_y,
            cx,
            cy,
        )
        self._apply_points(vertices, f"Уменьшение ({scale_x:g}; {scale_y:g})")

    def delete_last_point(self):
        """Удаляет последнюю вершину, пока многоугольник не замкнут."""
        if self.is_closed:
            self.set_status("Замкнутый многоугольник не редактируется. Используйте отмену или очистку.")
            return

        if not self.points:
            self.set_status("Нет вершин для удаления.")
            return

        self._save_history()
        self.points.pop()
        self.set_status("Последняя вершина удалена")
        self.draw_scene()

    def create_demo_polygon(self):
        """Создаёт готовый многоугольник для быстрой проверки кнопок."""
        self._save_history()
        self.points = [
            (340.0, 190.0),
            (520.0, 160.0),
            (650.0, 280.0),
            (570.0, 430.0),
            (380.0, 390.0),
        ]
        self.is_closed = True
        self.set_status("Создан пример многоугольника")
        self.draw_scene()

    def undo_last_action(self):
        """Возвращает предыдущее состояние фигуры."""
        if not self.history:
            self.set_status("Нет действий для отмены.")
            return

        points, is_closed = self.history.pop()
        self.points = points
        self.is_closed = is_closed
        self.set_status("Последнее действие отменено")
        self.draw_scene()

    def set_center_to_polygon_center(self):
        """Ставит C(cx, cy) в центр ограничивающего прямоугольника фигуры."""
        if not self.points:
            self.set_status("Нет фигуры для вычисления центра.")
            return

        vertices = np.array(self.points, dtype=float)
        min_x, min_y = vertices.min(axis=0)
        max_x, max_y = vertices.max(axis=0)
        cx = (min_x + max_x) / 2
        cy = (min_y + max_y) / 2
        self._set_entry("cx", cx)
        self._set_entry("cy", cy)
        self.set_status(f"Центр C установлен в ({cx:.1f}; {cy:.1f})")
        self.draw_scene()

    def fit_polygon_to_canvas(self):
        """Подбирает масштаб и сдвиг вида так, чтобы фигура была видна целиком."""
        if not self.points:
            self.set_status("Нет фигуры для перемещения.")
            return

        vertices = np.array(self.points, dtype=float)
        min_x, min_y = vertices.min(axis=0)
        max_x, max_y = vertices.max(axis=0)
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        margin = 45
        polygon_width = max(max_x - min_x, 1)
        polygon_height = max(max_y - min_y, 1)
        scale_x = (width - 2 * margin) / polygon_width
        scale_y = (height - 2 * margin) / polygon_height
        self.view_scale = self._clamp_view_scale(min(scale_x, scale_y))

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        self.view_offset_x = width / 2 - center_x * self.view_scale
        self.view_offset_y = height / 2 - center_y * self.view_scale

        self.set_status("Фигура вписана в окно")
        self.draw_scene()

    def zoom_in_workspace(self):
        """Приближает рабочую область."""
        self.zoom_workspace(1.25)
        self.set_status("Рабочая область приближена")

    def zoom_out_workspace(self):
        """Отдаляет рабочую область."""
        self.zoom_workspace(0.8)
        self.set_status("Рабочая область отдалена")

    def zoom_workspace_with_wheel(self, event):
        """Масштабирует рабочую область колесом мыши над Canvas."""
        factor = 1.12 if event.delta > 0 else 1 / 1.12
        self.zoom_workspace(factor, event.x, event.y)
        self.set_status("Масштаб рабочей области изменён колесом мыши")

    def zoom_workspace(self, factor, anchor_x=None, anchor_y=None):
        """Меняет масштаб вида, сохраняя точку под курсором на месте."""
        if anchor_x is None:
            anchor_x = self.canvas.winfo_width() / 2
        if anchor_y is None:
            anchor_y = self.canvas.winfo_height() / 2

        world_x, world_y = self.screen_to_world(anchor_x, anchor_y)
        self.view_scale = self._clamp_view_scale(self.view_scale * factor)
        self.view_offset_x = anchor_x - world_x * self.view_scale
        self.view_offset_y = anchor_y - world_y * self.view_scale
        self.draw_scene()

    def pan_workspace_left(self):
        """Сдвигает отображение рабочей области влево."""
        self.pan_workspace(-80, 0, "Рабочая область сдвинута влево")

    def pan_workspace_right(self):
        """Сдвигает отображение рабочей области вправо."""
        self.pan_workspace(80, 0, "Рабочая область сдвинута вправо")

    def pan_workspace_up(self):
        """Сдвигает отображение рабочей области вверх."""
        self.pan_workspace(0, -80, "Рабочая область сдвинута вверх")

    def pan_workspace_down(self):
        """Сдвигает отображение рабочей области вниз."""
        self.pan_workspace(0, 80, "Рабочая область сдвинута вниз")

    def pan_workspace(self, dx, dy, status):
        """Меняет экранный сдвиг рабочей области."""
        self.view_offset_x += dx
        self.view_offset_y += dy
        self.set_status(status)
        self.draw_scene()

    def reset_workspace_view(self):
        """Возвращает масштаб и сдвиг рабочей области к исходным значениям."""
        self.view_scale = 1.0
        self.view_offset_x = 0.0
        self.view_offset_y = 0.0
        self.set_status("Вид рабочей области сброшен")
        self.draw_scene()

    def set_status(self, text):
        """Обновляет текст последней операции."""
        self.last_operation.set(text)
        self.update_info()

    def update_info(self):
        """Обновляет информационную область."""
        self.vertex_count_text.set(f"Вершин: {len(self.points)}")
        state = "замкнут" if self.is_closed else "не замкнут"
        self.closed_state_text.set(f"Состояние: {state}")
        self.view_text.set(
            f"Вид: {self.view_scale * 100:.0f}%, "
            f"сдвиг ({self.view_offset_x:.0f}, {self.view_offset_y:.0f})"
        )

        if not self.points:
            self.bounds_text.set("Границы: —")
            return

        vertices = np.array(self.points, dtype=float)
        min_x, min_y = vertices.min(axis=0)
        max_x, max_y = vertices.max(axis=0)
        self.bounds_text.set(
            f"Границы: x {min_x:.0f}..{max_x:.0f}, y {min_y:.0f}..{max_y:.0f}"
        )

    def get_center(self):
        """Возвращает координаты центра C(cx, cy)."""
        return (
            self.get_float("cx", float(self.DEFAULT_VALUES["cx"])),
            self.get_float("cy", float(self.DEFAULT_VALUES["cy"])),
        )

    def world_to_screen(self, x, y):
        """Переводит координаты рабочей области в координаты Canvas."""
        return (
            x * self.view_scale + self.view_offset_x,
            y * self.view_scale + self.view_offset_y,
        )

    def screen_to_world(self, x, y):
        """Переводит координаты Canvas в координаты рабочей области."""
        return (
            (x - self.view_offset_x) / self.view_scale,
            (y - self.view_offset_y) / self.view_scale,
        )

    def points_to_screen(self, points):
        """Преобразует список мировых точек в экранные координаты."""
        return [self.world_to_screen(x, y) for x, y in points]

    def _stretch_factor(self, value):
        """Возвращает коэффициент растяжения больше 1."""
        if value > 1:
            return value
        if 0 < value < 1:
            return 1 / value
        return 1.2

    def _shrink_factor(self, value):
        """Возвращает коэффициент сжатия от 0 до 1."""
        if 0 < value < 1:
            return value
        if value > 1:
            return 1 / value
        return 0.8

    def _clamp_view_scale(self, value):
        """Ограничивает масштаб рабочей области разумным диапазоном."""
        return min(max(value, 0.1), 8.0)

    def _rotate_array(self, vertices, angle_degrees, cx, cy):
        """Возвращает NumPy-массив после поворота относительно C."""
        angle = math.radians(angle_degrees)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        center = np.array([cx, cy], dtype=float)
        shifted = vertices - center

        rotated = np.empty_like(shifted)
        rotated[:, 0] = shifted[:, 0] * cos_a - shifted[:, 1] * sin_a
        rotated[:, 1] = shifted[:, 0] * sin_a + shifted[:, 1] * cos_a
        return rotated + center

    def _scale_array(self, vertices, sx, sy, cx, cy):
        """Возвращает NumPy-массив после масштабирования относительно C."""
        center = np.array([cx, cy], dtype=float)
        scale = np.array([sx, sy], dtype=float)
        return center + scale * (vertices - center)

    def _apply_points(self, vertices, status):
        """Сохраняет историю, обновляет вершины и перерисовывает сцену."""
        self._save_history()
        self.points = self._to_points(vertices)
        self.set_status(status)
        self.draw_scene()

    def _save_history(self):
        """Сохраняет предыдущее состояние для отмены."""
        self.history.append((self.points.copy(), self.is_closed))
        if len(self.history) > 30:
            self.history.pop(0)

    def _to_points(self, vertices):
        """Преобразует NumPy-массив в список точек."""
        return [(float(x), float(y)) for x, y in vertices]

    def _set_entry(self, name, value):
        """Записывает число в поле ввода."""
        entry = self.entries[name]
        entry.delete(0, tk.END)
        entry.insert(0, f"{value:.1f}")

    def _section(self, title):
        """Добавляет заголовок раздела панели."""
        ttk.Label(
            self.control_panel,
            text=title,
            style="Section.TLabel",
        ).pack(anchor="w", pady=(14, 6))

    def _add_button(self, text, command, accent=False):
        """Добавляет кнопку на панель."""
        style_name = "Accent.TButton" if accent else "Dark.TButton"
        ttk.Button(
            self.control_panel,
            text=text,
            command=command,
            style=style_name,
        ).pack(fill="x", pady=3)

    def _add_checkbutton(self, text, variable):
        """Добавляет переключатель отображения."""
        ttk.Checkbutton(
            self.control_panel,
            text=text,
            variable=variable,
            command=self.draw_scene,
            style="Dark.TCheckbutton",
        ).pack(anchor="w", pady=3)

    def _redraw_center_on_input(self, _event=None):
        """Перерисовывает центр и оси после изменения cx или cy."""
        self.draw_scene()

    def _redraw_canvas_on_resize(self, _event=None):
        """Перерисовывает сцену при изменении размера Canvas."""
        self.draw_scene()

    def _update_panel_scroll_region(self, _event=None):
        """Обновляет область прокрутки левой панели."""
        self.panel_canvas.configure(scrollregion=self.panel_canvas.bbox("all"))

    def _resize_panel_window(self, event):
        """Подгоняет внутреннюю панель под ширину Canvas."""
        self.panel_canvas.itemconfigure(self.panel_window, width=max(event.width - 4, 260))

    def _scroll_panel(self, event):
        """Прокручивает левую панель колёсиком мыши."""
        panel_x = self.panel_canvas.winfo_rootx()
        panel_y = self.panel_canvas.winfo_rooty()
        panel_width = self.panel_canvas.winfo_width()
        panel_height = self.panel_canvas.winfo_height()

        if not (
            panel_x <= event.x_root <= panel_x + panel_width
            and panel_y <= event.y_root <= panel_y + panel_height
        ):
            return

        self.panel_canvas.yview_scroll(int(-event.delta / 120), "units")


if __name__ == "__main__":
    app = PolygonTransformEditor()
    app.run()
