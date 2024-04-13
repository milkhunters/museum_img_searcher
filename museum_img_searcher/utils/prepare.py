import io
from torch.utils.data import DataLoader
from datasets import load_dataset
from torch.utils.data import DataLoader
from torchvision import transforms
import torch
from PIL import Image
import numpy as np
from torch.utils.data import Dataset


class SqueezeAndToNumpy:
    """
    Принимает тензор, который имеет размерность (1, H, W) и возвращает numpy-массив размерности (H, W)
    """
    def __call__(self, tensor):
        if tensor.dim() == 3:
            squeezed_tensor = tensor.permute(1, 2, 0)[:, :, 0].unsqueeze(0)
        else:
            squeezed_tensor = tensor
        return squeezed_tensor
    
def get_image_from_bytes(image_bytes):
    """
    Принимает массив байтов, возвращает PIL-изображение
    """
    return Image.open(io.BytesIO(image_bytes))

def transform_images(samples, size=(256, 256), transformer=None):
        """
        Пайплайн для трансформации данных. Трансформирует изображения
        """
        if transformer is None:
            transformer = transforms.Compose([
                
                transforms.PILToTensor(),
                transforms.Resize(size),
                transforms.ConvertImageDtype(torch.float),
                SqueezeAndToNumpy()
            ])
        
        images = [sample['image'] for sample in samples]
        object_names = [sample['object_name'] for sample in samples]

        transformed_images = [transformer(image) for image in images]
        return np.array(transformed_images), object_names

def get_data_loader(dataset):

    transform = transforms.Compose([
        transforms.PILToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        transforms.Resize((256, 256)),
        transforms.ConvertImageDtype(torch.float),
        SqueezeAndToNumpy()
    ])

    transformed_collate_fn = functools.partial(transform_data, transformer=transform)

    dataloader = DataLoader(museum_staff, batch_size=4, collate_fn=transformed_collate_fn)
    return dataloader


train_dataset = Dataset()