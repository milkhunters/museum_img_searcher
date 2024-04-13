import io
from uuid import UUID

import torch
from PIL import Image
from torch import Tensor
from torchvision import transforms, models as mdls
from torchvision.models import Inception3
from torchvision.transforms import Compose

from museum_img_searcher.config import load_config
from museum_img_searcher.db import create_psql_session
from museum_img_searcher.domain.img_vector import ImgVector


def add(file: io.BytesIO, exhibit_id: str, encoder: Inception3, transform: Compose, session):
    vector: Tensor = encoder(transform(Image.open(file)).unsqueeze(0))
    print(vector)
    print(exhibit_id)

    with session() as s:
        item = ImgVector(
            exhibit_id=UUID(exhibit_id),
            vector=vector,
        )
        s.add(item)
        s.commit()


if __name__ == "__main__":
    config = load_config()

    # Load model
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((256, 256), antialias=True),
        transforms.ConvertImageDtype(torch.float),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])

    encoder = mdls.inception_v3(pretrained=True, aux_logits=True)
    encoder.eval()

    lazy_session = create_psql_session(
        config.POSTGRESQL.USERNAME,
        config.POSTGRESQL.PASSWORD,
        config.POSTGRESQL.HOST,
        config.POSTGRESQL.PORT,
        config.POSTGRESQL.DATABASE,
        echo=config.DEBUG,
    )[1]

    add(
        io.BytesIO(open("3837069.jpg", "rb").read()),
        "22d933a7-391d-43e0-b179-2320043db20a",
        encoder,
        transform,
        lazy_session,
    )
