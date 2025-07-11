# 🚀 FastAPI Project Template (Cookiecutter)

---

This repository provides a robust and opinionated Cookiecutter template for quickly bootstrapping new FastAPI projects. It aims to set up a clean, scalable, and well-structured foundation with modern Python development best practices, including asynchronous capabilities, database integration, and pre-configured tools for linting, formatting, and testing using `uv` and `ruff`.

---
## ✨ Features of the Generated Project

* **FastAPI:** High-performance, easy to use, web framework for building APIs.
* **SQLAlchemy (Async):** Asynchronous ORM for database interactions.
* **Pydantic:** Data validation and settings management.
* **`uv`:** Modern, fast dependency management and execution for Python projects.
* **`ruff`:** An extremely fast Python linter and formatter, replacing Black, isort, and Flake8.
* **Pytest & Pytest-Cov:** Comprehensive testing framework with code coverage reporting.
* **Modular Structure:** Organized into `api`, `schemas`, `database`, `config`, etc., for maintainability.
* **FastAPI Dependency Injection:** Structured use of FastAPI's dependency system.
* **Basic API Versioning (Optional):** Setup for `api/v1` routes.

---

## ⚡ How to Use This Template

To use this template, you need `cookiecutter` installed. If you don't have it, install it via pip:

```bash
pip install cookiecutter
cookiecutter [https://github.com/peter-daptl/fastapi-template.git](https://github.com/peter-daptl/fastapi-template.git)
