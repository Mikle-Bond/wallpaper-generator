#!/usr/bin/python3

"""
Simple python wallpaper generator.

Usage: main.py [WIDTHxHEIGHT].
Code and examples here: https://github.com/timozattol/wallpaper-generator
"""

__author__ = "Timothée Lottaz"
__licence__ = "MIT"
__email__ = "timozattol@gmail.com"
__status__ = "Prototype"

import click
from pathlib import Path

from math import ceil
from PIL import Image, ImageDraw
from random import sample
from polylattice import PolyLattice
from colors import palettes

from palettes import palette_providers

def check_resolution(ctx, param, resolution):
    try:
        res_parse = resolution.split("x")
        if len(res_parse) != 2:
            raise ValueError()

        res_parse = [int(x) for x in res_parse]
        if any(x < 0 for x in res_parse):
            raise ValueError()

        return res_parse

    except ValueError:
        raise click.BadParameter('Resolution given in arguments must be written like "1920x1080".')

def select_palette(ctx, param, value):
    p = palette_providers[value]()
    return p.get_color_pair()

@click.command()
@click.option('--resolution', '-r', callback=check_resolution, default='1366x768',
        help='screen resolution, written as 1920x1080')
@click.option('--palette', '-p', 'colors', default='pastel', callback=select_palette,
        type=click.Choice(list(palette_providers.keys())),
        help='one of palettes')
@click.option('--output', '-o', default='wallpaper.png',
        type=click.Path(file_okay=True, dir_okay=False, writable=True, readable=False),
        help='output file')
@click.option('--force', '-f', is_flag=True, default=False,
        help='overwrite output file if it exists')
@click.option('--mutation', '-m', 'mutation_intensity', type=click.INT, default=30,
        help='mutation intensity')
def main(resolution, colors, output, force, mutation_intensity):

    # Polygons have a fixed size in px. Higher resolution = more polygons
    poly_sizes = (120, 100)

    ## Output file ##
    render_file = Path(output)

    # Script shouldn't be supposed to meke dirs
    if not render_file.parent.exists():
        raise click.BadParameter('Path to the output file does not exist')

    # Delete eventual previous renders
    if render_file.is_file():
        if not force:
            click.confirm('File "{}" exists. Overwrite?'.format(render_file), abort=True)
        else:
            click.echo('Warning, file "{}" will be overwriten.'.format(render_file), err=True)
        render_file.unlink()

    # Create an image of the size of the screen
    im = Image.new("RGB", resolution, 0)
    image_draw = ImageDraw.Draw(im)

    # Initialise a PolyLattice
    poly_count_x = (resolution[0] / poly_sizes[0])
    poly_count_y = (resolution[1] / poly_sizes[1])

    # Last polygons might be partly overflowing the image
    polylattice = PolyLattice(
        im.size,
        (ceil(poly_count_x), ceil(poly_count_y)),
        poly_sizes)
    polylattice.initialise(separate_in_triangles=True)

    # Mutate PolyLattice and apply random gradient of colors
    polylattice.mutate(mutation_intensity)
    polylattice.gradient_colors_random_direction(*colors)

    # Draw the polylattice on the image
    polylattice.draw(image_draw)

    # Save image in renders
    im.save(render_file)

if __name__ == '__main__':
    main()

