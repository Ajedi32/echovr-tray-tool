import os

PROGRAM_FILES = os.environ['ProgramW6432']
STORE_ASSETS = os.path.join(
    PROGRAM_FILES,
    *'Oculus/CoreData/Software/StoreAssets/ready-at-dawn-echo-arena_assets'.split('/')
)
ICON_IMAGE = os.path.join(STORE_ASSETS, 'icon_image.jpg')
