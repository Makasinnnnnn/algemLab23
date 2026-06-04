import os
import numpy as np
import matplotlib.pyplot as plt


OUT_DIR = "variant1_graphs"
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 10


def setup_axes(ax, xlim, ylim, title):
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")

    ax.axhline(0, color="black", linewidth=1.1)
    ax.axvline(0, color="black", linewidth=1.1)

    ax.grid(True, linestyle="--", alpha=0.45)
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    ax.set_xticks(np.arange(np.floor(xlim[0]), np.ceil(xlim[1]) + 1, 1))
    ax.set_yticks(np.arange(np.floor(ylim[0]), np.ceil(ylim[1]) + 1, 1))


def save_fig(fig, filename):
    path = os.path.join(OUT_DIR, filename)
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"saved: {path}")


def plot_line(ax, A, B, C, xlim, ylim, label=None, color="gray", linestyle="--", linewidth=1.5):
    """
    Рисует прямую Ax + By + C = 0.
    """
    xs = np.linspace(xlim[0], xlim[1], 500)

    if abs(B) > 1e-12:
        ys = -(A * xs + C) / B
        ax.plot(xs, ys, color=color, linestyle=linestyle, linewidth=linewidth, label=label)
    else:
        x0 = -C / A
        ax.plot([x0, x0], [ylim[0], ylim[1]], color=color, linestyle=linestyle, linewidth=linewidth, label=label)


def mark_point(ax, x, y, label, color="red", dx=0.15, dy=0.15):
    ax.scatter([x], [y], color=color, s=35, zorder=5)
    ax.text(x + dx, y + dy, label, color=color, fontsize=10, fontweight="bold")


# ============================================================
# 1а: эллипс
# x² + y² + xy - 3x - 3y + 2 = 0
# Канонический вид:
# u²/(2/3) + v²/2 = 1
# u = (x + y - 2)/sqrt(2)
# v = (x - y)/sqrt(2)
# ============================================================

def graph_1a():
    fig, ax = plt.subplots(figsize=(7, 7))
    xlim = (-2.5, 4.5)
    ylim = (-2.5, 4.5)
    setup_axes(ax, xlim, ylim, "1а) Эллипс: x² + y² + xy - 3x - 3y + 2 = 0")

    C = np.array([1.0, 1.0])

    e_u = np.array([1 / np.sqrt(2), 1 / np.sqrt(2)])
    e_v = np.array([1 / np.sqrt(2), -1 / np.sqrt(2)])

    a_u = np.sqrt(2 / 3)
    a_v = np.sqrt(2)

    t = np.linspace(0, 2 * np.pi, 800)
    u = a_u * np.cos(t)
    v = a_v * np.sin(t)

    points = C[:, None] + e_u[:, None] * u + e_v[:, None] * v
    x = points[0]
    y = points[1]

    ax.plot(x, y, color="blue", linewidth=2.2, label="эллипс")

    # Центр
    mark_point(ax, 1, 1, "C(1;1)", color="red")

    # Фокальная ось: x + y = 2
    plot_line(ax, 1, 1, -2, xlim, ylim, label="фокальная ось x+y=2", color="orange")

    # Малая ось: направление u, y - 1 = x - 1 => y = x
    plot_line(ax, -1, 1, 0, xlim, ylim, label="ось u", color="green", linestyle=":")

    # Вершины большой полуоси
    P1 = C + a_v * e_v
    P2 = C - a_v * e_v
    mark_point(ax, P1[0], P1[1], "A₁", color="purple")
    mark_point(ax, P2[0], P2[1], "A₂", color="purple")

    # Фокусы
    c = np.sqrt(a_v ** 2 - a_u ** 2)
    F1 = C + c * e_v
    F2 = C - c * e_v
    mark_point(ax, F1[0], F1[1], "F₁", color="darkred")
    mark_point(ax, F2[0], F2[1], "F₂", color="darkred")

    ax.legend(loc="upper right")
    save_fig(fig, "fig_1a_ellipse.png")


# ============================================================
# 1б: окружность
# x² + y² + 6x - 10y = 11
# (x + 3)² + (y - 5)² = 45
# Касательная в M0(0;-1): x - 2y - 2 = 0
# ============================================================

