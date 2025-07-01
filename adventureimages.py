#adventureimages.py
#!/usr/bin/env python3
"""
Stable Diffusion Image Generator and Uploader
Generates images from text prompts and uploads them via SCP
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional

import torch
from diffusers import StableDiffusionPipeline
from diffusers import StableDiffusionXLPipeline,DiffusionPipeline,UNet2DConditionModel, EulerDiscreteScheduler
from safetensors.torch import load_file
from huggingface_hub import hf_hub_download

from PIL import Image




class ByteDanceLightGenerator:

    def __init__(self, model_name: str, local_model_dir: str = None,     
                 local_model: bool = False, device: Optional[str] = None):
        self.model_name = model_name
        self.local_model_dir = local_model_dir
        self.pipe = None

    def load_model(self):
        base = "stabilityai/stable-diffusion-xl-base-1.0"
        repo = "ByteDance/SDXL-Lightning"
        ckpt = "sdxl_lightning_4step_unet.safetensors" # Use the correct ckpt for your step setting!
        unet = UNet2DConditionModel.from_config(base, subfolder="unet").to("cuda", torch.float16)
        unet.load_state_dict(load_file(hf_hub_download(repo, ckpt), device="cuda"))
        self.pipe = StableDiffusionXLPipeline.from_pretrained(base, unet=unet, torch_dtype=torch.float16, variant="fp16").to("cuda")
    
    def generate_image(self, prompt: str, width: int = 512, height: int = 512, 
                       num_inference_steps: int = 20, guidance_scale: float = 7.5) -> Image.Image:
        image = self.pipe(prompt,height=height,
            width=width,
            num_inference_steps=4
            ).images[0]
        return image
    
    
    
    
class NotaGenerator:
    def __init__(self, model_name: str, local_model_dir: str = None,     
                 local_model: bool = False, device: Optional[str] = None):
        self.model_name = model_name
        self.local_model_dir = local_model_dir
        self.pipe = None

    def load_model(self):
        pipe = DiffusionPipeline.from_pretrained("nota-ai/bk-sdm-base",torch_dtype=torch.float16)
        pipe.to("cuda")
        self.pipe = pipe
    
    def generate_image(self, prompt: str, width: int = 512, height: int = 512, 
                       num_inference_steps: int = 20, guidance_scale: float = 7.5) -> Image.Image:
        image = self.pipe(prompt,height=height,
            width=width,
            num_inference_steps=4   
            ).images[0]
        return image    

class SchnellGenerator:
    
    def __init__(self, model_name: str, local_model_dir: str = None,     
                 local_model: bool = False, device: Optional[str] = None):
        self.model_name = model_name
        self.local_model_dir = local_model_dir
        self.pipe = None

    def load_model(self):
        pipe = DiffusionPipeline.from_pretrained("Enblack-forest-labs/FLUX.1-schnell")
        pipe.to("cuda")
        self.pipe = pipe
    
    def generate_image(self, prompt: str, width: int = 512, height: int = 512, 
                       num_inference_steps: int = 20, guidance_scale: float = 7.5) -> Image.Image:
        image = self.pipe(prompt,height=height,
            width=width,
            guidance_scale=0.0,
            num_inference_steps=4   
            ).images[0]
        return image

class InkPunkGenerator:
    
    def __init__(self, model_name: str, local_model_dir: str = None,     
                 local_model: bool = False, device: Optional[str] = None):
        self.model_name = model_name
        self.local_model_dir = local_model_dir
        self.pipe = None

    def load_model(self):
        pipe = DiffusionPipeline.from_pretrained("Envvi/Inkpunk-Diffusion")
        pipe.to("cuda")
        self.pipe = pipe
    
    def generate_image(self, prompt: str, width: int = 512, height: int = 512, 
                       num_inference_steps: int = 20, guidance_scale: float = 7.5) -> Image.Image:
        image = self.pipe("  nvinkpunk " + prompt,height=height,
            width=width,
            num_inference_steps=20
            ).images[0]
        return image



class EnvaGenerator:
    
    def __init__(self, model_name: str, local_model_dir: str = None,     
                 local_model: bool = False, device: Optional[str] = None):
        self.model_name = model_name
        self.local_model_dir = local_model_dir
        self.pipe = None

    def load_model(self):
        pipe = DiffusionPipeline.from_pretrained("mann-e/Mann-E_Dreams")
        pipe.to("cuda")
        self.pipe = pipe
    
    def generate_image(self, prompt: str, width: int = 512, height: int = 512, 
                       num_inference_steps: int = 20, guidance_scale: float = 7.5) -> Image.Image:
        image = self.pipe(prompt,height=height,
            width=width,
            num_inference_steps=20
            ).images[0]
        return image


class NotaGenerator:
    
    def __init__(self, model_name: str, local_model_dir: str = None,     
                 local_model: bool = False, device: Optional[str] = None):
        self.model_name = model_name
        self.local_model_dir = local_model_dir
        self.pipe = None

    def load_model(self):
        pipe = DiffusionPipeline.from_pretrained("nota-ai/bk-sdm-small",torch_dtype=torch.float16)
        pipe.to("cuda")
        self.pipe = pipe
    
    def generate_image(self, prompt: str, width: int = 512, height: int = 512, 
                       num_inference_steps: int = 20, guidance_scale: float = 7.5) -> Image.Image:
        image = self.pipe(prompt,height=height,
            width=width,
            num_inference_steps=20
            ).images[0]
        return image

class StableDiffusionGenerator:
    """
    Stable Diffusion image generator class
    """
    def __init__(self, model_name: str, local_model_dir: str = None, 
                 local_model: bool = False, device: Optional[str] = None):
        self.model_name = model_name
        self.local_model_dir = local_model_dir
        self.local_model = local_model
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.pipe = None
        
    def load_model(self):
        """Load the Stable Diffusion model"""
        if self.local_model:
            model_path = os.path.join(self.local_model_dir, self.model_name)
            self.pipe = StableDiffusionPipeline.from_pretrained(
                model_path, local_files_only=True
            ).to(self.device)
        else:
            self.pipe = StableDiffusionPipeline.from_pretrained(
                self.model_name, 
                use_auth_token=False,
            ).to(self.device)
        
        # Enable memory optimization if using CUDA
        if self.device == "cuda":
            self.pipe.enable_attention_slicing()
            
    def generate_image(self, prompt: str, width: int = 512, height: int = 512, 
                       num_inference_steps: int = 20, guidance_scale: float = 7.5) -> Image.Image:
        """
        Generate an image using the loaded model
        
        Args:
            prompt: Text prompt to generate image from
            width: Output image width
            height: Output image height
            num_inference_steps: Number of denoising steps
            guidance_scale: Guidance scale for conditioning
            
        Returns:
            PIL Image object
        """
        if self.pipe is None:
            raise RuntimeError("Model not loaded. Call load_model() first")
            
        return self.pipe(
            prompt,
            height=height,
            width=width,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale
        ).images[0]


def create_generator(model_name: str, **kwargs):
    """
    Create an appropriate image generator based on the model name
    
    Args:
        model_name: Name of the model to use
        **kwargs: Additional arguments to pass to the generator
    
    Returns:
        An image generator object
    """
    # Currently only supporting StableDiffusion models
    # Can be extended to support other model types
    if "stable-diffusion" in model_name.lower() or "runwayml" in model_name.lower():
        return StableDiffusionGenerator(model_name=model_name, **kwargs)
    
    if "nota" in model_name.lower():
        return  NotaGenerator(model_name=model_name, **kwargs)

    if "schnell" in model_name.lower():
        return SchnellGenerator(model_name=model_name, **kwargs)


    if "mann-e" in model_name.lower():
        return EnvaGenerator(model_name=model_name, **kwargs)
    
    
    if "notai" in model_name.lower():
        return NotaGenerator(model_name=model_name, **kwargs)
    
    if "inkpunk" in model_name.lower():
        return  InkPunkGenerator(model_name=model_name, **kwargs)    
    else:
        # Default to StableDiffusion for now
        # This could be expanded to support DALL-E, Midjourney API, etc.
        print(f"Using default StableDiffusionGenerator for model: {model_name}")
        return StableDiffusionGenerator(model_name=model_name, **kwargs)

def read_prompt_files(prompt_dir: str) -> List[tuple]:
    """
    Read all text files from the prompt directory.
    
    Args:
        prompt_dir: Directory containing prompt text files
        
    Returns:
        List of tuples (file_path, prompt_text, base_name)
    """
    prompt_path = Path(prompt_dir)
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt directory not found: {prompt_dir}")
    
    prompts = []
    for txt_file in prompt_path.glob("*.prompt"):
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                prompt_text = f.read().strip()
            
            if prompt_text:
                base_name = txt_file.stem
                prompts.append((str(txt_file), prompt_text, base_name))
            else:
                print(f"Warning: Empty prompt file: {txt_file}")
                
        except Exception as e:
            print(f"Error reading file {txt_file}: {e}")
    
    return prompts

def upload_images(image_dir: str, remote_host: str = "erik@chinese.eriktamm.com",
                    remote_path: str = "/var/www/html/adventures"):
    """
    Upload generated images to remote server using a single SCP command.
    
    Args:
        image_dir: Local directory containing images
        remote_host: Remote host for SCP upload
        remote_path: Remote path for uploads
    """
    image_path = Path(image_dir)
    jpg_files = list(image_path.glob("*.jpg"))
    
    if not jpg_files:
        print("No JPG files found to upload")
        return
    
    print(f"Uploading {len(jpg_files)} images to {remote_host}:{remote_path}")
    
    try:
        # Use a single scp command with all files
        cmd = ["scp"] + [str(jpg_file) for jpg_file in jpg_files] + [f"{remote_host}:{remote_path}/"]
        print(f"Executing: {' '.join(cmd[:3])}... (and {len(jpg_files)} files)")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✓ Successfully uploaded {len(jpg_files)} images")
        else:
            print(f"✗ Failed to upload images: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print(f"✗ Upload timed out after 300 seconds")
    except Exception as e:
        print(f"✗ Error during upload: {e}")



def main():
    parser = argparse.ArgumentParser(description="Generate images from text prompts using Stable Diffusion")
    parser.add_argument("local_model", default="no",help="dont save")    
    parser.add_argument("prompt_dir", default="input",help="Directory containing prompt text files")
    parser.add_argument("-o", "--output-dir", default="./generated_images", 
                       help="Output directory for generated images")
    parser.add_argument("-m", "--model-dir", default="./models/stable-diffusion",
                       help="Local model directory")
    parser.add_argument("--model-name", default="runwayml/stable-diffusion-v1-5",
                       help="HuggingFace model name")
    parser.add_argument("--width", type=int, default=512, help="Image width")
    parser.add_argument("--height", type=int, default=512, help="Image height")
    parser.add_argument("--steps", type=int, default=20, help="Number of inference steps")
    parser.add_argument("--guidance", type=float, default=7.5, help="Guidance scale")
    parser.add_argument("--no-upload", action="store_true", help="Skip uploading images")
    parser.add_argument("--device", choices=["cuda", "cpu", "auto"], default="auto",
                       help="Device to use for inference")
    
    args = parser.parse_args()
    
    # Create output directory
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Read prompt files
        print(f"Reading prompts from: {args.prompt_dir}")
        prompts = read_prompt_files(args.prompt_dir)
        
        if not prompts:
            print("No valid prompt files found!")
            return 1
        
        print(f"Found {len(prompts)} prompt files")
        
        # Initialize generator
        device = None if args.device == "auto" else args.device
        
        # Load model
        print(f"Initializing generator with model: {args.model_name}")
        generator = create_generator(model_name=args.model_name,
            local_model_dir=args.model_dir if args.local_model.lower() == "yes" else None,
            local_model=args.local_model.lower() == "yes",
            device=device
        )
        generator.load_model()
        # Generate images
        for i, (file_path, prompt_text, base_name) in enumerate(prompts, 1):
            print(f"\nProcessing {i}/{len(prompts)}: {base_name}")
            
            try:
                # Generate image
                image = generator.generate_image(
                    prompt=prompt_text,
                    width=args.width,
                    height=args.height,
                    num_inference_steps=args.steps,
                    guidance_scale=args.guidance
                )
                
                # Save image
                output_file = output_path / f"{base_name}.jpg"
                image.save(output_file, "JPEG", quality=95)
                print(f"✓ Saved: {output_file}")
                
            except Exception as e:
                print(f"✗ Error generating image for {base_name}: {e}")
                continue
        
        # Upload images
        if not args.no_upload:
            print(f"\nUploading images...")
            upload_images(args.output_dir)
        else:
            print(f"\nSkipping upload (--no-upload specified)")
        
        print(f"\nCompleted! Generated images saved in: {args.output_dir}")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
