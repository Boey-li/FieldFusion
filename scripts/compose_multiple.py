import imageio
import torch
import torchvision
import numpy as np
import cv2
import os

from rich.progress import Progress
import argparse

def combine(fg_path, bg_path, out_path, mask_path=None, shadow_path=None):
    fg_image_paths = []
    for fg_path_i in fg_path:
        fg_image_paths.append([os.path.join(fg_path_i, f) for f in sorted(os.listdir(fg_path_i))])

    bg_image_path = [os.path.join(bg_path, f) for f in sorted(os.listdir(bg_path))]
    if mask_path is not None:
        mask_image_paths = []
        for mask_path_i in mask_path:
            mask_image_paths.append([os.path.join(mask_path_i, f) for f in sorted(os.listdir(mask_path_i))])
    if shadow_path is not None:
        shadow_image_path = [os.path.join(shadow_path, f) for f in sorted(os.listdir(shadow_path))]
    
    N = len(bg_image_path)
    fg_image_paths = [f[:N] for f in fg_image_paths]
    
    bg_image_path = bg_image_path[:N]
    mask_image_paths = [f[:N] for f in mask_image_paths] if mask_path is not None else [[None]*len(fg_image_paths)]*N
    shadow_image_path = shadow_image_path[:N] if shadow_path is not None else [None]*N
    
    composed_images = []
    with Progress() as progress:
        task = progress.add_task("Postprocessing...", total=N)
        for idx, (bg_img_path, shadow_img_path) in enumerate(zip(bg_image_path, shadow_image_path)):
            bg_img = imageio.imread(bg_img_path) / 255.0
            fg_img = np.zeros_like(bg_img)
            mask = np.zeros((bg_img.shape[0], bg_img.shape[1]))
            for fg_img_path, mask_img_path in zip(fg_image_paths, mask_image_paths):
                _fg_img_path = fg_img_path[idx]
                _mask_img_path = mask_img_path[idx]
                _fg_img = imageio.imread(_fg_img_path) / 255.0

                _mask = imageio.imread(_mask_img_path)
                _mask = _mask / 255.0
                _mask = cv2.erode(_mask, (5,5), iterations=2)
                _mask = cv2.GaussianBlur(_mask, (7, 7), 2) # Smooth mask
                
                fg_img = fg_img * (1-_mask[:,:,None]) + _fg_img * _mask[:,:,None]
                mask += _mask
                
            mask[mask > 1] = 1
            if shadow_img_path is not None:
                shadow = imageio.imread(shadow_img_path)
                shadow = shadow / 255.0
                shadow_mask = shadow[:,:,-1][...,None]
                shadow = shadow[:,:,:3]
                composed = fg_img * mask[:,:,None] + (bg_img * (1-shadow_mask) + shadow*shadow_mask) * (1-mask[:,:,None])
            else:
                composed = fg_img * mask[:,:,None] + bg_img * (1-mask[:,:,None])

            composed = (composed * 255).astype(np.uint8)
            composed_images.append(composed)
            progress.update(task, advance=1)

    # Save video
    with imageio.get_writer(os.path.join(out_path, 'video_composed.mp4'), fps=30) as video:
        for img in composed_images:
            video.append_data(img)

    # Save images
    for i, img in enumerate(composed_images):
        imageio.imwrite(os.path.join(out_path, f'{i:04d}.png'), img)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bg_path', type=str, required=True, help='Background image path')
    parser.add_argument('--shadow_path', type=str, default=None, help='Shadow image path')
    parser.add_argument('--out_path', type=str, required=True, help='Output image path')

    fg_base_path = '/projects/bbjv/leoxie/Project/CS445/FieldFusion/render/foreground'
    fg_names = ['clock', 'mustard_bottle']
    fg_path = [os.path.join(fg_base_path, f, 'images') for f in fg_names]
    mask_path = [os.path.join(fg_base_path, f, 'masks') for f in fg_names]

    args = parser.parse_args()
    combine(fg_path, args.bg_path, args.out_path, mask_path, args.shadow_path)