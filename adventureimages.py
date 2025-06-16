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
from PIL import Image


#

class StableDiffusionGenerator:
    def __init__(self, model_name: str = "mann-e/Mann-E_Dreams", 
                 local_model_dir: str = "./models/manne",
                 device: Optional[str] = None):
        """
        Initialize the Stable Diffusion generator.
        
        Args:
            model_name: HuggingFace model identifier
            local_model_dir: Local directory to store/load model
            device: Device to use ('cuda', 'cpu', or None for auto-detection)
        """
        self.model_name = model_name
        self.local_model_dir = Path(local_model_dir)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.pipeline = None
        
        print(f"Using device: {self.device}")
        
    def load_model(self):
        """Load the model from local directory or download from HuggingFace."""
        try:
            # Try to load from local directory first
            if self.local_model_dir.exists() and any(self.local_model_dir.iterdir()):
                print(f"Loading model from local directory: {self.local_model_dir}")
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    str(self.local_model_dir),
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    safety_checker=None,
                    requires_safety_checker=False
                )
            else:
                raise FileNotFoundError("Local model not found")
                
        except (FileNotFoundError, OSError, Exception) as e:
            print(f"Failed to load local model: {e}")
            print(f"Downloading model from HuggingFace: {self.model_name}")
            
            # Download from HuggingFace
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                safety_checker=None,
                requires_safety_checker=False
            )
            
            # Save model locally for future use
            print(f"Saving model to local directory: {self.local_model_dir}")
            self.local_model_dir.mkdir(parents=True, exist_ok=True)
            self.pipeline.save_pretrained(str(self.local_model_dir))
        
        # Move pipeline to device and optimize
        self.pipeline = self.pipeline.to(self.device)
        
        if self.device == "cuda":
            # Enable memory efficient attention if available
            try:
                self.pipeline.enable_xformers_memory_efficient_attention()
            except ImportError:
                print("xformers not available, using default attention")
            
            # Enable CPU offload to save GPU memory
            self.pipeline.enable_model_cpu_offload()
    
    def generate_image(self, prompt: str, width: int = 512, height: int = 512, 
                      num_inference_steps: int = 20, guidance_scale: float = 7.5) -> Image.Image:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Text prompt for image generation
            width: Image width
            height: Image height
            num_inference_steps: Number of denoising steps
            guidance_scale: Guidance scale for generation
            
        Returns:
            PIL Image object
        """
        if self.pipeline is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        print(f"Generating image for prompt: '{prompt[:50]}...'")
        
        with torch.autocast(self.device):
            result = self.pipeline(
                prompt=prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=torch.Generator(device=self.device).manual_seed(42)  # For reproducibility
            )
        
        return result.images[0]


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
        generator = StableDiffusionGenerator(
            model_name=args.model_name,
            local_model_dir=args.model_dir,
            device=device
        )
        
        # Load model
        print("Loading Stable Diffusion model...")
        generator.load_model()
        print("Model loaded successfully!")
        
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
