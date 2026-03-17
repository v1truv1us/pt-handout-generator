#!/usr/bin/env python3
import click
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from discover import discover_images
from image_selector import select_images
from download import download_images
from pdf_generator import generate_pdf


@click.group()
def cli():
    """PT Handout Generator - Create printable exercise handouts"""
    pass


@cli.command()
def discover():
    """Discover image candidates from source pages"""
    discover_images()


@cli.command()
def select():
    """Select best images for each exercise"""
    select_images()


@cli.command()
def download():
    """Download selected images locally"""
    download_images()


@cli.command()
def generate():
    """Generate PDF handout"""
    generate_pdf()


@cli.command()
def all():
    """Run full pipeline: discover -> select -> download -> generate"""
    print("=== Step 1: Discovering images ===")
    discover_images()
    print("\n=== Step 2: Selecting best images ===")
    select_images()
    print("\n=== Step 3: Downloading images ===")
    download_images()
    print("\n=== Step 4: Generating PDF ===")
    generate_pdf()
    print("\n=== Complete! ===")


if __name__ == "__main__":
    cli()
