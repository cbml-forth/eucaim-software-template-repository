from radiomics import featureextractor
from pathlib import Path
from typing import List
import six
import SimpleITK as sitk

class RadiomicsExtractor:
    def __init__(self, params_file) -> None:
        self.params_file = params_file
        # log.debug(params_file)
        self.__extractor = featureextractor.RadiomicsFeatureExtractor(params_file)
    
    def __extract_feature_vector(self, image_name: str | sitk.Image, mask_name: str | sitk.Image, peritumoral: bool=False, skip_diagnostics=True, **kwargs):
        feature_vector = self.__extractor.execute(image_name, mask_name)
        
        radiomics = {}
        for key, value in six.iteritems(feature_vector):
            if skip_diagnostics:
                if (not 'diagnostics_' in key):
                    if peritumoral:
                        radiomics[f"peritumoral_{key}"] = value
                    else:
                        radiomics[key] = value
            else:
                radiomics = feature_vector
                break        
        
        return radiomics
    
    def extract(self, image: str | List[str] | Path | List[Path], mask: str  | List[str] | Path | List[Path], peritumoral: bool=False, **kwargs):
        if isinstance(image, sitk.Image) and isinstance(mask, sitk.Image):
            return self.__extract_feature_vector(image, mask, peritumoral, **kwargs)
        elif isinstance(image, list) and isinstance(mask, list) and (len(image) == len(mask)) and len(image) > 0:
            return [self.__extract_feature_vector(str(image[i]), str(mask[i]), peritumoral, **kwargs) for i in range(len(image))]
        elif (isinstance(image, str) and isinstance(mask, str)) or (isinstance(image, Path) and isinstance(mask, Path)):
            return self.__extract_feature_vector(str(image), str(mask), peritumoral, **kwargs)
        
        raise ValueError('Invalid input for radiomics extraction')
    