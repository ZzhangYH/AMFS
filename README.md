# AMFS (Automated Marking and Feedback System)

## Get Started

### Setting up development environment

```shell
conda create -n AMFS python=3.11 Flask
```

### Activate/deactivate this environment

```shell
conda activate AMFS
# or
conda deactivate
```

### Install dependencies

- `beautifulsoup4=4.12.3` (conda-forge)
- `flask=3.0.2` (conda-forge)
- `flask-weasyprint==1.1.0` (pip)
- `mosspy==1.0.9` (pip)
- `weasyprint=61.2` (conda-forge)

In the `AMFS` environment, use the following commands for quick installation:
```shell
conda install beautifulsoup4=4.12.3 flask=3.0.2 weasyprint=61.2 -c conda-forge
python -m pip install flask-weasyprint==1.1.0 mosspy==1.0.9
```

### Run the application

In the `AMFS` environment, launch flask server:
```shell
flask --app amfs run --debug
```
