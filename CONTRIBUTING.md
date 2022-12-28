## Contributing

#### With Conda

```bash
# Import the current conda env in the repository
conda env create -f environment.yml

# Activate the conda env
conda activate <name>

# If you update the environment aka installing packages, update the yml
conda env export > environment.yml
```

##### Building for conda-forge
```bash

# Set conda forge
conda config --add channels conda-forge
conda config --set channel_priority strict

# Will run tests and prepore for the forge
conda build recipe

# Cleaning if you built many times, will clean the build directories
conda build purge 

# Installing recently built version
conda install --use-local hpo-toolkit
```


##### Uploading to conda-forge
```bash
# https://conda-forge.org/#contribute
```

#### PyPi

The following packages are required for testing, building, and deployment to PyPi:
- `tox`
- `build`
- `twine`

Consider creating a dedicated virtual environment with the above packages. Then, run the following 
to deploy `hpo-toolkit` to PyPi:  

```bash
cd hpo-toolkit

# Test
tox run

# Build
python -m build

# Deploy
python -m twine upload --sign --identity <YOUR_GPG_KEY_HERE> dist/*
```

The commands will run tests, build source distribution and a wheel, and deploy the source distribution and wheel to PyPi.
During deployment, you will be prompted for your PyPi credentials.  
