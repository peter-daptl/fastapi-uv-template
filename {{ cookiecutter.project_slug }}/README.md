# {{ cookiecutter.project_name }}

This is a Cookiecutter template for generating a FastAPI project with the following features:

* **True Class-Based Views:** It uses `fastapi-utils`'s `@cbv` decorator for a clean, object-oriented API structure.
* **Modular Design:**
    * Pydantic schemas are centralized in `schemas/`.
    * SQLAlchemy ORM models are in `database/models/`.
    * Views and service (domain) logic are organized into feature-specific folders (e.g., `api/v1/items/`), reflecting the API routes.
    * **Strict Import Style:** Uses fully qualified imports (e.g., `from {{ cookiecutter.app_name }}.some_module.sub_module import ...`) for clarity. `__init__.py` files declare their public API using `__all__` to explicitly manage re-exports.
* **Google-Style Docstrings:** All Python code uses Google-style docstrings for consistent and clear documentation.
* **Separation of Concerns:** Service layer (your "domain" logic) explicitly uses Pydantic schemas for input/output, ensuring consistency between the API layer and business logic.
* **Pre-Commit Hooks (with Ruff & uv):** Configured with essential pre-commit hooks for code quality and consistency using `ruff` for linting and formatting, and `uv` for dependency lock file management:
    * `trailing-whitespace`
    * `end-of-file-fixer`
    * `check-yaml`
    * `check-added-large-files`
    * `debug-statements` (removes `print` and `breakpoint` calls)
    * `ruff-format` (code formatter)
    * `ruff` (linter, includes checks for unused imports/variables)
    * `uv-lock` (ensures `uv.lock` is up-to-date)
    * **`pytest`**: Ensures all tests pass before committing, run via `uv`.
* **Testing Setup:** Includes a `tests/` directory with a sample `pytest` test file and `httpx` for API testing.
* **Modern Dependency Management with `uv`:** Dependencies are managed directly in `pyproject.toml` and locked with `uv.lock`.
* **Centralized Tool Configuration:** `pyproject.toml` contains configuration for `ruff` and `coverage.py`, ensuring consistency across your development environment.
* **`.gitignore`:** Pre-configured to ignore common Python, Git, and IDE artifacts, including `uv.lock`.

---

## **How to Use**

To get started with your new project, follow these steps:

1.  **Install Cookiecutter:**
    ```bash
    pip install cookiecutter
    ```

2.  **Generate a new project:**
    Navigate to the directory where you want your new project to be created, then run:
    ```bash
    cookiecutter /path/to/this/template/fastapi-class-based-template
    ```
    (Remember to replace `cookiecutter /path/to/this/template/fastapi-class-based-template` with the actual path to where you've saved this Cookiecutter template.)

3.  **Follow the prompts** to name your project.

4.  **Navigate into your new project directory:**
    ```bash
    cd {{ cookiecutter.project_slug }}
    ```

5.  **Install `uv`:**
    If you don't have `uv` installed globally, you can get it with `pip`:
    ```bash
    pip install uv
    ```
    Or, a recommended way is to use `pipx` for global CLI tools:
    ```bash
    pipx install uv
    ```

6.  **Set up the development environment with `uv`:**
    `uv` will read your `pyproject.toml` to understand your project's dependencies.
    ```bash
    uv sync
    ```
    This command will create a virtual environment (if one doesn't exist) and install all the project and development dependencies.

7.  **Install pre-commit hooks:**
    ```bash
    uv run pre-commit install
    ```
    This sets up the Git hooks that will run `ruff` and `pytest` automatically before each commit.

---

## **Running the Application and Tests**

### Running the FastAPI Application

Once your environment is set up, you can run the application using `uv run`:

```bash
uv run uvicorn main:app --reload
