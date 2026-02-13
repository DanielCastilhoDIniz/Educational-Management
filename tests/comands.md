Remove-Item -Force .\.coverage -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\htmlcov -ErrorAction SilentlyContinue
ytest --cov=domain --cov-report=term-missing