import base64


def search(image_base64: str) -> list[str]:
    image_bytes = base64.b64decode(image_base64)

    # ... some image processing code ...

    return ["dd9b505c-3cd9-4444-bd83-6456e2107441", "22d933a7-391d-43e0-b179-2320043db20a"]


if __name__ == "__main__":
    with open("museum_img_searcher/images/22d933a7-391d-43e0-b179-2320043db20a.jpg", "rb") as file:
        print(base64.b64encode(file.read()).decode())
