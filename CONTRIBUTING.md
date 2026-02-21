# Contributing to TaskSync

We'd love your contributions to TaskSync! Here are some guidelines to help you get started.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/tasksync.git`
3. Create a virtual environment: `python -m venv .venv`
4. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
5. Install development dependencies: `pip install -e ".[dev]"`

## Development Workflow

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Write or update tests for your changes
4. Run tests: `pytest`
5. Format code: `black tasksync/`
6. Check imports: `isort tasksync/`
7. Lint code: `flake8 tasksync/`
8. Commit your changes: `git commit -m 'Add my feature'`
9. Push to your fork: `git push origin feature/my-feature`
10. Open a Pull Request

## Code Style

- Use Black for code formatting
- Use isort for import sorting
- Follow PEP 8 guidelines
- Maximum line length: 100 characters
- Write descriptive docstrings

## Testing

- Write tests for new features
- Ensure all tests pass: `pytest`
- Aim for high test coverage
- Test both happy paths and edge cases

## Pull Request Process

1. Update README.md with any new features or changes
2. Ensure all tests pass
3. Update CHANGELOG.md if applicable
4. Reference any related issues in your PR description
5. Wait for code review and feedback

## Reporting Bugs

1. Use the GitHub issue tracker
2. Describe the bug clearly
3. Include steps to reproduce
4. Include expected vs. actual behavior
5. Include your environment details (OS, Python version, etc.)

## Feature Requests

1. Use the GitHub issue tracker
2. Describe the feature and why it would be useful
3. Provide any relevant examples or use cases

## Questions?

Feel free to open an issue or reach out to the maintainers.

Thank you for contributing!
