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

# Will run tests and prepare for the forge
conda build recipe

# Cleaning if you built many times, will clean the build directories
conda build purge 

# Installing recently built version
conda install --use-local hpo-toolkit
```

