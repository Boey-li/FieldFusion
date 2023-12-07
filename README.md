# FieldsFusion: Harmonious Radiance Fields Composition

`This is a final project for CS445 (Computational Photography) Fall 2023 at UIUC`  

FieldsFusion is a project focused on advancing the field of 3D object and scene composition, with a particular emphasis on composition of radiance fields like NeRF and 3D Gaussian splatting. Our goal is to seamlessly integrate foreground objects with background scenes, both reconstructed from radiance fields, to facilitate high-fidelity rendering and composition. 
  
Our Data, Render Results and Example Blender Script can be found in [Google Drive](https://drive.google.com/drive/folders/18kqCHF76pFMARM17qI19g3a3A7ZTTzwx?usp=sharing)

![demo](/assets/demo.gif)

## 1. Installation

### 1.1. Clone the repository and submodules
```shell
git clone --recurse-submodules git@github.com:ZiYang-xie/FieldFusion.git
```

### 1.2. Install submodule dependencies
```shell
cd model/nerfstudio
pip install -r requirements.txt
pip install -e .

cd model/TensoIR
pip install torch==1.10 torchvision
pip install tqdm scikit-image opencv-python configargparse lpips imageio-ffmpeg kornia lpips tensorboard loguru plyfile
```

###  1.3. Put Blender into externel/
```shell
mkdir external
cd external
wget https://download.blender.org/release/Blender2.93/blender-2.93.0-linux-x64.tar.xz
tar -xvf blender-2.93.0-linux-x64.tar.xz
```

###  1.4. Install nerfstudio Addon `scripts/nerfstudio_addon.py` in Blender 
- According to [nerfstudio tutorial](https://docs.nerf.studio/extensions/blender_addon.html)

## Pipeline Overview
![pipeline](/assets/pipeline.png)

## 2. Usage

### 2.1 Data Preparation
- Prepare the data for the foreground object and background scene separately.
- The data should be in the form of a set of images and camera poses.
- Refer to [nerfstudio data preparation](https://docs.nerf.studio/quickstart/custom_dataset.html) for more details.

### 2.1.2(Optional) Invserse Rendering with Relighting
- Run the Rendering with a pre-trained model under learned lighting condition, refer to [TensoIR](https://github.com/Haian-Jin/TensoIR) for more details.
```shell
export PYTHONPATH=. && python "$training_file" --config "$config_path" --ckpt "$ckpt_path" --render_only 1 --render_test 1
```

### 2.2 Run the reconstruction pipeline
- Run the reconstruction pipeline for the foreground object and background scene separately.
```shell
MODEL= <nerfacto/gaussian-splatting>

DATA=colmap
SCENE_NAME=<INPUT_YOUR_SCENE_NAME>
DATA_DIR=./data/<background/foreground>/$SCENE_NAME/
EXP_NAME=$MODEL-$SCENE_NAME

ns-train $MODEL \
--vis wandb \
--experiment-name $EXP_NAME \
$DATA \
--data $DATA_DIR \
--train-split-fraction 1 \
```

### 2.3 Export the geometry prior
- Export Pointcloud for background
```shell
ns-export gaussian-splat --load-config <CONFIG> --output-dir <OUTPUT_DIR>
```

- Crop the foreground object with Bbox and export the mesh
```shell
ns-export poisson \
    --load-config <CONFIG> \
    --output-dir <OUTPUT_DIR> \
    --normal-method open3d \
    --remove-outliers True \
    --obb-center <FLOAT FLOAT FLOAT> \
    --obb-rotation <FLOAT FLOAT FLOAT> \
    --obb-scale <FLOAT FLOAT FLOAT>
```

You can crop the foreground object with `ns-viewer` to get the `obb-center`, `obb-rotation` and `obb-scale`

### 2.3 Open Blender to align the foreground object and background scene
![blender](/assets/blender.png)
- Import the foreground object and background scene into Blender.
- Put the foreground object into the background scene.
- Design a camera trajectory.
- Export the camera poses of the foreground object and background scene respectively.
- [OPTIONAL] Add a equiangular camera in the center of the scene to render the environment map.

### 2.4 Render the scene and objects
- Given the prepared camera poses, render the foreground object and background scene.

```shell
ns-render camera-path \
    --load-config <Foreground / Background config> \
    --output-format images \
    --output-path <Your Save Path> \
    --camera-path-filename <Exported Camera Path> \
    # --rendered-output-names accumulation 
```

Use `--rendered-output-names accumulation` to render foreground accumulation mask.

### 2.5 Render the shadow
- Save the blender script generated in Step 2.3 as `shadow.blend`.
- Change the file path in `scripts/render_shadow.py` to your own path.
- Run the following command to render the shadow.
```shell
./externel/blender/blender -b -E CYCLES -P ./scripts/shadow_render.py 
```

### 2.6 Compose the final results
- Given the RGB images of the foreground object and background scene, shadow and the foreground accumulation mask, compose the images to get the final results.

```shell
python scripts/compose.py \
    --fg_path <Foreground RGB> \
    ---bg_path <Background RGB> \
    --shadow_path <Shadow> \
    --mask_path <Foreground Accumulation Mask> \
    --output <Output Path>
```

## License
This is an open access article distributed under the terms of the CC-BY-NC-ND license  
Donnot use this code for commercial purposes. 

