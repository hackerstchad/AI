#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                                                                                  ║
║    ██████╗ ███████╗ ██████╗ ██████╗ ██████╗ ████████╗    ██████╗ ██████╗       ║
║   ██╔════╝ ██╔════╝██╔═══██╗██╔══██╗██╔══██╗╚══██╔══╝    ██╔══██╗╚════██╗      ║
║   ██║  ███╗█████╗  ██║   ██║██║  ██║██████╔╝   ██║       ██████╔╝  ▄███╔╝      ║
║   ██║   ██║██╔══╝  ██║   ██║██║  ██║██╔══██╗   ██║       ██╔══██╗  ▀▀══╝       ║
║   ╚██████╔╝███████╗╚██████╔╝██████╔╝██║  ██║   ██║       ██║  ██║  ██╗         ║
║    ╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚═╝  ╚═╝  ╚═╝         ║
║                                                                                  ║
║          G E O 3 D   M A S T E R   -   E S P A C E   G É O M É T R I Q U E      ║
║                                                                                  ║
║   Version  : 1.0.0                                                               ║
║   Auteur   : hackers_tchad 🇹🇩                                                    ║
║   Objectif : Visualisation 3D géométrique interactive et éducative               ║
║                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝

⚠️  AVERTISSEMENT : Cet outil est un simulateur éducatif de visualisation 3D.
    Il ne peut pas "voir" l'utilisateur sans caméra active et explicite.
    Si une caméra est utilisée, c'est uniquement avec le consentement de
    l'utilisateur et à des fins pédagogiques. Aucune capture ni stockage
    d'image réelle n'est effectué sans permission.
