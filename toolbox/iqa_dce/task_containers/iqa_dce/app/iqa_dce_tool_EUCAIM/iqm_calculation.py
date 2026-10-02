'''
    @Author: Aikaterini Dovrou
    @email: dovrou97@gmail.com
'''

import piq
import numpy as np
import torch
import warnings
warnings.filterwarnings("ignore") #, category=DeprecationWarning) 

def prepro(x:np.ndarray):
    '''
    Apply min-max normalization to 1 image (since the piq library expects values larger or equal to 0 in image) and convert it to a tensor
    Values should be between 0 and 1
        ...
        Parameters:
        x: numpy.ndarray
            The input image as 3D array of shape [SLICES, HEIGHT, WIDTH]
        
        Return:
        img_tensor_dce: torch.Tensor
            The min-max normalized image as a tensor of shape [SLICES, 1, HEIGHT, WIDTH]
    '''

    normalized_img=[]
    for i in range(x.shape[0]):
        normalized_img.append((x[i]-np.min(x[i]))/(np.max(x[i])-np.min(x[i])))
    normalized_img=np.asarray(normalized_img) 

    img_tensor = torch.Tensor(normalized_img)
    img_tensor = torch.unsqueeze(img_tensor, 1)   
 
    return img_tensor

def tensor_to_numpy(x:torch.Tensor):
    return round(float(x.cpu().detach().numpy()),2)

def tensor_to_numpy_array(x:torch.Tensor):
    return x.cpu().detach().numpy()

def calculate_fr_metrics(x:torch.Tensor, y:torch.Tensor):
    '''
    Calculate Full Reference (FR) Metrics 

        ...
        Parameters:
        x: torch.Tensor
            The input image
        y: torch.Tensor
            The reference image
        
        Return:
        metrics: dict
            A dictionary that contains the values of the FR metrics
    
    '''
    metrics = {}
    metrics['PSNR'] = np.round(tensor_to_numpy_array(piq.psnr(x, y, data_range=1., reduction='none')),2)
    metrics['SSIM'] = np.round(tensor_to_numpy_array(piq.ssim(x, y, data_range=1., reduction='none')),2)
    metrics['MS_SSIM'] = np.round(tensor_to_numpy_array(piq.multi_scale_ssim(x, y, data_range=1., reduction='none')),2)
    metrics['FSIM'] = np.round(tensor_to_numpy_array(piq.fsim(x, y, data_range=1., chromatic=False, reduction='none')),2)

    return metrics

def calculate_nr_metrics(x=torch.Tensor):
    '''
    Calculate No Reference (NR) Metrics 

        ...
        Parameters:
        x: torch.Tensor
            The input image
        
        Return:
        metrics: dict
            A dictionary that contains the values of the NR metrics
    
    '''
    metrics = {}
    metrics['BRISQUE'] = tensor_to_numpy_array(piq.brisque(x, data_range=1., reduction='none')).tolist()[0]
    metrics['TOTAL_VARIATION'] = tensor_to_numpy_array(piq.total_variation(x, reduction='none')).tolist()[0]

    return metrics