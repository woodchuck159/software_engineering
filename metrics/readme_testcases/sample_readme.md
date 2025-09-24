---
library_name: diffusers
license: other
license_name: tencent-hunyuan-community
license_link: https://github.com/Tencent-Hunyuan/SRPO/blob/main/LICENSE.txt
pipeline_tag: text-to-image
---

<div align=“center” style=“font-family: charter;”>
<h1 align="center">Directly Aligning the Full Diffusion Trajectory with Fine-Grained Human Preference </h1>
<div align="center">
  <a href='https://arxiv.org/abs/2509.06942'><img src='https://img.shields.io/badge/ArXiv-red?logo=arxiv'></a>  &nbsp;
  <a href='https://github.com/Tencent-Hunyuan/SRPO'><img src='https://img.shields.io/badge/_Code-SRPO-181717?color=121717&logo=github&logoColor=whitee'></a> &nbsp; 
  <a href='https://tencent.github.io/srpo-project-page/'><img src='https://img.shields.io/badge/%F0%9F%92%BB_Project-SRPO-blue'></a> &nbsp;
</div>
<div align="center">
  Xiangwei Shen<sup>1,2*</sup>,
  <a href="https://scholar.google.com/citations?user=Lnr1FQEAAAAJ&hl=zh-CN" target="_blank"><b>Zhimin Li</b></a><sup>1*</sup>,
  <a href="https://scholar.google.com.hk/citations?user=Fz3X5FwAAAAJ" target="_blank"><b>Zhantao Yang</b></a><sup>1</sup>, 
  <a href="https://shiyi-zh0408.github.io/" target="_blank"><b>Shiyi Zhang</b></a><sup>3</sup>,
  Yingfang Zhang<sup>1</sup>,
  Donghao Li<sup>1</sup>,
  <br>
  <a href="https://scholar.google.com/citations?user=VXQV5xwAAAAJ&hl=en" target="_blank"><b>Chunyu Wang</b></a><sup>1</sup>,
  <a href="https://openreview.net/profile?id=%7EQinglin_Lu2" target="_blank"><b>Qinglin Lu</b></a><sup>1</sup>,
  <a href="https://andytang15.github.io" target="_blank"><b>Yansong Tang</b></a><sup>3,✝</sup>
</div>
<div align="center">
  <sup>1</sup>Hunyuan, Tencent 
  <br>
  <sup>2</sup>School of Science and Engineering, The Chinese University of Hong Kong, Shenzhen 
  <br>
  <sup>3</sup>Shenzhen International Graduate School, Tsinghua University 
  <br>
  <sup>*</sup>Equal contribution 
  <sup>✝</sup>Corresponding author
</div>



## Abstract
Recent studies have demonstrated the effectiveness of directly aligning diffusion models with human preferences using differentiable reward. However, they exhibit two primary challenges: (1) they rely on multistep denoising with gradient computation for reward scoring, which is computationally expensive, thus restricting optimization to only a few diffusion steps; (2) they often need continuous offline adaptation of reward models in order to achieve desired aesthetic quality, such as photorealism or precise lighting effects. To address the limitation of multistep denoising, we propose Direct-Align, a method that predefines a noise prior to effectively recover original images from any time steps via interpolation, leveraging the equation that diffusion states are interpolations between noise and target images, which effectively avoids over-optimization in late timesteps. Furthermore, we introduce Semantic Relative Preference Optimization (SRPO), in which rewards are formulated as text-conditioned signals. This approach enables online adjustment of rewards in response to positive and negative prompt augmentation, thereby reducing the reliance on offline reward fine-tuning. By fine-tuning the FLUX.1.dev model with optimized denoising and online reward adjustment, we improve its human-evaluated realism and aesthetic quality by over 3x.

## Acknowledgement

We sincerely appreciate contributions from the research community to this project. Below are quantized versions developed by fellow researchers.

1. 8bit(fp8_e4m3fn/Q8_0) version by wikeeyang: https://huggingface.co/wikeeyang/SRPO-Refine-Quantized-v1.0
![image/png](https://cdn-uploads.huggingface.co/production/uploads/6645835a2b57c619a19cc0c4/BATJ0bW_0QPhkN5WY0Q1H.png)

2. bf16 version by rockerBOO: https://huggingface.co/rockerBOO/flux.1-dev-SRPO
3. GGUF version by befox: https://huggingface.co/befox/SRPO-GGUF

⚠️ Note: When loading weights in ComfyUI, avoid direct conversion of FP32 weights to FP8 format, as this may result in incomplete denoising. For official weights in this repository, FP32/BF16 loading is recommended.


### Checkpoints
The `diffusion_pytorch_model.safetensors` is online version of SRPO based on [FLUX.1 Dev](https://huggingface.co/black-forest-labs/FLUX.1-dev), trained on HPD dataset with [HPSv2](https://github.com/tgxs002/HPSv2)
## 🔑 Inference

### Using ComfyUI

You can use it in [ComfyUI](https://github.com/comfyanonymous/ComfyUI).

Load the following image in ComfyUI to get the workflow, or load the JSON file directly [SRPO-workflow](comfyui/SRPO-workflow.json):

Tip: The workflow JSON info was added to the image file.

![Example](comfyui/SRPO-workflow.png)

### Quick start
```bash
from diffusers import FluxPipeline
from safetensors.torch import load_file

prompt='The Death of Ophelia by John Everett Millais, Pre-Raphaelite painting, Ophelia floating in a river surrounded by flowers, detailed natural elements, melancholic and tragic atmosphere'
pipe = FluxPipeline.from_pretrained('./data/flux',
        torch_dtype=torch.bfloat16,
        use_safetensors=True
    ).to("cuda")
state_dict = load_file("./srpo/diffusion_pytorch_model.safetensors")
pipe.transformer.load_state_dict(state_dict)
image = pipe(
    prompt,
    guidance_scale=3.5,
    height=1024,
    width=1024,
    num_inference_steps=50,
    max_sequence_length=512,
    generator=generator
).images[0]
```
### License
SRPO is licensed under the License Terms of SRPO. See `./License.txt` for more details.
## Citation
If you use SRPO for your research, please cite our paper:

```bibtex
@misc{shen2025directlyaligningdiffusiontrajectory,
      title={Directly Aligning the Full Diffusion Trajectory with Fine-Grained Human Preference}, 
      author={Xiangwei Shen and Zhimin Li and Zhantao Yang and Shiyi Zhang and Yingfang Zhang and Donghao Li and Chunyu Wang and Qinglin Lu and Yansong Tang},
      year={2025},
      eprint={2509.06942},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2509.06942}, 
}
```