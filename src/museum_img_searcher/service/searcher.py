import io

from PIL import Image
from sqlalchemy import select
from torch import Tensor
from torchvision.models import Inception3
from torchvision.transforms import Compose

from museum_img_searcher.domain import ImgVector


def search(file: io.BytesIO, encoder: Inception3, transform: Compose, session) -> list[str]:
    vector: Tensor = encoder(transform(Image.open(file)).unsqueeze(0))

    with session() as s:
        values = s.execute(
            select(ImgVector).order_by(ImgVector.vector.l2_distance(vector.tolist()[0])).limit(10)
        ).scalars().all()

    return [str(value.exhibit_id) for value in values]
