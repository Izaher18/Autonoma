# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of the Agentic AI Framework seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please DO NOT report security vulnerabilities through public GitHub issues.

Instead, please report them via email to: [your-email@example.com]

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the following information in your report:

* Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
* Full paths of source file(s) related to the issue
* The location of the affected source code (tag/branch/commit or direct URL)
* Any special configuration required to reproduce the issue
* Step-by-step instructions to reproduce the issue
* Proof-of-concept or exploit code (if possible)
* Impact of the issue, including how an attacker might exploit it

### What to expect

* We will acknowledge receipt of your vulnerability report
* We will confirm the vulnerability and determine its impact
* We will release a fix as soon as possible
* We will publicly disclose the vulnerability after a fix is available

## Security Best Practices

When using this framework:

1. **API Keys**: Never commit API keys to the repository
   - Use `.env` files (already in `.gitignore`)
   - Use environment variables in production
   - Rotate keys regularly

2. **Dependencies**: Keep dependencies up to date
   - Run `pip install --upgrade -r requirements.txt` regularly
   - Monitor for security advisories

3. **Input Validation**: Always validate user input
   - The framework provides basic validation
   - Add additional checks for your use case

4. **Memory Storage**: Be cautious with stored data
   - Don't store sensitive information in memory systems
   - Encrypt sensitive data if storage is necessary
   - Use secure file permissions

5. **Access Control**: Implement proper access controls
   - Use authentication for production deployments
   - Implement rate limiting
   - Log access attempts

## Known Security Considerations

* This framework integrates with external LLM APIs (OpenAI, Anthropic)
* Memory systems store data in JSON files by default
* No built-in authentication (add for production use)
* Logs may contain sensitive information

## Updates

Subscribe to security announcements by watching this repository.
