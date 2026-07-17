# 🤝 Contributing to AquaSentinel-AI

We welcome contributions to the AquaSentinel-AI Agentic Platform! Follow these guidelines to keep code quality consistent and deployment-ready.

---

## 🌿 Git Branching Workflow
1. Create a branch from `release/v1.0` or `main`:
   * Feature Branch: `feature/name`
   * Bug Fix: `bugfix/issue`
2. Keep commits atomic and descriptive.
3. Submit a Pull Request targeting `release/v1.0` or `main`.

---

## 🐍 Python Coding Standards
* Follow **PEP 8** style guidelines.
* Preserve existing comments and docstrings.
* Use type annotations for all new function signatures.
* Ensure all new REST endpoints are fully authenticated using the `get_current_user` Bearer dependency injection helper.

---

## 🗄️ Database Migrations
Always use Alembic when adding or modifying SQLAlchemy schemas:
1. Make structural adjustments in [backend/app/models/db_models.py](file:///e:/Projects/AquaSentinel-AI-main/backend/app/models/db_models.py).
2. Generate migration script:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```
3. Verify that SQLite-specific commands use `batch_alter_table` contexts to prevent database transaction errors.
4. Upgrade your local database:
   ```bash
   alembic upgrade head
   ```

---

## 🧪 Testing Guidelines
Run tests locally before proposing any changes:
```bash
# Run pytest in the testing environment
$env:APP_ENV="testing"; pytest backend/app/tests/

# Run Milestone 4 offline vision scenarios
python backend/app/tests/test_milestone4.py
```
Ensure all automated checkmarks pass successfully!
