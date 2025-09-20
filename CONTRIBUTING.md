# Contributing to pywaifu

Thank you for your interest in contributing to pywaifu! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/waifuai/waifu-llm-vrm.git
   cd pywaifu
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m uv venv .venv

   # Activate environment
   source .venv/Scripts/activate  # On Windows: .venv\Scripts\activate

   # Install development dependencies
   python -m uv pip install -r requirements-dev.txt
   ```

3. **Set Up Pre-commit Hooks**
   ```bash
   # Install pre-commit
   python -m uv pip install pre-commit

   # Install hooks
   pre-commit install
   ```

## Development Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Follow PEP 8 style guidelines
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

3. **Run Tests**
   ```bash
   # Run all tests
   python -m pytest

   # Run with coverage
   python -m pytest --cov=src/pywaifu

   # Run specific tests
   python -m pytest src/pywaifu/tests/test_character.py
   ```

4. **Code Quality Checks**
   ```bash
   # Format code
   python -m black src/ examples/

   # Lint code
   python -m flake8 src/ examples/

   # Type checking
   python -m mypy src/
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

6. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style Guidelines

### Python Style
- Follow PEP 8
- Use 4 spaces for indentation
- Maximum line length: 88 characters (Black default)
- Use type hints for function parameters and return types

### Documentation
- Use docstrings for all public functions, classes, and methods
- Follow Google docstring format
- Document complex logic with inline comments

### Naming Conventions
- Classes: PascalCase
- Functions and variables: snake_case
- Constants: UPPER_SNAKE_CASE
- Private methods: _prefixed

### Error Handling
- Use custom exceptions where appropriate
- Provide meaningful error messages
- Log errors appropriately
- Don't expose internal implementation details in error messages

## Testing

### Unit Tests
- Write tests for all new functionality
- Use pytest framework
- Mock external dependencies
- Test edge cases and error conditions
- Aim for high test coverage

### Test Structure
```
src/pywaifu/tests/
├── __init__.py
├── test_character.py     # Character class tests
├── test_vrm.py          # VRMCharacter class tests
├── test_godot.py        # GodotConnector tests
└── test_utils.py        # Utility function tests
```

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=src/pywaifu --cov-report=html

# Specific test file
pytest src/pywaifu/tests/test_character.py

# Verbose output
pytest -v
```

## Pull Request Process

1. **Title**: Use conventional commit format
   - `feat:` new feature
   - `fix:` bug fix
   - `docs:` documentation changes
   - `style:` code style changes
   - `refactor:` code refactoring
   - `test:` test additions/modifications
   - `chore:` maintenance tasks

2. **Description**: Provide clear description of changes
   - What problem does this solve?
   - How does the solution work?
   - Any breaking changes?
   - Screenshots or examples if applicable

3. **Checklist**:
   - [ ] Code follows project style guidelines
   - [ ] Tests added/updated for new functionality
   - [ ] Documentation updated
   - [ ] All tests pass
   - [ ] Code reviewed by at least one other contributor

## Documentation

### Updating Documentation
- Update README.md for significant changes
- Add examples for new features
- Update docstrings for API changes
- Update type hints if needed

### Building Documentation
```bash
# Generate Sphinx documentation
cd docs/
make html
```

## Release Process

### Versioning
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update version in `pyproject.toml` or `__init__.py`
- Update CHANGELOG.md

### Release Steps
1. Create release branch
2. Update version numbers
3. Update changelog
4. Run full test suite
5. Create pull request
6. Merge to main
7. Create GitHub release
8. Publish to PyPI

## Community

### Getting Help
- Check existing issues and documentation first
- Use clear, descriptive issue titles
- Provide minimal reproducible examples
- Include relevant error messages and stack traces

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a positive community environment

## License

By contributing to pywaifu, you agree that your contributions will be licensed under the same license as the project (MIT-0 License).