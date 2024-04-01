# AMFS (Automated Marking and Feedback System)

## Get Started

### OS Requirements
- macOS 11 Big Sur or later

### Setting up development environment

```shell
conda create -n AMFS python=3.11
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

### Sample Submission Test

You may use the following information to fill in the marking configuration page, please refer to the [USER_MANUAL](USER_MANUAL.pdf):
- Compile command: `javac -encoding UTF-8 -sourcepath . IdSum.java`
- Execute command: `java -Dfile.encoding=UTF-8 -XX:+UseSerialGC -Xss64m -Xms1920m -Xmx1920m IdSum`
- _**Absolute path**_ to the subdirectories listed below

```
└── test
    ├── solution      # includes sample solution
    ├── submission    # includes five submissions
    └── test_case     # includes two .in test cases
```
