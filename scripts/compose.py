import imageio
import torch
import torchvision
import numpy as np
import cv2
import os

from rich.progress import Progress
import argparse

def combine(fg_path, bg_path, out_path, mask_path=None, shadow_path=None):
    fg_image_path = [os.path.join(fg_path, f) for f in sorted(os.listdir(fg_path))]
    bg_image_path = [os.path.join(bg_path, f) for f in sorted(os.listdir(bg_path))]
    if mask_path is not None:
        mask_image_path = [os.path.join(mask_path, f) for f in sorted(os.listdir(mask_path))]
    if shadow_path is not None:
        shadow_image_path = [os.path.join(shadow_path, f) for f in sorted(os.listdir(shadow_path))]
    
    N = min(len(fg_image_path), len(bg_image_path))
    fg_image_path = fg_image_path[:N]
    
    bg_image_path = bg_image_path[:N]
    mask_image_path = mask_image_path[:N] if mask_path is not None else [None]*N
    shadow_image_path = shadow_image_path[:N] if shadow_path is not None else [None]*N
    
    composed_images = []
    with Progress() as progress:
        task = progress.add_task("Postprocessing...", total=len(fg_image_path))
        for fg_img_path, bg_img_path, mask_img_path, shadow_img_path in zip(fg_image_path, bg_image_path, mask_image_path, shadow_image_path):
            fg_img = imageio.imread(fg_img_path) / 255.0
            bg_img = imageio.imread(bg_img_path) / 255.0

            if mask_img_path is not None:
                mask = imageio.imread(mask_img_path)
                mask = mask / 255.0
                mask = cv2.erode(mask, (5,5), iterations=5)
                mask = cv2.GaussianBlur(mask, (7, 7), 3) # Smooth mask
            else:
                mask = fg_img[:,:,0] > 10
                mask = mask / 255.0

            if shadow_img_path is not None:
                shadow = imageio.imread(shadow_img_path)
                shadow = shadow / 255.0
                shadow_mask = shadow[:,:,-1][...,None]
                shadow = shadow[:,:,:3]
                composed = fg_img * mask[:,:,None] + (bg_img * (1-shadow_mask) + shadow*shadow_mask) * (1-mask[:,:,None])
            else:
                composed = fg_img * mask[:,:,None]  + bg_img * (1-mask[:,:,None])

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
    parser.add_argument('--fg_path', type=str, required=True, help='Foreground image path')
    parser.add_argument('--bg_path', type=str, required=True, help='Background image path')
    parser.add_argument('--mask_path', type=str, default=None, help='Mask image path')
    parser.add_argument('--shadow_path', type=str, default=None, help='Shadow image path')
    parser.add_argument('--out_path', type=str, required=True, help='Output image path')

    args = parser.parse_args()
    combine(args.fg_path, args.bg_path, args.out_path, args.mask_path, args.shadow_path)