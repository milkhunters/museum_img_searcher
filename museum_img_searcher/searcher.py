import io


def search(image: io.BytesIO) -> list[str]:

    # ... some image processing code ...

    return ["dd9b505c-3cd9-4444-bd83-6456e2107441", "22d933a7-391d-43e0-b179-2320043db20a"]


if __name__ == "__main__":
    with open("museum_img_searcher/images/22d933a7-391d-43e0-b179-2320043db20a.jpg", "rb") as file:
        print(search(io.BytesIO(file.read())))
