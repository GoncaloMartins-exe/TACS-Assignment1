# Setup

Create and activate a Python virtual environment, then install the required dependencies.

### 1. Create virtual environment

```bash
python3 -m venv .venv
```

### 2. Activate virtual environment

**Linux:**

```bash
source .venv/bin/activate
```

**Windows:**

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

# Run

Select one of the files in the `input/` directory (or create your own) and run:
```bash
python pipeline.py <file-path>
```

# Makefile Commands

<table>
  <tr>
    <th>Command</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>

```bash
make run
```

</td>
    <td>Run the pipeline sequentially on the 3 main test instances</td>
  </tr>
  <tr>
    <td>

```bash
make validate
```

</td>
    <td>Run the complete validation suite against the classical baseline</td>
  </tr>
  <tr>
    <td>

```bash
make clean
```

</td>
    <td>Clean generated output artifacts and Python caches</td>
  </tr>
  <tr>
    <td>

```bash
make help
```

</td>
    <td>Display all available commands</td>
  </tr>
</table>