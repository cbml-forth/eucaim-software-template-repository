import SimpleITK as sitk
from numpy.typing import NDArray

class SitkReader():
    def read(self, path='', **kwargs) -> NDArray:
        returnObject = kwargs.get("returnObject", False)
        returnSpacing = kwargs.get("returnSpacing", False)
        try:
            image = sitk.ReadImage(path)
            if returnObject:
                return image
            
            if returnSpacing:
                return sitk.GetArrayFromImage(image).squeeze(), image.GetSpacing()
            return sitk.GetArrayFromImage(image).squeeze()
        except Exception as e:
            # self.log.error(f'Could not read image file with SimpleITK.')
            # self.log.exception(e)
            raise e