def graph_1b():
    fig, ax = plt.subplots(figsize=(7, 7))
    xlim = (-12, 6)
    ylim = (-4, 14)
    setup_axes(ax, xlim, ylim, "1б) Окружность: (x+3)² + (y-5)² = 45")

    C = np.array([-3.0, 5.0])
    R = np.sqrt(45)

    t = np.linspace(0, 2 * np.pi, 1000)
    x = C[0] + R * np.cos(t)
    y = C[1] + R * np.sin(t)

    ax.plot(x, y, color="blue", linewidth=2.2, label="окружность")

    mark_point(ax, C[0], C[1], "C(-3;5)", color="red")
    mark_point(ax, 0, -1, "M₀(0;-1)", color="purple")

    # Радиус к точке касания
    ax.plot([C[0], 0], [C[1], -1], color="green", linewidth=1.7, label="радиус CM₀")

    # Касательная x - 2y - 2 = 0
    plot_line(ax, 1, -2, -2, xlim, ylim, label="касательная x-2y-2=0", color="orange")

    ax.legend(loc="upper right")
    save_fig(fig, "fig_1b_circle_tangent.png")


# ============================================================
# 1в: гипербола
# 3x² + 3y² + 10xy - 2x - 14y = 13
# Канонический вид:
# u² - v²/4 = 1
# u = (x + y - 1)/sqrt(2)
# v = (x - y - 3)/sqrt(2)
# Центр C(2;-1)
# Фокальная ось: y = x - 3
# Асимптоты:
# x + 3y + 1 = 0
# 3x + y - 5 = 0
# ============================================================

def graph_1v():
    fig, ax = plt.subplots(figsize=(7, 7))
    xlim = (-6, 10)
    ylim = (-9, 7)
    setup_axes(ax, xlim, ylim, "1в) Гипербола: u² - v²/4 = 1")

    C = np.array([2.0, -1.0])

    e_u = np.array([1 / np.sqrt(2), 1 / np.sqrt(2)])
    e_v = np.array([1 / np.sqrt(2), -1 / np.sqrt(2)])

    a = 1.0
    b = 2.0

    t = np.linspace(-2.0, 2.0, 600)

    # Правая ветвь в координатах u,v: u = a cosh(t), v = b sinh(t)
    u_right = a * np.cosh(t)
    v_right = b * np.sinh(t)

    points_right = C[:, None] + e_u[:, None] * u_right + e_v[:, None] * v_right
    ax.plot(points_right[0], points_right[1], color="blue", linewidth=2.2, label="гипербола")

    # Левая ветвь: u = -a cosh(t)
    u_left = -a * np.cosh(t)
    v_left = b * np.sinh(t)

    points_left = C[:, None] + e_u[:, None] * u_left + e_v[:, None] * v_left
    ax.plot(points_left[0], points_left[1], color="blue", linewidth=2.2)

    mark_point(ax, C[0], C[1], "C(2;-1)", color="red")

    # Фокальная ось y = x - 3 => -x + y + 3 = 0
    plot_line(ax, -1, 1, 3, xlim, ylim, label="фокальная ось y=x-3", color="orange")

    # Асимптоты
    plot_line(ax, 1, 3, 1, xlim, ylim, label="асимптота x+3y+1=0", color="gray")
    plot_line(ax, 3, 1, -5, xlim, ylim, label="асимптота 3x+y-5=0", color="gray")

    # Фокусы
    c = np.sqrt(a ** 2 + b ** 2)
    F1 = C + c * e_u
    F2 = C - c * e_u
    mark_point(ax, F1[0], F1[1], "F₁", color="darkred")
    mark_point(ax, F2[0], F2[1], "F₂", color="darkred")

    # Вершины
    A1 = C + a * e_u
    A2 = C - a * e_u
    mark_point(ax, A1[0], A1[1], "A₁", color="purple")
    mark_point(ax, A2[0], A2[1], "A₂", color="purple")

    ax.legend(loc="upper right")
    save_fig(fig, "fig_1v_hyperbola.png")


