Remove-Item -Force .\.coverage -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\htmlcov -ErrorAction SilentlyContinue
Pytest --cov=src --cov-report=term-missing