"""

import os
import sys
import time
import math
import json
import random
import shutil
import socket
import getpass
import argparse
import datetime
from collections import defaultdict

# Imports optionnels avec fallback

try:
    import numpy as np
except ImportError:
    np = None

try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
except ImportError:
    plt = None

try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
except ImportError:
    class _DummyColor:
        def __getattr__(self, name):
            return ''
    Fore = Style = Back = _DummyColor()

try:
    from tqdm import tqdm
except ImportError:
    class tqdm:
        def __init__(self, iterable=None, **kwargs):
            self.iterable = iterable
        def __iter__(self):
            for x in self.iterable:
                yield x
        def update(self, n=1):
            pass
        def close(self):
            pass

try:
    import pyfiglet
except ImportError:
    pyfiglet = None


# ═══════════════════════════════════════════════════════════════════════════════════
# CONFIGURATION GLOBALE
# ═══════════════════════════════════════════════════════════════════════════════════
VERSION = "1.0.0"
AUTHOR = "hackers_tchad"
TITLE = "GEO3D MASTER"
TAGLINES = [
    "L'espace géométrique entre vos mains.",
    "Visualisez, apprenez, créez en 3D.",
    "La géométrie n'a plus de secrets.",
    "Formes, lumières, perspectives vertes.",
    "Explorez l'infini en trois dimensions.",
]

SESSION_LOG = []
SCENES = defaultdict(list)
CAMERA_ENABLED = False
CAMERA_SOURCE = None


# ═══════════════════════════════════════════════════════════════════════════════════
# UTILITAIRES D'AFFICHAGE
# ═══════════════════════════════════════════════════════════════════════════════════
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def line(char="═", color=Fore.GREEN):
    width = shutil.get_terminal_size().columns
    print(color + char * width + Style.RESET_ALL)


def center(text, color=Fore.GREEN):
    width = shutil.get_terminal_size().columns
    print(color + text.center(width) + Style.RESET_ALL)


def banner():
    clear()
    if pyfiglet:
        f = pyfiglet.Figlet(font='ogre')
        art = f.renderText(TITLE)
        print(Fore.GREEN + Style.BRIGHT + art)
    else:
        line("█", Fore.GREEN)
        center("G E O 3 D   M A S T E R", Fore.GREEN + Style.BRIGHT)
        line("█", Fore.GREEN)
    center("Visualisation 3D Géométrique & Éducative", Fore.CYAN)
    center(f"Version {VERSION} | Auteur: {AUTHOR}", Fore.YELLOW)
    center(random.choice(TAGLINES), Fore.MAGENTA)
    line()
    center("⚠️  SIMULATEUR ÉDUCATIF UNIQUEMENT  ⚠️", Fore.RED + Back.BLACK)
    line()


def header(text):
    print(f"\n{Fore.GREEN}{Style.BRIGHT}╔═ {text} ═{'═' * (70 - len(text))}╗{Style.RESET_ALL}")


def info(text):
    print(f"{Fore.CYAN}[ℹ] {text}{Style.RESET_ALL}")


def success(text):
    print(f"{Fore.GREEN}[✓] {text}{Style.RESET_ALL}")


def warning(text):
    print(f"{Fore.YELLOW}[!] {text}{Style.RESET_ALL}")


def error(text):
    print(f"{Fore.RED}[✗] {text}{Style.RESET_ALL}")


def prompt(text):
    return input(f"{Fore.GREEN}{Style.BRIGHT}[?] {text}{Style.RESET_ALL}").strip()


def pause():
    input(f"\n{Fore.YELLOW}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")


def ts_iso():
    return datetime.datetime.now().isoformat()


def log_event(category, action, detail="", status="OK"):
    entry = {
        "timestamp": ts_iso(),
        "category": category,
        "action": action,
        "detail": detail,
        "status": status,
    }
    SESSION_LOG.append(entry)


# ═══════════════════════════════════════════════════════════════════════════════════
# BARRES DE PROGRESSION & ANIMATIONS
# ═══════════════════════════════════════════════════════════════════════════════════
def progress(desc, total=100, min_sleep=0.005, max_sleep=0.02):
    for _ in tqdm(range(total), desc=f"{Fore.GREEN}{desc}{Style.RESET_ALL}",
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
        time.sleep(random.uniform(min_sleep, max_sleep))


def steps_progress(prefix, steps):
    for step in steps:
        for _ in tqdm(range(100), desc=f"{Fore.CYAN}{prefix} {step}{Style.RESET_ALL}", leave=False,
                      bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
            time.sleep(random.uniform(0.003, 0.01))
        success(f"{step} terminé.")


def matrix_rain(duration=1.5):
    chars = "01"
    width = shutil.get_terminal_size().columns
    end = time.time() + duration
    while time.time() < end:
        line = "".join(random.choice(chars) if random.random() > 0.80 else " " for _ in range(width))
        print(Fore.GREEN + line + Style.RESET_ALL, end="\r")
        time.sleep(0.05)
    print()


# ═══════════════════════════════════════════════════════════════════════════════════
# MOTEUR 3D GÉOMÉTRIQUE DE BASE
# ═══════════════════════════════════════════════════════════════════════════════════
class Vec3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self):
        return f"Vec3({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self):
        l = self.length()
        if l == 0:
            return Vec3(0, 0, 0)
        return Vec3(self.x / l, self.y / l, self.z / l)

    def to_tuple(self):
        return (self.x, self.y, self.z)


class Mat4:
    def __init__(self, identity=False):
        if identity:
            self.m = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
        else:
            self.m = [[0.0 for _ in range(4)] for _ in range(4)]

    @staticmethod
    def identity():
        return Mat4(identity=True)

    @staticmethod
    def translation(tx, ty, tz):
        mat = Mat4.identity()
        mat.m[0][3] = tx
        mat.m[1][3] = ty
        mat.m[2][3] = tz
        return mat

    @staticmethod
    def rotation_x(angle):
        mat = Mat4.identity()
        c = math.cos(angle)
        s = math.sin(angle)
        mat.m[1][1] = c
        mat.m[1][2] = -s
        mat.m[2][1] = s
        mat.m[2][2] = c
        return mat

    @staticmethod
    def rotation_y(angle):
        mat = Mat4.identity()
        c = math.cos(angle)
        s = math.sin(angle)
        mat.m[0][0] = c
        mat.m[0][2] = s
        mat.m[2][0] = -s
        mat.m[2][2] = c
        return mat

    @staticmethod
    def rotation_z(angle):
        mat = Mat4.identity()
        c = math.cos(angle)
        s = math.sin(angle)
        mat.m[0][0] = c
        mat.m[0][1] = -s
        mat.m[1][0] = s
        mat.m[1][1] = c
        return mat

    @staticmethod
    def scaling(sx, sy, sz):
        mat = Mat4.identity()
        mat.m[0][0] = sx
        mat.m[1][1] = sy
        mat.m[2][2] = sz
        return mat

    def multiply(self, other):
        result = Mat4()
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    result.m[i][j] += self.m[i][k] * other.m[k][j]
        return result

    def transform_vec3(self, v):
        x = self.m[0][0] * v.x + self.m[0][1] * v.y + self.m[0][2] * v.z + self.m[0][3]
        y = self.m[1][0] * v.x + self.m[1][1] * v.y + self.m[1][2] * v.z + self.m[1][3]
        z = self.m[2][0] * v.x + self.m[2][1] * v.y + self.m[2][2] * v.z + self.m[2][3]
        return Vec3(x, y, z)


# ═══════════════════════════════════════════════════════════════════════════════════
# FORMES GÉOMÉTRIQUES 3D
# ═══════════════════════════════════════════════════════════════════════════════════
class Geometry3D:
    def __init__(self, name="object"):
        self.name = name
        self.vertices = []
        self.faces = []
        self.color = "green"
        self.position = Vec3()
        self.rotation = Vec3()
        self.scale = Vec3(1, 1, 1)
        self.wireframe = False

    def add_vertex(self, x, y, z):
        self.vertices.append(Vec3(x, y, z))

    def add_face(self, indices):
        self.faces.append(indices)

    def transform(self):
        t = Mat4.translation(self.position.x, self.position.y, self.position.z)
        rx = Mat4.rotation_x(self.rotation.x)
        ry = Mat4.rotation_y(self.rotation.y)
        rz = Mat4.rotation_z(self.rotation.z)
        s = Mat4.scaling(self.scale.x, self.scale.y, self.scale.z)
        transform = t.multiply(rx).multiply(ry).multiply(rz).multiply(s)
        return [transform.transform_vec3(v) for v in self.vertices]

    def get_face_vertices(self):
        transformed = self.transform()
        return [[transformed[i] for i in face] for face in self.faces]

    def center(self):
        if not self.vertices:
            return Vec3()
        cx = sum(v.x for v in self.vertices) / len(self.vertices)
        cy = sum(v.y for v in self.vertices) / len(self.vertices)
        cz = sum(v.z for v in self.vertices) / len(self.vertices)
        return Vec3(cx, cy, cz)


def create_cube(size=1.0):
    geo = Geometry3D("cube")
    s = size / 2.0
    geo.add_vertex(-s, -s, -s)
    geo.add_vertex(s, -s, -s)
    geo.add_vertex(s, s, -s)
    geo.add_vertex(-s, s, -s)
    geo.add_vertex(-s, -s, s)
    geo.add_vertex(s, -s, s)
    geo.add_vertex(s, s, s)
    geo.add_vertex(-s, s, s)
    faces = [
        [0, 1, 2, 3],
        [4, 5, 6, 7],
        [0, 1, 5, 4],
        [2, 3, 7, 6],
        [0, 3, 7, 4],
        [1, 2, 6, 5],
    ]
    for f in faces:
        geo.add_face(f)
    return geo


def create_pyramid(size=1.0):
    geo = Geometry3D("pyramid")
    s = size / 2.0
    h = size
    geo.add_vertex(0, h, 0)
    geo.add_vertex(-s, 0, -s)
    geo.add_vertex(s, 0, -s)
    geo.add_vertex(s, 0, s)
    geo.add_vertex(-s, 0, s)
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [0, 3, 4],
        [0, 4, 1],
        [1, 2, 3, 4],
    ]
    for f in faces:
        geo.add_face(f)
    return geo


def create_sphere(radius=1.0, segments=16, rings=16):
    geo = Geometry3D("sphere")
    vertices = []
    for r in range(rings + 1):
        theta = math.pi * r / rings
        for s in range(segments + 1):
            phi = 2 * math.pi * s / segments
            x = radius * math.sin(theta) * math.cos(phi)
            y = radius * math.cos(theta)
            z = radius * math.sin(theta) * math.sin(phi)
            vertices.append(Vec3(x, y, z))
            geo.add_vertex(x, y, z)
    for r in range(rings):
        for s in range(segments):
            a = r * (segments + 1) + s
            b = a + segments + 1
            geo.add_face([a, b, b + 1, a + 1])
    return geo


def create_torus(radius_major=1.0, radius_minor=0.3, segments_major=24, segments_minor=16):
    geo = Geometry3D("torus")
    for i in range(segments_major):
        theta = 2 * math.pi * i / segments_major
        for j in range(segments_minor):
            phi = 2 * math.pi * j / segments_minor
            x = (radius_major + radius_minor * math.cos(phi)) * math.cos(theta)
            y = radius_minor * math.sin(phi)
            z = (radius_major + radius_minor * math.cos(phi)) * math.sin(theta)
            geo.add_vertex(x, y, z)
    for i in range(segments_major):
        for j in range(segments_minor):
            a = i * segments_minor + j
            b = ((i + 1) % segments_major) * segments_minor + j
            c = ((i + 1) % segments_major) * segments_minor + (j + 1) % segments_minor
            d = i * segments_minor + (j + 1) % segments_minor
            geo.add_face([a, b, c, d])
    return geo


def create_octahedron(size=1.0):
    geo = Geometry3D("octahedron")
    s = size
    geo.add_vertex(s, 0, 0)
    geo.add_vertex(-s, 0, 0)
    geo.add_vertex(0, s, 0)
    geo.add_vertex(0, -s, 0)
    geo.add_vertex(0, 0, s)
    geo.add_vertex(0, 0, -s)
    faces = [
        [0, 2, 4],
        [0, 4, 3],
        [0, 3, 5],
        [0, 5, 2],
        [1, 2, 5],
        [1, 5, 3],
        [1, 3, 4],
        [1, 4, 2],
    ]
    for f in faces:
        geo.add_face(f)
    return geo


def create_dodecahedron(size=1.0):
    geo = Geometry3D("dodecahedron")
    phi = (1 + math.sqrt(5)) / 2
    s = size
    points = [
        (-1, -1, -1), (-1, -1, 1), (-1, 1, -1), (-1, 1, 1),
        (1, -1, -1), (1, -1, 1), (1, 1, -1), (1, 1, 1),
        (0, -1/phi, -phi), (0, -1/phi, phi), (0, 1/phi, -phi), (0, 1/phi, phi),
        (-1/phi, -phi, 0), (-1/phi, phi, 0), (1/phi, -phi, 0), (1/phi, phi, 0),
        (-phi, 0, -1/phi), (-phi, 0, 1/phi), (phi, 0, -1/phi), (phi, 0, 1/phi),
    ]
    for p in points:
        geo.add_vertex(p[0] * s, p[1] * s, p[2] * s)
    faces = [
        [0, 8, 4, 14, 12],
        [0, 12, 1, 17, 16],
        [0, 16, 2, 10, 8],
        [1, 9, 5, 19, 17],
        [1, 12, 14, 5, 9],
        [2, 11, 6, 10, 16],
        [2, 17, 19, 6, 11],
        [3, 13, 7, 11, 15],
        [3, 15, 18, 4, 9],
        [3, 9, 1, 17, 13],
        [4, 18, 5, 14, 8],
        [5, 19, 18, 15, 14],
        [6, 19, 5, 18, 15],
        [6, 10, 8, 4, 18],
        [7, 13, 17, 19, 6],
        [7, 11, 2, 16, 13],
    ]
    for f in faces:
        geo.add_face(f)
    return geo


def create_icosahedron(size=1.0):
    geo = Geometry3D("icosahedron")
    phi = (1 + math.sqrt(5)) / 2
    points = [
        (0, 1, phi), (0, 1, -phi), (0, -1, phi), (0, -1, -phi),
        (1, phi, 0), (1, -phi, 0), (-1, phi, 0), (-1, -phi, 0),
        (phi, 0, 1), (phi, 0, -1), (-phi, 0, 1), (-phi, 0, -1),
    ]
    for p in points:
        geo.add_vertex(p[0] * size, p[1] * size, p[2] * size)
    faces = [
        [0, 2, 8], [0, 8, 4], [0, 4, 6], [0, 6, 10], [0, 10, 2],
        [3, 1, 9], [3, 9, 5], [3, 5, 7], [3, 7, 11], [3, 11, 1],
        [1, 4, 9], [1, 6, 4], [1, 11, 6], [1, 9, 11],
        [2, 5, 8], [2, 7, 5], [2, 10, 7], [2, 8, 10],
        [4, 8, 9], [5, 9, 8], [6, 7, 11], [7, 6, 10],
    ]
    for f in faces:
        geo.add_face(f)
    return geo


def create_icosahedron_subdivided(size=1.0, subdivisions=2):
    geo = create_icosahedron(size)
    for _ in range(subdivisions):
        new_faces = []
        for face in geo.faces:
            if len(face) == 3:
                v0 = geo.vertices[face[0]]
                v1 = geo.vertices[face[1]]
                v2 = geo.vertices[face[2]]
                a = len(geo.vertices)
                m01 = ((v0 + v1) * 0.5).normalize() * size
                m12 = ((v1 + v2) * 0.5).normalize() * size
                m20 = ((v2 + v0) * 0.5).normalize() * size
                geo.vertices.extend([m01, m12, m20])
                new_faces.extend([
                    [face[0], a, a + 2],
                    [face[1], a + 1, a],
                    [face[2], a + 2, a + 1],
                    [a, a + 1, a + 2],
                ])
        geo.faces = new_faces
    return geo


# ═══════════════════════════════════════════════════════════════════════════════════
# SCÈNE 3D
# ═══════════════════════════════════════════════════════════════════════════════════
class Scene3D:
    def __init__(self, name="default"):
        self.name = name
        self.objects = []
        self.camera_pos = Vec3(5, 5, 5)
        self.camera_target = Vec3(0, 0, 0)
        self.camera_up = Vec3(0, 1, 0)
        self.fov = 60
        self.near = 0.1
        self.far = 100.0
        self.light_pos = Vec3(10, 10, 10)
        self.background_color = "black"

    def add(self, obj):
        self.objects.append(obj)

    def remove(self, name):
        self.objects = [o for o in self.objects if o.name != name]

    def list_objects(self):
        if not self.objects:
            warning("La scène est vide.")
            return
        for idx, obj in enumerate(self.objects, 1):
            print(f"  {Fore.CYAN}[{idx}]{Style.RESET_ALL} {obj.name} | pos={obj.position} | faces={len(obj.faces)}")

    def rotate_all(self, rx=0.0, ry=0.0, rz=0.0):
        for obj in self.objects:
            obj.rotation.x += rx
            obj.rotation.y += ry
            obj.rotation.z += rz

    def animate_rotation(self, steps=60, delay=0.05):
        if plt is None or np is None:
            error("matplotlib et numpy sont requis pour l'animation 3D.")
            return
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        for _ in range(steps):
            ax.clear()
            ax.set_facecolor('black')
            ax.set_title('GEO3D MASTER - Animation Verte', color='green')
            self.rotate_all(0.05, 0.1, 0.02)
            render_scene_to_axes(self, ax, animated=True)
            plt.pause(delay)
        plt.close()


# ═══════════════════════════════════════════════════════════════════════════════════
# RENDU MATPLOTLIB
# ═══════════════════════════════════════════════════════════════════════════════════
def render_scene_to_axes(scene, ax, animated=False):
    if np is None:
        return
    ax.set_xlabel('X', color='green')
    ax.set_ylabel('Y', color='green')
    ax.set_zlabel('Z', color='green')
    ax.tick_params(colors='green')
    all_x, all_y, all_z = [], [], []
    for obj in scene.objects:
        faces = obj.get_face_vertices()
        for face in faces:
            xs = [v.x for v in face]
            ys = [v.y for v in face]
            zs = [v.z for v in face]
            all_x.extend(xs)
            all_y.extend(ys)
            all_z.extend(zs)
            verts = [list(zip(xs, ys, zs))]
            poly3d = Poly3DCollection(verts, alpha=0.6, facecolor=obj.color, edgecolor='lime', linewidth=0.5)
            ax.add_collection3d(poly3d)
    if all_x:
        margin = 1.5
        ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
        ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
        ax.set_zlim(min(all_z) - margin, max(all_z) + margin)
    if not animated:
        plt.show()


def render_scene(scene):
    if plt is None or np is None:
        error("matplotlib et numpy sont requis. Installez : pip install matplotlib numpy")
        return
    header(f"Rendu 3D : {scene.name}")
    progress("Génération de la scène", total=50)
    fig = plt.figure(figsize=(12, 9))
    fig.patch.set_facecolor('black')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('black')
    ax.set_title('GEO3D MASTER - Espace Géométrique', color='green', fontsize=16)
    render_scene_to_axes(scene, ax)
    log_event("RENDER", "scene", scene.name)


# ═══════════════════════════════════════════════════════════════════════════════════
# CAMÉRA (OPTIONNELLE ET EXPLICITE)
# ═══════════════════════════════════════════════════════════════════════════════════
def check_camera():
    global CAMERA_ENABLED, CAMERA_SOURCE
    try:
        import cv2
        CAMERA_SOURCE = cv2
        CAMERA_ENABLED = True
        success("Caméra détectée. Activation possible via le menu.")
        log_event("CAMERA", "detected")
    except ImportError:
        CAMERA_ENABLED = False
        warning("OpenCV non installé. Mode caméra désactivé.")
        log_event("CAMERA", "not_available")


def camera_preview(duration=5):
    global CAMERA_ENABLED, CAMERA_SOURCE
    if not CAMERA_ENABLED or CAMERA_SOURCE is None:
        warning("Caméra non disponible. Affichage d'une géométrie de remplacement.")
        show_face_geometry()
        return
    header("Aperçu caméra (consentement requis)")
    consent = prompt("Activer la caméra temporairement ? (oui/non) : ").lower()
    if consent not in ("oui", "o", "yes", "y"):
        info("Caméra non activée.")
        return
    cap = CAMERA_SOURCE.VideoCapture(0)
    if not cap.isOpened():
        error("Impossible d'ouvrir la caméra.")
        return
    info(f"Aperçu pendant {duration} secondes...")
    start = time.time()
    while time.time() - start < duration:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('GEO3D MASTER - Camera Preview', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    success("Aperçu caméra terminé.")
    log_event("CAMERA", "preview", f"duration={duration}")


def show_face_geometry():
    header("Géométrie faciale simulée (sans caméra)")
    progress("Construction du maillage facial", total=80)
    scene = Scene3D("face_geometry")
    # Créer une représentation géométrique stylisée de visage
    head = create_sphere(1.5, 12, 12)
    head.color = "darkgreen"
    head.position = Vec3(0, 0, 0)
    eye1 = create_sphere(0.2, 8, 8)
    eye1.color = "lime"
    eye1.position = Vec3(-0.5, 0.4, 1.2)
    eye2 = create_sphere(0.2, 8, 8)
    eye2.color = "lime"
    eye2.position = Vec3(0.5, 0.4, 1.2)
    nose = create_pyramid(0.4)
    nose.color = "green"
    nose.position = Vec3(0, 0, 1.3)
    mouth = create_torus(0.4, 0.05, 16, 8)
    mouth.color = "lime"
    mouth.position = Vec3(0, -0.5, 1.2)
    scene.add(head)
    scene.add(eye1)
    scene.add(eye2)
    scene.add(nose)
    scene.add(mouth)
    success("Géométrie faciale générée.")
    render_scene(scene)


# ═══════════════════════════════════════════════════════════════════════════════════
# SCÈNES PRÉDÉFINIES
# ═══════════════════════════════════════════════════════════════════════════════════
def scene_geometric_universe():
    scene = Scene3D("geometric_universe")
    cube = create_cube(1.5)
    cube.color = "forestgreen"
    cube.position = Vec3(-2, 0, 0)
    sphere = create_sphere(1.0, 16, 16)
    sphere.color = "limegreen"
    sphere.position = Vec3(2, 0, 0)
    pyramid = create_pyramid(1.5)
    pyramid.color = "darkgreen"
    pyramid.position = Vec3(0, 2, 0)
    torus = create_torus(1.0, 0.3, 24, 16)
    torus.color = "green"
    torus.position = Vec3(0, -2, 0)
    octa = create_octahedron(1.0)
    octa.color = "springgreen"
    octa.position = Vec3(0, 0, 2)
    scene.add(cube)
    scene.add(sphere)
    scene.add(pyramid)
    scene.add(torus)
    scene.add(octa)
    return scene


def scene_platonic_solids():
    scene = Scene3D("platonic_solids")
    positions = [
        (Vec3(-3, 0, 0), "tetra"),
        (Vec3(-1.5, 0, 0), "cube"),
        (Vec3(0, 0, 0), "octa"),
        (Vec3(1.5, 0, 0), "dodeca"),
        (Vec3(3, 0, 0), "icosa"),
    ]
    creators = {
        "tetra": create_pyramid,
        "cube": create_cube,
        "octa": create_octahedron,
        "dodeca": create_dodecahedron,
        "icosa": create_icosahedron,
    }
    colors = ["lime", "green", "darkgreen", "forestgreen", "springgreen"]
    for (pos, key), color in zip(positions, colors):
        obj = creators[key](0.8)
        obj.color = color
        obj.position = pos
        scene.add(obj)
    return scene


def scene_molecular():
    scene = Scene3D("molecular")
    center_atom = create_sphere(1.0, 16, 16)
    center_atom.color = "green"
    scene.add(center_atom)
    for i in range(6):
        angle = 2 * math.pi * i / 6
        atom = create_sphere(0.4, 12, 12)
        atom.color = "lime"
        atom.position = Vec3(math.cos(angle) * 2, math.sin(angle) * 2, 0)
        scene.add(atom)
        bond = create_cube(0.1)
        bond.color = "darkgreen"
        bond.position = Vec3(math.cos(angle), math.sin(angle), 0)
        bond.scale = Vec3(20, 1, 1)
        bond.rotation.z = angle
        scene.add(bond)
    return scene


def scene_galaxy():
    scene = Scene3D("galaxy")
    for i in range(200):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0.5, 5)
        star = create_sphere(random.uniform(0.03, 0.1), 6, 6)
        star.color = random.choice(["green", "lime", "springgreen", "palegreen"])
        star.position = Vec3(
            math.cos(angle) * radius,
            random.uniform(-0.5, 0.5),
            math.sin(angle) * radius,
        )
        scene.add(star)
    return scene


# ═══════════════════════════════════════════════════════════════════════════════════
# GÉNÉRATEURS PROCÉDURAUX
# ═══════════════════════════════════════════════════════════════════════════════════
def generate_terrain(size=10, resolution=30):
    scene = Scene3D("terrain")
    step = size / resolution
    for i in range(resolution):
        for j in range(resolution):
            x = -size / 2 + i * step
            z = -size / 2 + j * step
            y = math.sin(x) * math.cos(z) * 0.5 + random.uniform(-0.1, 0.1)
            block = create_cube(step * 0.9)
            block.color = "green"
            block.position = Vec3(x, y, z)
            block.scale.y = 0.2 + abs(y)
            scene.add(block)
    return scene


def generate_fractal_tree(depth=4, length=2.0, angle=0.5):
    scene = Scene3D("fractal_tree")
    def branch(pos, direction, depth, length):
        if depth == 0:
            return
        end = pos + direction * length
        cyl = create_cube(0.1)
        cyl.color = "green"
        mid = (pos + end) * 0.5
        cyl.position = mid
        cyl.scale = Vec3(1, length * 5, 1)
        cyl.rotation.x = math.atan2(direction.z, direction.y)
        cyl.rotation.z = math.atan2(direction.x, direction.y)
        scene.add(cyl)
        branch(end, direction + Vec3(angle, 0.5, 0).normalize(), depth - 1, length * 0.7)
        branch(end, direction + Vec3(-angle, 0.5, 0).normalize(), depth - 1, length * 0.7)
    branch(Vec3(0, -2, 0), Vec3(0, 1, 0), depth, length)
    return scene


def generate_spiral_tower(height=10, segments=40):
    scene = Scene3D("spiral_tower")
    for i in range(segments):
        t = i / segments
        angle = t * 4 * math.pi
        radius = 1 + t * 2
        y = -height / 2 + t * height
        obj = create_cube(0.5)
        obj.color = random.choice(["green", "lime", "springgreen"])
        obj.position = Vec3(math.cos(angle) * radius, y, math.sin(angle) * radius)
        obj.rotation.y = angle
        scene.add(obj)
    return scene


def generate_wireframe_sphere(radius=2.0, segments=24):
    scene = Scene3D("wireframe_sphere")
    sphere = create_sphere(radius, segments, segments)
    sphere.color = "green"
    sphere.wireframe = True
    scene.add(sphere)
    return scene


# ═══════════════════════════════════════════════════════════════════════════════════
# TRANSFORMATIONS & UTILITAIRES 3D
# ═══════════════════════════════════════════════════════════════════════════════════
def apply_transform_menu(obj):
    header("Transformation de l'objet")
    print(f"  Position actuelle : {obj.position}")
    print(f"  Rotation actuelle : {obj.rotation}")
    print(f"  Échelle actuelle  : {obj.scale}")
    tx = prompt("Translation X : ") or "0"
    ty = prompt("Translation Y : ") or "0"
    tz = prompt("Translation Z : ") or "0"
    rx = prompt("Rotation X (degrés) : ") or "0"
    ry = prompt("Rotation Y (degrés) : ") or "0"
    rz = prompt("Rotation Z (degrés) : ") or "0"
    sx = prompt("Échelle X : ") or "1"
    sy = prompt("Échelle Y : ") or "1"
    sz = prompt("Échelle Z : ") or "1"
    try:
        obj.position += Vec3(float(tx), float(ty), float(tz))
        obj.rotation += Vec3(math.radians(float(rx)), math.radians(float(ry)), math.radians(float(rz)))
        obj.scale = Vec3(float(sx), float(sy), float(sz))
        success("Transformation appliquée.")
        log_event("TRANSFORM", "apply", obj.name)
    except ValueError:
        error("Valeurs numériques invalides.")


def calculate_distance(v1, v2):
    return (v1 - v2).length()


def calculate_volume_cube(size):
    return size ** 3


def calculate_volume_sphere(radius):
    return (4 / 3) * math.pi * radius ** 3


def calculate_surface_area_sphere(radius):
    return 4 * math.pi * radius ** 2


# ═══════════════════════════════════════════════════════════════════════════════════
# MENUS ET INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════════
MAIN_MENU = [
    ("🏠 Scènes prédéfinies", "scene_menu"),
    ("🔧 Créer un objet géométrique", "create_menu"),
    ("🎨 Générateurs procéduraux", "procedural_menu"),
    ("📐 Transformations & calculs", "transform_menu"),
    ("🎥 Animation automatique", "animation_menu"),
    ("📷 Caméra / Géométrie faciale", "camera_menu"),
    ("📄 Rapports & informations", "report_menu"),
    ("🌧 Animation Matrix", "matrix_animation"),
    ("❌ Quitter", "exit"),
]


def scene_menu():
    header("Scènes prédéfinies")
    print("  [1] Univers géométrique")
    print("  [2] Solides platoniciens")
    print("  [3] Structure moléculaire")
    print("  [4] Galaxie verte")
    c = prompt("Choix : ")
    scenes = {
        "1": scene_geometric_universe,
        "2": scene_platonic_solids,
        "3": scene_molecular,
        "4": scene_galaxy,
    }
    if c in scenes:
        scene = scenes[c]()
        render_scene(scene)
        log_event("SCENE", "load", scene.name)
    else:
        error("Choix invalide.")


def create_menu():
    header("Créer un objet géométrique")
    print("  [1] Cube")
    print("  [2] Sphère")
    print("  [3] Pyramide")
    print("  [4] Torus")
    print("  [5] Octaèdre")
    print("  [6] Dodécaèdre")
    print("  [7] Icosaèdre")
    print("  [8] Icosaèdre subdivisé")
    c = prompt("Choix : ")
    size = prompt("Taille / Rayon : ") or "1"
    try:
        size = float(size)
    except ValueError:
        size = 1.0
    creators = {
        "1": lambda: create_cube(size),
        "2": lambda: create_sphere(size, 16, 16),
        "3": lambda: create_pyramid(size),
        "4": lambda: create_torus(size, size * 0.3),
        "5": lambda: create_octahedron(size),
        "6": lambda: create_dodecahedron(size),
        "7": lambda: create_icosahedron(size),
        "8": lambda: create_icosahedron_subdivided(size, 1),
    }
    if c in creators:
        obj = creators[c]()
        obj.color = "green"
        scene = Scene3D("custom_object")
        scene.add(obj)
        render_scene(scene)
        log_event("CREATE", "object", obj.name)
    else:
        error("Choix invalide.")


def procedural_menu():
    header("Générateurs procéduraux")
    print("  [1] Terrain 3D")
    print("  [2] Arbre fractal")
    print("  [3] Tour spirale")
    print("  [4] Sphère filaire")
    c = prompt("Choix : ")
    if c == "1":
        scene = generate_terrain()
    elif c == "2":
        scene = generate_fractal_tree()
    elif c == "3":
        scene = generate_spiral_tower()
    elif c == "4":
        scene = generate_wireframe_sphere()
    else:
        error("Choix invalide.")
        return
    render_scene(scene)
    log_event("PROCEDURAL", "generate", scene.name)


def transform_menu():
    header("Transformations & calculs")
    print("  [1] Distance entre deux points")
    print("  [2] Volume d'un cube")
    print("  [3] Volume d'une sphère")
    print("  [4] Surface d'une sphère")
    print("  [5] Info sur les vecteurs")
    c = prompt("Choix : ")
    if c == "1":
        x1 = float(prompt("X1 : ") or "0")
        y1 = float(prompt("Y1 : ") or "0")
        z1 = float(prompt("Z1 : ") or "0")
        x2 = float(prompt("X2 : ") or "1")
        y2 = float(prompt("Y2 : ") or "1")
        z2 = float(prompt("Z2 : ") or "1")
        d = calculate_distance(Vec3(x1, y1, z1), Vec3(x2, y2, z2))
        success(f"Distance : {d:.4f}")
    elif c == "2":
        s = float(prompt("Côté : ") or "1")
        success(f"Volume : {calculate_volume_cube(s):.4f}")
    elif c == "3":
        r = float(prompt("Rayon : ") or "1")
        success(f"Volume : {calculate_volume_sphere(r):.4f}")
    elif c == "4":
        r = float(prompt("Rayon : ") or "1")
        success(f"Surface : {calculate_surface_area_sphere(r):.4f}")
    elif c == "5":
        v1 = Vec3(1, 2, 3)
        v2 = Vec3(4, 5, 6)
        info(f"v1 = {v1}")
        info(f"v2 = {v2}")
        info(f"v1 + v2 = {v1 + v2}")
        info(f"v1 · v2 = {v1.dot(v2)}")
        info(f"v1 × v2 = {v1.cross(v2)}")
    else:
        error("Choix invalide.")


def animation_menu():
    header("Animation automatique")
    scene = scene_geometric_universe()
    info("Animation en cours... Fermez la fenêtre matplotlib pour continuer.")
    scene.animate_rotation(steps=60, delay=0.05)
    log_event("ANIMATION", "rotation", scene.name)


def camera_menu():
    header("Caméra / Géométrie faciale")
    print("  [1] Aperçu caméra (avec consentement)")
    print("  [2] Géométrie faciale simulée (sans caméra)")
    print("  [3] Vérifier la disponibilité caméra")
    c = prompt("Choix : ")
    if c == "1":
        camera_preview()
    elif c == "2":
        show_face_geometry()
    elif c == "3":
        check_camera()
    else:
        error("Choix invalide.")


def report_menu():
    header("Rapports & informations")
    print("  [1] Sauvegarder rapport JSON")
    print("  [2] Informations système")
    print("  [3] Afficher les événements")
    c = prompt("Choix : ")
    if c == "1":
        filename = f"geo3d_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        data = {
            "generated_at": ts_iso(),
            "version": VERSION,
            "author": AUTHOR,
            "events": SESSION_LOG,
            "camera_enabled": CAMERA_ENABLED,
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        success(f"Rapport sauvegardé : {filename}")
        log_event("REPORT", "save", filename)
    elif c == "2":
        info(f"OS : {os.name}")
        info(f"Machine : {socket.gethostname()}")
        info(f"Python : {sys.version.split()[0]}")
        info(f"GEO3D Master : {VERSION}")
        info(f"Caméra disponible : {CAMERA_ENABLED}")
    elif c == "3":
        for e in SESSION_LOG[-20:]:
            print(f"  [{e['timestamp'][:19]}] {e['category']} | {e['action']} | {e['detail']}")
    else:
        error("Choix invalide.")


def matrix_animation():
    header("Animation Matrix")
    matrix_rain(duration=3.0)
    success("Animation terminée.")


def auto_setup():
    info("Initialisation automatique de GEO3D Master...")
    progress("Chargement du moteur 3D", total=100)
    check_camera()
    success("Initialisation terminée.")
    log_event("SYSTEM", "auto_setup")


# ═══════════════════════════════════════════════════════════════════════════════════
# BOUCLE PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description="GEO3D Master - Visualisation 3D géométrique")
    parser.add_argument("--auto", action="store_true", help="Lancer automatiquement")
    parser.add_argument("--scene", type=str, default="", help="Nom de scène à charger")
    args = parser.parse_args()

    banner()
    auto_setup()

    if args.scene:
        scenes = {
            "universe": scene_geometric_universe,
            "platonic": scene_platonic_solids,
            "molecular": scene_molecular,
            "galaxy": scene_galaxy,
        }
        if args.scene in scenes:
            render_scene(scenes[args.scene]())

    while True:
        banner()
        print(f"\n{Fore.GREEN}{Style.BRIGHT}═══ MENU PRINCIPAL GEO3D MASTER ═══{Style.RESET_ALL}\n")
        for idx, (label, _) in enumerate(MAIN_MENU, 1):
            print(f"  {Fore.CYAN}[{idx}]{Style.RESET_ALL} {label}")

        choice = prompt("Choix : ")

        if choice == "9" or choice.lower() in ("quit", "exit", "q"):
            info("Fermeture de GEO3D Master. À bientôt dans l'espace !")
            log_event("SYSTEM", "shutdown", "user_exit")
            sys.exit(0)

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(MAIN_MENU):
                action = MAIN_MENU[idx][1]
                if action == "scene_menu":
                    scene_menu()
                elif action == "create_menu":
                    create_menu()
                elif action == "procedural_menu":
                    procedural_menu()
                elif action == "transform_menu":
                    transform_menu()
                    pause()
                elif action == "animation_menu":
                    animation_menu()
                elif action == "camera_menu":
                    camera_menu()
                elif action == "report_menu":
                    report_menu()
                elif action == "matrix_animation":
                    matrix_animation()
                    pause()
            else:
                error("Choix invalide.")
                time.sleep(0.5)
        except ValueError:
            error("Entrée invalide.")
            time.sleep(0.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        warning("Interruption par l'utilisateur. Au revoir !")
        log_event("SYSTEM", "shutdown", "keyboard_interrupt")
        sys.exit(0)