# ============================================================
# 1г: парабола
# 9x² + 16y² - 24xy - 20x + 110y = 50
# u = (-3x + 4y)/5
# v = (4x + 3y)/5
# U = u + 2
# V = v - 3
# U² = -2V
# Вершина: (18/5; 1/5)
# Ось симметрии: 3x - 4y - 10 = 0
# ============================================================

def graph_1g():
    fig, ax = plt.subplots(figsize=(7, 7))
    xlim = (-5, 9)
    ylim = (-7, 7)
    setup_axes(ax, xlim, ylim, "1г) Парабола: U² = -2V")

    # Параметризация:
    # U = t
    # V = -t²/2
    # u = U - 2
    # v = V + 3
    # x = (-3u + 4v)/5
    # y = (4u + 3v)/5

    t = np.linspace(-4.2, 4.2, 1000)
    U = t
    V = -t ** 2 / 2

    u = U - 2
    v = V + 3

    x = (-3 * u + 4 * v) / 5
    y = (4 * u + 3 * v) / 5

    ax.plot(x, y, color="blue", linewidth=2.2, label="парабола")

    # Вершина
    P0 = np.array([18 / 5, 1 / 5])
    mark_point(ax, P0[0], P0[1], "P₀(18/5;1/5)", color="red")

    # Ось симметрии: 3x - 4y - 10 = 0
    plot_line(ax, 3, -4, -10, xlim, ylim, label="ось 3x-4y-10=0", color="orange")

    # Фокус для U² = 2pV, p=-1:
    # фокус в координатах U,V: (0, p/2) = (0, -1/2)
    # значит u=-2, v=3-1/2=5/2
    u_f = -2
    v_f = 5 / 2
    x_f = (-3 * u_f + 4 * v_f) / 5
    y_f = (4 * u_f + 3 * v_f) / 5
    mark_point(ax, x_f, y_f, "F", color="darkred")

    # Директриса: V = 1/2 => v = 3 + 1/2 = 7/2
    # v = (4x+3y)/5 = 7/2 => 4x + 3y = 35/2
    plot_line(ax, 4, 3, -35 / 2, xlim, ylim, label="директриса", color="green", linestyle=":")

    ax.legend(loc="upper right")
    save_fig(fig, "fig_1g_parabola.png")


# ============================================================
# Задача 2
# Эллипс с фокусами в фокусах гиперболы x² - y² = 2
# Ответ:
# x²/16 + y²/12 = 1
# Фокусы: (-2;0), (2;0)
# Точка M(2;3)
# ============================================================

def graph_task2():
    fig, ax = plt.subplots(figsize=(7, 7))
    xlim = (-5.5, 5.5)
    ylim = (-4.5, 4.5)
    setup_axes(ax, xlim, ylim, "Задача 2) Эллипс: x²/16 + y²/12 = 1")

    a = 4
    b = np.sqrt(12)

    t = np.linspace(0, 2 * np.pi, 1000)
    x = a * np.cos(t)
    y = b * np.sin(t)

    ax.plot(x, y, color="blue", linewidth=2.2, label="эллипс")

    mark_point(ax, 0, 0, "O(0;0)", color="red")
    mark_point(ax, -2, 0, "F₁(-2;0)", color="darkred")
    mark_point(ax, 2, 0, "F₂(2;0)", color="darkred")
    mark_point(ax, 2, 3, "M(2;3)", color="purple")

    # Большая ось Ox
    ax.plot([-4, 4], [0, 0], color="orange", linewidth=1.7, label="большая ось")

    # Вершины
    mark_point(ax, -4, 0, "A₁", color="green")
    mark_point(ax, 4, 0, "A₂", color="green")

    ax.legend(loc="upper right")
    save_fig(fig, "fig_task2_ellipse.png")


# ============================================================
# Задача 3
# Асимптоты: 3x ± 4y = 0
# Фокусы на Oy, 2c = 20
# Ответ:
# y²/36 - x²/64 = 1
# ============================================================

