import tkinter as tk
from tkinter import ttk

import numpy as np


class SplineApp:
    """Приложение для построения ломаной линии и сглаживания ее сплайном."""

    POINT_RADIUS = 4
    POLYLINE_COLOR = "#4b5563"
    SPLINE_COLOR = "#2563eb"
    POINT_FILL = "#ef4444"
    POINT_OUTLINE = "#7f1d1d"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Лабораторная работа №2 — Ломаная и сплайн")
        self.root.geometry("900x600")
        self.root.minsize(700, 450)

        self.points = []
        self.spline_points = []
        self.display_mode = "polyline"

        self._configure_style()
        self._create_widgets()

    def _configure_style(self):
        """Настраивает аккуратный внешний вид стандартных элементов Tkinter."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f3f4f6")
        style.configure("Hint.TLabel", background="#f3f4f6", foreground="#374151")
        style.configure("TButton", padding=(10, 6), font=("Segoe UI", 10))

    def _create_widgets(self):
        """Создает область рисования, кнопки и текстовую подсказку."""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(self.root, padding=(12, 10))
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.columnconfigure(3, weight=1)

        self.clear_button = ttk.Button(
            toolbar,
            text="Очистить",
            command=self.clear_canvas,
        )
        self.clear_button.grid(row=0, column=0, padx=(0, 8))

        self.show_polyline_button = ttk.Button(
            toolbar,
            text="Показать ломаную",
            command=self.show_polyline,
        )
        self.show_polyline_button.grid(row=0, column=1, padx=(0, 8))

        self.show_spline_button = ttk.Button(
            toolbar,
            text="Показать сплайн",
            command=self.show_spline,
        )
        self.show_spline_button.grid(row=0, column=2, padx=(0, 8))

        hint = ttk.Label(
            toolbar,
            text="Кликайте по полю, чтобы добавить точки",
            style="Hint.TLabel",
            anchor="e",
        )
        hint.grid(row=0, column=3, sticky="e")

        self.canvas = tk.Canvas(
            self.root,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#d1d5db",
            cursor="crosshair",
        )
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.canvas.bind("<Button-1>", self.add_point)

    def run(self):
        """Запускает главный цикл приложения."""
        self.root.mainloop()

    def add_point(self, event):
        """Добавляет контрольную точку по клику мыши."""
        self.points.append((event.x, event.y))
        self.spline_points = []
        self.display_mode = "polyline"
        self.redraw()

    def draw_points(self):
        """Рисует все контрольные точки маленькими кругами."""
        for index, (x, y) in enumerate(self.points, start=1):
            self.canvas.create_oval(
                x - self.POINT_RADIUS,
                y - self.POINT_RADIUS,
                x + self.POINT_RADIUS,
                y + self.POINT_RADIUS,
                fill=self.POINT_FILL,
                outline=self.POINT_OUTLINE,
                width=1,
            )
            self.canvas.create_text(
                x + 10,
                y - 10,
                text=str(index),
                fill="#6b7280",
                font=("Segoe UI", 9),
                anchor="w",
            )

    def draw_polyline(self):
        """Рисует прямые отрезки между соседними контрольными точками."""
        if len(self.points) < 2:
            return

        self.canvas.create_line(
            self.points,
            fill=self.POLYLINE_COLOR,
            width=2,
            smooth=False,
        )

    def catmull_rom_spline(self, points, samples_per_segment=30):
        """
        Строит точки Catmull-Rom сплайна по списку контрольных точек.

        Для краев первая и последняя точки дублируются, чтобы кривая начиналась
        в первой контрольной точке и заканчивалась в последней.
        """
        if len(points) < 2:
            return []

        if len(points) == 2:
            return points[:]

        control_points = np.array(points, dtype=float)
        extended_points = np.vstack(
            [control_points[0], control_points, control_points[-1]]
        )

        spline = []

        for i in range(1, len(extended_points) - 2):
            p0 = extended_points[i - 1]
            p1 = extended_points[i]
            p2 = extended_points[i + 1]
            p3 = extended_points[i + 2]

            # t идет от 0 до 1; правую границу добавим отдельно,
            # чтобы не дублировать точки на стыках соседних участков.
            for sample in range(samples_per_segment):
                t = sample / samples_per_segment
                t2 = t * t
                t3 = t2 * t

                point = 0.5 * (
                    2 * p1
                    + (-p0 + p2) * t
                    + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                    + (-p0 + 3 * p1 - 3 * p2 + p3) * t3
                )

                spline.append((float(point[0]), float(point[1])))

        spline.append(tuple(map(float, control_points[-1])))
        return spline

    def show_polyline(self):
        """Показывает исходную ломаную линию."""
        self.display_mode = "polyline"
        self.redraw()

    def show_spline(self):
        """Показывает сплайн, если для него достаточно точек."""
        if len(self.points) < 2:
            return

        if not self.spline_points:
            self.spline_points = self.catmull_rom_spline(self.points)

        self.display_mode = "spline"
        self.redraw()

    def clear_canvas(self):
        """Удаляет точки, ломаную и сплайн."""
        self.points = []
        self.spline_points = []
        self.display_mode = "polyline"
        self.redraw()

    def redraw(self):
        """Полностью перерисовывает текущую сцену."""
        self.canvas.delete("all")

        if self.display_mode == "spline":
            if len(self.spline_points) >= 2:
                self.canvas.create_line(
                    self.spline_points,
                    fill=self.SPLINE_COLOR,
                    width=3,
                    smooth=False,
                )
            elif len(self.points) == 2:
                self.draw_polyline()
        else:
            self.draw_polyline()

        self.draw_points()


if __name__ == "__main__":
    app = SplineApp()
    app.run()
