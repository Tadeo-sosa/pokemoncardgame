import os

import flet as ft
import httpx

SERVER_URL = os.environ.get("SERVER_URL", "http://localhost:8001")


def main(page: ft.Page):
    page.title = "🎨 PokéDraw"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    selected_file = {"path": None}

    # ---------------- IMAGEN ----------------
    img_preview = ft.Image(
        src="https://via.placeholder.com/300",
        width=300,
        height=300,
        visible=False,
    )

    # ---------------- TEXTOS ----------------
    status = ft.Text("Seleccioná una imagen")
    result_txt = ft.Text(size=18, weight="bold")

    # ---------------- MAZO ----------------
    deck_area = ft.Column(
        visible=False,
        scroll="auto",
        height=300,
    )

    # ---------------- FILE PICKER ----------------
    file_picker = ft.FilePicker()

    async def pick_file(e):
        files = await file_picker.pick_files(
            allow_multiple=False
        )
        if files:
            file_path = files[0].path

            selected_file["path"] = file_path

            img_preview.src = file_path
            img_preview.visible = True

            status.value = "✅ Imagen seleccionada"

            send_btn.disabled = False

            page.update()

    # ---------------- ENVIAR ----------------
    async def send_image(e):

        if not selected_file["path"]:
            status.value = "❌ Seleccioná una imagen"
            page.update()
            return

        try:
            status.value = "📡 Enviando..."
            page.update()

            with open(selected_file["path"], "rb") as f:
                file_bytes = f.read()

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{SERVER_URL}/upload",
                    files={
                        "file": (
                            "image.jpg",
                            file_bytes,
                            "image/jpeg",
                        )
                    },
                )

            data = response.json()

            result_txt.value = (
                f"🎴 Pokémon: {data['pokemon']}\n"
                f"❤️ HP: {data['hp']}\n"
                f"⚔️ ATK: {data['attack']}\n"
                f"🎯 Similaridad: {round(data['similarity'] * 100, 1)}%"
            )

            status.value = "✅ Carta creada"

        except Exception as ex:
            result_txt.value = ""
            status.value = f"❌ Error: {str(ex)}"

        page.update()

    # ---------------- VER MAZO ----------------
    async def show_deck(e):

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.get(
                    f"{SERVER_URL}/deck"
                )

            data = response.json()

            deck_area.controls.clear()

            cards = data["cards"]

            if len(cards) == 0:
                deck_area.controls.append(
                    ft.Text("🃏 El mazo está vacío")
                )

            for card in reversed(cards):

                card_ui = ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                f"🎴 {card['pokemon']}",
                                size=18,
                                weight="bold",
                            ),
                            ft.Text(f"❤️ HP: {card['hp']}"),
                            ft.Text(f"⚔️ ATK: {card['attack']}"),
                            ft.Text(
                                f"🎯 {round(card['similarity'] * 100, 1)}%"
                            ),
                        ]
                    ),
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.Colors.BLUE_GREY_900,
                )

                deck_area.controls.append(card_ui)

            deck_area.visible = True

            page.update()

        except Exception as ex:
            status.value = f"❌ No conecta con servidor: {str(ex)}"
            page.update()

    # ---------------- OCULTAR MAZO ----------------
    def hide_deck(e):
        deck_area.visible = False
        page.update()

    # ---------------- BOTONES ----------------
    btn_pick = ft.Button(
        "📁 Seleccionar imagen",
        on_click=pick_file,
    )

    send_btn = ft.Button(
        "📤 Enviar",
        on_click=send_image,
        disabled=True,
    )

    btn_deck = ft.Button(
        "🃏 Ver mazo",
        on_click=show_deck,
    )

    btn_hide = ft.Button(
        "❌ Ocultar mazo",
        on_click=hide_deck,
    )

    # ---------------- UI ----------------
    page.add(
        ft.Text(
            "🎨 PokéDraw",
            size=30,
            weight="bold",
        ),
        btn_pick,
        img_preview,
        send_btn,
        result_txt,
        status,
        ft.Row(
            [
                btn_deck,
                btn_hide,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        deck_area,
    )


ft.run(main)