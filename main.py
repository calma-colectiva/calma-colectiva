from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

templates = Jinja2Templates(directory="templates")

class Usuario(BaseModel):
    id: int
    nombre: str
    latitud: float
    longitud: float
    nivel_de_calma: int

usuarios: List[Usuario] = []

@app.get("/")
def inicio():
    return {"mensaje": "Calma Colectiva activa en Montevideo"}

@app.post("/usuarios/")
def crear_usuario(usuario: Usuario):
    for u in usuarios:
        if u.id == usuario.id:
            return {"error": "Ya existe un usuario con ese ID"}
    usuarios.append(usuario)
    return {"mensaje": "Usuario agregado", "usuario": usuario}

@app.get("/usuarios/")
def listar_usuarios():
    return usuarios

import math

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371  # Radio de la Tierra en km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon/2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@app.get("/cercanos/{usuario_id}")
def usuarios_cercanos(usuario_id: int, radio_metros: float = 200):

    usuario_base = None

    for u in usuarios:
        if u.id == usuario_id:
            usuario_base = u
            break

    if not usuario_base:
        return {"error": "Usuario no encontrado"}

    radio_km = radio_metros / 1000  # Convertir a km
    cercanos = []

    for u in usuarios:
        if u.id != usuario_id:
            distancia = calcular_distancia(
                usuario_base.latitud,
                usuario_base.longitud,
                u.latitud,
                u.longitud
            )

            if distancia <= radio_km:
                cercanos.append({
                    "id": u.id,
                    "nombre": u.nombre,
                    "distancia_metros": round(distancia * 1000, 1),
                    "nivel_de_calma": u.nivel_de_calma
                })

    return cercanos

@app.get("/form", response_class=HTMLResponse)
def mostrar_formulario(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})