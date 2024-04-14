import io

import numpy as np
from PIL import Image
from sqlalchemy import select
from torch import Tensor
from torchvision.models import Inception3
from torchvision.transforms import Compose

from museum_img_searcher.domain import ImgVector


def search(file: io.BytesIO, encoder: Inception3, transform: Compose, session, classificator) -> tuple[str, list[str]]:
    vector: Tensor = encoder(transform(Image.open(file)).unsqueeze(0))

    classificator_id: np.ndarray = classificator.predict(vector.detach().numpy())
    classificators = np.array(['Археология', 'Графика', 'ДПИ', 'Документы',
                               'Естественнонауч.коллекция', 'Живопись', 'Минералогия',
                               'Нумизматика', 'Оружие', 'Печатная продукция', 'Прочие',
                               'Редкие книги', 'Скульптура', 'Техника', 'Фото, негативы'],
                              dtype='<U25')
    classif = str(classificators[classificator_id][0])

    with session() as s:
        values = s.execute(
            select(ImgVector).order_by(ImgVector.vector.l2_distance(vector.tolist()[0])).limit(10)
        ).scalars().all()

    return classif, [str(value.exhibit_id) for value in values]