def graph_task3():
    fig, ax = plt.subplots(figsize=(7, 7))
    xlim = (-14, 14)
    ylim = (-14, 14)
    setup_axes(ax, xlim, ylim, "Задача 3) Гипербола: y²/36 - x²/64 = 1")

    a = 6
    b = 8
    c = 10

    t = np.linspace(-1.45, 1.45, 700)

    # Верхняя ветвь: y = a cosh(t), x = b sinh(t)
    x_top = b * np.sinh(t)
    y_top = a * np.cosh(t)

    # Нижняя ветвь
    x_bottom = b * np.sinh(t)
    y_bottom = -a * np.cosh(t)

    ax.plot(x_top, y_top, color="blue", linewidth=2.2, label="гипербола")
    ax.plot(x_bottom, y_bottom, color="blue", linewidth=2.2)

    # Асимптоты y = ±3/4 x
    xs = np.linspace(xlim[0], xlim[1], 500)
    ax.plot(xs, 3 / 4 * xs, color="gray", linestyle="--", linewidth=1.5, label="асимптоты")
    ax.plot(xs, -3 / 4 * xs, color="gray", linestyle="--", linewidth=1.5)

    # Центр, фокусы, вершины
    mark_point(ax, 0, 0, "O(0;0)", color="red")
    mark_point(ax, 0, -c, "F₁(0;-10)", color="darkred")
    mark_point(ax, 0, c, "F₂(0;10)", color="darkred")
    mark_point(ax, 0, -a, "A₁", color="green")
    mark_point(ax, 0, a, "A₂", color="green")

    ax.legend(loc="upper right")
    save_fig(fig, "fig_task3_hyperbola.png")


# ============================================================
# Задача 4
# Парабола симметрична относительно Oy
# Ответ:
# y = -2x² + 40
# Канонический вид:
# x² = -1/2 (y - 40)
# Если x² = 2p(y-y0), то:
# 2p = -1/2, p = -1/4
# Директриса:
# y = y0 - p/2 = 40 - (-1/4)/2 = 321/8
# ============================================================

def graph_task4():
    fig, ax = plt.subplots(figsize=(7, 8))
    xlim = (-6, 6)
    ylim = (-8, 43)
    setup_axes(ax, xlim, ylim, "Задача 4) Парабола: y = -2x² + 40")

    x = np.linspace(xlim[0], xlim[1], 1000)
    y = -2 * x ** 2 + 40

    ax.plot(x, y, color="blue", linewidth=2.2, label="парабола y=-2x²+40")

    # Прямая x+y=0
    ax.plot(x, -x, color="gray", linestyle="--", linewidth=1.4, label="прямая x+y=0")

    # Окружность x² + y² - x = 40
    # (x - 1/2)² + y² = 40 + 1/4 = 161/4
    circle_center = np.array([0.5, 0.0])
    R = np.sqrt(161 / 4)

    t = np.linspace(0, 2 * np.pi, 1000)
    xc = circle_center[0] + R * np.cos(t)
    yc = circle_center[1] + R * np.sin(t)
    ax.plot(xc, yc, color="green", linestyle=":", linewidth=1.8, label="окружность")

    # Вершина
    mark_point(ax, 0, 40, "P₀(0;40)", color="red", dx=0.2, dy=0.2)

    # Фокус и директриса
    # Для x² = 2p(y-40), p=-1/4
    # Фокус: y = y0 + p/2 = 40 - 1/8 = 319/8
    # Директриса: y = y0 - p/2 = 40 + 1/8 = 321/8
    y_focus = 319 / 8
    y_directrix = 321 / 8

    mark_point(ax, 0, y_focus, "F", color="darkred", dx=0.2, dy=-0.5)
    ax.axhline(y_directrix, color="orange", linestyle="--", linewidth=1.7, label="директриса y=321/8")

    # Точки пересечения прямой и окружности:
    # 2x² - x - 40 = 0
    roots = np.roots([2, -1, -40])
    for i, xr in enumerate(roots):
        yr = -xr
        mark_point(ax, xr, yr, f"M{i+1}", color="purple", dx=0.15, dy=0.15)

    ax.legend(loc="lower right")
    save_fig(fig, "fig_task4_parabola_directrix.png")


def main():
    graph_1a()
    graph_1b()
    graph_1v()
    graph_1g()
    graph_task2()
    graph_task3()
    graph_task4()

    print("\nГотово. Все графики сохранены в папку:", OUT_DIR)


if __name__ == "__main__":
    main()