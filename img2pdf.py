import argparse
import glob
import os

from PIL import Image, UnidentifiedImageError

"""
img2pdf by Stephen Genusa

Convert images to PDF
 
"""

class Image2PDFMaker(object):

    def __init__(self, args):
        self.image_list = []
        self.input_folder = args.input_folder
        self.output_filename = args.output_filename
        self.keep_animations = args.keep_animations
        self.recursive = args.recursive

    def process_directory(self, starting_path, recursive):
        if recursive:
            file_list = glob.glob(os.path.join(starting_path, '**/*.*'), recursive=recursive)
        else:
            file_list = glob.glob(os.path.join(starting_path, '*.*'), recursive=recursive)
        total_files = len(file_list)
        for idx, file_name in enumerate(file_list):
            if os.path.isdir(file_name):
                if recursive:
                    print("Processing path", file_name)
                    self.process_directory(file_name, True)
            else:
                Image.MAX_IMAGE_PIXELS = None
                try:
                    if os.path.isfile(file_name):
                        _, ext = os.path.splitext(file_name)
                        if ext[1:].lower() in ['apng', 'blp', 'bmp', 'cur', 'dcx', 'dds', 'dib', 'eps', 'fli', 'flc',
                                               'fpx', 'ftex', 'gbr', 'gif', 'ico', 'jpeg', 'jp2k', 'jpg', 'j2k',
                                               'j2p', 'jpx', 'msp', 'pbm', 'pgm', 'ppm', 'pcx', 'png', 'raw',
                                               'tga', 'tif', 'tiff', 'psd', 'svg', 'wmf', 'xcf']:
                            try:
                                # Bit of a Kabuki dance to try and prevent invalid images from getting added to list.
                                # causes nasty problems in Save() where troubleshooting the offending image is
                                # much harder
                                print(idx + 1, '/', total_files, file_name)
                                im = Image.open(file_name)
                                im.verify()
                                im.close()
                                im = Image.open(file_name)
                                im.load()
                                im.close()
                                im = Image.open(file_name)
                                # Now deal with multi-frame images such as animations that PIL will split out into a
                                # bunch of separate pages
                                if self.keep_animations or (not (hasattr(im, 'n_frames')) or (
                                        hasattr(im, 'n_frames') and im.n_frames == 1)):
                                    if not im.mode == 'RGB':
                                        im = im.convert('RGB')
                                    self.image_list.append(im)
                                else:
                                    print('Skipping file', file_name, im.n_frames, "due to multiple frames", file_name)
                            except (UnidentifiedImageError, SyntaxError, ValueError):
                                print('Skipping file that PIL has a problem loading', file_name)
                except PermissionError:
                    print("Permission denied on file", file_name)
                except OSError:
                    print("OSError on", file_name)

    def save_pdf(self):
        output_filename = os.path.join(os.path.expanduser('~'), "Desktop", self.output_filename)
        if len(self.image_list) == 0:
            print("No qualifying images found")
        elif len(self.image_list) == 1:
            self.image_list[0].save(output_filename, save_all=True, quality=100)
        elif len(self.image_list) > 1:
            self.image_list[0].save(output_filename, save_all=True, quality=100, append_images=self.image_list[1:])

    def build_pdf(self):
        self.process_directory(self.input_folder, self.recursive)
        self.save_pdf()
        print("Done!")


def main():
    parser = argparse.ArgumentParser(prog='img2pdf',
                                     usage='%(prog)s [options] path',
                                     description='Convert images files to PDF')
    parser.add_argument('-i', '--input-folder', action='store', type=str, required=True)
    parser.add_argument('-o', '--output-filename', action='store', type=str, required=True)
    parser.add_argument('-k', '--keep-animations', action='store_true', required=False, default=False)
    parser.add_argument('-r', '--recursive', action='store_true', required=False, default=False)
    args = parser.parse_args()
    pdf_maker = Image2PDFMaker(args)
    pdf_maker.build_pdf()


if __name__ == '__main__':
    main()
