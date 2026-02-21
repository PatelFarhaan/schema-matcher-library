# Schema Matcher (smtools)

A Python library for schema matching and data profiling, featuring tokenizers, type detection, trait analysis, and storage backends (local and AWS S3). Includes a Spark-based preprocessor and profiler for large-scale data processing. Built with PyBuilder and tested with pytest.

## Tech Stack

- **Language:** Python 3
- **Build System:** PyBuilder
- **Testing:** pytest, pytest-coverage
- **Big Data:** PySpark
- **Data Processing:** pandas, NLTK, py_stringmatching
- **Cloud Storage:** AWS S3 (Boto3)
- **CI/CD:** Jenkins (Jenkinsfile)

## Features

- Schema matching utilities for CSV data
- Tokenizer functions for text processing
- Type detection and classification for data columns
- Trait analysis for data profiling
- Pluggable storage backends (local filesystem, AWS S3)
- S3 storage with presigned URLs and sampling support
- PySpark preprocessor for distributed data cleaning
- PySpark profiler for large-scale data analysis
- Comprehensive test suite with coverage reporting

## Prerequisites

- Python 3.6+
- PyBuilder
- Apache Spark (for Spark-based features)
- AWS account (for S3 storage backend)

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd pytest
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install PyBuilder and dependencies:**
   ```bash
   pip install pybuilder
   pyb install_dependencies
   ```

4. **Configure environment (for S3 storage):**
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials
   ```

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | AWS access key (for S3 backend) | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key (for S3 backend) | `your-secret` |
| `AWS_REGION` | AWS region | `us-east-1` |
| `S3_BUCKET` | S3 bucket name | `my-data-bucket` |

## How to Run

### Build and Test
```bash
pyb install_dependencies
pyb
```

### Run Tests Only
```bash
pyb run_unit_tests
```

## Project Structure

```
pytest/
├── build.py                    # PyBuilder configuration
├── pyproject.toml              # PEP 517 build system config
├── setup.py                    # pip install support
├── Jenkinsfile                 # CI/CD pipeline definition
└── src/
    ├── main/python/
    │   ├── schemamatcher/
    │   │   ├── __init__.py
    │   │   ├── storage.py          # Abstract storage base class
    │   │   ├── s3_storage.py       # AWS S3 storage implementation
    │   │   └── utils/
    │   │       ├── types.py        # Type detection utilities
    │   │       ├── traits.py       # Data trait analysis
    │   │       └── tokenizers.py   # Text tokenization functions
    │   └── schemamatcher_spark/
    │       ├── __init__.py
    │       ├── preprocessor.py     # Spark data preprocessor
    │       └── profiler.py         # Spark data profiler
    └── unittest/python/
        ├── schemamatcher/
        │   ├── test_tokenizers.py
        │   ├── test_traits.py
        │   └── test_types.py
        └── schemamatcher_spark/
            ├── test_spark_profile.py
            └── test_spark_preprocessor.py
```

## License

MIT
