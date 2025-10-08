# Contributing to Agentic AI Framework

First off, thank you for considering contributing to the Agentic AI Framework! It's people like you that make this project such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our commitment to providing a welcoming and inspiring community for all.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples**
* **Describe the behavior you observed and what you expected**
* **Include screenshots if relevant**
* **Note your environment** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

* **Use a clear and descriptive title**
* **Provide a detailed description of the suggested enhancement**
* **Explain why this enhancement would be useful**
* **List any alternatives you've considered**

### Pull Requests

* Fill in the required template
* Follow the Python style guide (PEP 8)
* Include tests for new features
* Update documentation as needed
* Ensure all tests pass

## Development Process

1. **Fork the repo** and create your branch from `main`
2. **Install dependencies**: `./setup.sh`
3. **Make your changes** and add tests
4. **Run tests**: `pytest tests/`
5. **Ensure code quality**: `black . && flake8`
6. **Update documentation** if needed
7. **Commit your changes** with a clear message
8. **Push to your fork** and submit a pull request

## Style Guidelines

### Python Code Style

* Follow PEP 8
* Use meaningful variable names
* Add docstrings to all functions and classes
* Keep functions focused and small
* Use type hints where appropriate

Example:
```python
def process_data(input_data: List[str]) -> Dict[str, Any]:
    """Process input data and return results.
    
    Args:
        input_data: List of strings to process
        
    Returns:
        Dictionary with processed results
    """
    # Implementation
    pass
```

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters
* Reference issues and pull requests after the first line

### Documentation

* Use Markdown for documentation
* Keep language clear and concise
* Include code examples where helpful
* Update README.md if adding major features

## Testing

* Write unit tests for new features
* Ensure all existing tests pass
* Aim for high test coverage
* Use meaningful test names

```python
def test_agent_processes_input_correctly():
    """Test that agent correctly processes user input."""
    # Test implementation
    pass
```

## Project Structure

When adding new features, follow the existing structure:

```
aiagentic/
├── agents/       # New agents go here
├── core/         # Core framework (be careful!)
├── tools/        # New tools here
├── memory/       # Memory implementations
└── tests/        # Tests mirror the structure
```

## Recognition

Contributors will be recognized in:
* README.md Contributors section
* Release notes
* Project documentation

Thank you for contributing! 🎉
