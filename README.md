# Batch Image Renaming Tool

[中文版本](README_zh.md)

This is a recursive image renaming tool that can batch rename images in folders according to the folder name. Supports multilingual interface, including Chinese, English, Russian, Japanese, German, Portuguese and French.

## Features

- Recursive processing: Automatically processes selected folders and all their subfolders
- Smart renaming: Renames images to "foldername_number.extension" format
- Multilingual support: Interface supports 7 languages
- Real-time logging: Displays processing progress and results
- User-friendly: Simple and intuitive graphical interface

## Supported Image Formats

- JPG/JPEG
- PNG
- GIF
- BMP
- TIFF
- WEBP

## Usage

1. Run the program: `python rename_images_gui.py`
2. Select root folder: Click "Browse..." button to select the root folder
3. Start processing: Click "Start Renaming" button
4. View results: Check processing results in the log area

## Development Info

### Dependencies

This project mainly uses Python standard library, no additional third-party libraries required.

### Automated Build

This project uses GitHub Actions for automated testing and releases:

- **Test Workflow**: Automatically runs tests when code is pushed
- **Release Workflow**: Automatically builds executable files and releases to GitHub Releases when new tags are created

### Release New Version

Create a new tag to trigger automatic build and release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

## License

Please see the LICENSE file in the project for license information.