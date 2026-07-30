# Contributing to TikTok Decoder

Thank you for considering contributing to **TikTok Decoder**! We welcome bug reports, feature requests, code improvements, and documentation fixes.

---

## 🤝 How to Contribute

### 1. Reporting Bugs
- Search existing [GitHub Issues](https://github.com/ryoqe/TikTok-Decoder/issues) to ensure the bug hasn't already been reported.
- If not, open a new issue using the **Bug Report** template.
- Include your OS, Python version, FFmpeg version, and console logs.

### 2. Suggesting Enhancements
- Open a new issue using the **Feature Request** template.
- Explain the use case and how the proposed change benefits users.

### 3. Submitting Pull Requests (PRs)

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/<your-username>/TikTok-Decoder.git
   cd TikTok-Decoder
   ```
3. **Create a new branch** for your feature or fix:
   ```bash
   git checkout -b feature/my-new-feature
   ```
4. **Make your changes** and test thoroughly:
   ```bash
   # Test CLI interface
   python main.py -h
   
   # Compile check
   python -m compileall src main.py gui.py
   ```
5. **Commit your changes**:
   ```bash
   git commit -m "feat: describe your change"
   ```
6. **Push to your fork** and submit a Pull Request against the `main` branch.

---

## 📜 Code Style Guidelines
- Follow standard Python PEP 8 conventions.
- Keep module dependencies clean and self-contained inside `src/`.
- Ensure new CLI arguments are properly documented in `main.py`.

Thank you for making **TikTok Decoder** better for everyone! 🚀
