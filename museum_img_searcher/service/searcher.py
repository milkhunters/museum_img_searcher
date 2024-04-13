import io


def search(image: io.BytesIO) -> list[str]:
    print(image)
    # ... some image processing code ...
    print("что-то")

    return ["8b58cfd8-bb11-4704-b5dc-9f02b7c2ed47"]


if __name__ == "__main__":
    with open("museum_img_searcher/images/22d933a7-391d-43e0-b179-2320043db20a.jpg", "rb") as file:
        print(search(io.BytesIO(file.read())))
