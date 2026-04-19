---
name: 🐛 Bug Report
description: Report something that isn't working as expected
labels: ["bug", "triage"]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        Thank you for taking time to report a bug! 🙏
        Please fill out as much detail as you can so we can investigate quickly.

  - type: textarea
    id: description
    attributes:
      label: 📝 Description
      description: Clear description of the bug you encountered
      placeholder: |
        Example: "When I upload an NDVI image, the crop recommendation fails..."
    validations:
      required: true

  - type: textarea
    id: steps
    attributes:
      label: 🔍 Steps to Reproduce
      description: Exact steps to replicate the issue
      placeholder: |
        1. Start the backend with `docker run -p 8000:8000 krishi-veda`
        2. Open http://localhost:8000 in browser
        3. Click "Voice Input" button
        4. Say "Check my rice field"
        5. System crashes with error...
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: ✅ Expected Behavior
      description: What should happen instead?
      placeholder: "The system should return crop advisory in Bengali"
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: ❌ Actual Behavior
      description: What actually happened?
      placeholder: "Error 500: Internal server error"
    validations:
      required: true

  - type: dropdown
    id: environment
    attributes:
      label: 🖥️ Environment
      options:
        - Docker (Linux)
        - Local Python
        - Android (Termux)
        - HuggingFace Spaces
        - Other (please specify)
    validations:
      required: true

  - type: input
    id: os
    attributes:
      label: Operating System
      placeholder: "Ubuntu 22.04 / Windows 11 / Android 13 / macOS 14"
    validations:
      required: false

  - type: input
    id: python_version
    attributes:
      label: Python Version (if applicable)
      placeholder: "3.11.0"
    validations:
      required: false

  - type: textarea
    id: logs
    attributes:
      label: 📋 Error Logs
      description: Paste any error messages or logs
      render: bash
      placeholder: |
        Traceback (most recent call last):
          File "main.py", line 45, in get_advisory
            result = self.model.generate(...)
        RuntimeError: CUDA out of memory...

  - type: textarea
    id: context
    attributes:
      label: 📌 Additional Context
      description: Any other context (screenshots, config files, etc.)
      placeholder: "Using Qwen2 quantized model on 4GB RAM phone..."

  - type: checkboxes
    id: checklist
    attributes:
      label: ✓ Before You Submit
      description: Have you done these?
      options:
        - label: Searched existing issues for duplicates
          required: true
        - label: Provided clear reproduction steps
          required: true
        - label: Included error logs/screenshots
          required: false
