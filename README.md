# PokéDraw - Pokémon Card Game

Juego de cartas Pokémon que usa inteligencia artificial (CLIP) para identificar dibujos de Pokémon y generar cartas con estadísticas basadas en la similitud del dibujo.

## Estructura del Proyecto

```
pokemoncardgame/
├── server/          # API FastAPI + modelo CLIP
│   ├── main.py      # Servidor principal
│   ├── deck.json    # Almacenamiento de cartas
│   └── requirements.txt
├── client/          # Interfaz gráfica con Flet
│   ├── main.py      # Cliente principal
│   └── requirements.txt
└── README.md
```

## Requisitos

- Python 3.10+

## Instalación

### Servidor

```bash
cd server
pip install -r requirements.txt
```

### Cliente

```bash
cd client
pip install -r requirements.txt
```

## Uso

### 1. Iniciar el servidor

```bash
cd server
python main.py
```

El servidor se inicia en `http://0.0.0.0:8001`.

### 2. Iniciar el cliente

```bash
cd client
python main.py
```

Por defecto, el cliente se conecta a `http://localhost:8001`. Para apuntar a otro servidor:

```bash
SERVER_URL=http://192.168.1.100:8001 python client/main.py
```

## Cómo Funciona

1. Dibujás o seleccionás una imagen de un Pokémon
2. El cliente la envía al servidor
3. El servidor usa el modelo CLIP para comparar tu dibujo con descripciones de 27 Pokémon
4. Se genera una carta con HP y ATK basados en la similaridad del dibujo
5. La carta se guarda en el mazo (`deck.json`)

## API Endpoints

| Método | Ruta      | Descripción                          |
|--------|-----------|--------------------------------------|
| GET    | `/`       | Info del servidor                    |
| GET    | `/health` | Estado de salud del servidor         |
| POST   | `/upload` | Subir imagen y generar carta         |
| GET    | `/deck`   | Ver todas las cartas del mazo        |
