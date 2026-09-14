# 🤝 Contributing to DDMS

Thank you for your interest in making space safer! This guide will help you contribute effectively to the Differential Drag Maneuvering System project.

---

## 🎯 **Types of Contributions Welcome**

### 💻 **Code**
- **Core Algorithms:** Improve DDME, AECRM, orbital mechanics
- **Dashboard:** Enhance PVSD UI/UX, add new visualization features
- **Tests:** Expand test coverage, add edge cases
- **Examples:** Create tutorials for users
- **Embedded C:** Optimize microcontroller implementations

### 📚 **Documentation**
- **API Docs:** Fill in missing docstrings
- **Tutorials:** Write "how-to" guides
- **Architecture:** Clarify complex components
- **Case Studies:** Document real-world integrations

### 🐛 **Bug Reports**
- Reproduce issues reliably
- Include environment details
- Provide minimum reproducible example

### 💡 **Feature Requests**
- Explain the use case
- Describe desired behavior
- Link to related issues

### 🌍 **Community**
- Answer questions in Discussions
- Review pull requests
- Promote DDMS in your network

---

## 🚀 **Getting Started**

### **1. Fork & Clone**
```bash
git clone https://github.com/YOUR-USERNAME/differential-drag-collision-avoidance.git
cd differential-drag-collision-avoidance
```

### **2. Set Up Development Environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Testing, linting, formatting

# Install pre-commit hooks
pre-commit install
```

### **3. Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/your-bug-name
```

### **4. Make Changes**
```bash
# Edit files, write tests
pytest tests/  # Run tests locally
pylint core/  # Check code quality
black --check core/  # Check formatting
```

### **5. Commit & Push**
```bash
git add .
git commit -m "Brief description of changes"
# Commit message format:
# Type: Subject (max 50 chars)
# 
# Detailed explanation (max 72 chars per line)
# 
# - Point 1
# - Point 2
#
# Fixes #issue_number

git push origin feature/your-feature-name
```

### **6. Create Pull Request**
- Go to GitHub repository
- Click "Compare & pull request"
- Fill in PR template:
  - **What:** Brief description
  - **Why:** Motivation & context
  - **How:** Technical approach
  - **Testing:** How you tested changes
  - **Related Issues:** Links to issues

---

## 📝 **Commit Message Guidelines**

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting (no logic change)
- `refactor:` Code restructuring
- `perf:` Performance improvement
- `test:` Adding tests

**Examples:**
```
feat(aecrm): add sensor fusion for LIDAR data

Implement Kalman filter for combining TLE ephemeris with
LIDAR ranging data. Reduces uncertainty ellipsoid by 40%.

Fixes #123
```

---

## 🧪 **Testing Requirements**

### **Unit Tests**
```bash
# Test single module
pytest tests/unit/test_drag_model.py

# Test with coverage
pytest --cov=core tests/
```

### **Integration Tests**
```bash
pytest tests/integration/
```

### **Test Coverage Minimum**
- Core logic: **≥ 80% coverage**
- New features: **≥ 70% coverage**
- Critical paths: **100% coverage**

### **Writing Tests**
```python
import pytest
from core.aecrm import conjunction_assessor

class TestConjunctionAssessor:
    def test_collision_probability_high_risk(self):
        """Test that high-risk conjunction is detected."""
        ca = conjunction_assessor.ConjunctionAssessor()
        pc = ca.compute_probability(doca=100, uncertainty=50)
        assert pc > 1e-3  # High risk
    
    def test_collision_probability_low_risk(self):
        """Test that low-risk conjunction is accepted."""
        ca = conjunction_assessor.ConjunctionAssessor()
        pc = ca.compute_probability(doca=10000, uncertainty=1000)
        assert pc < 1e-5  # Low risk
```

---

## 🎨 **Code Style**

### **Python Style Guide**
Follow **PEP 8** with these tools:

```bash
# Format code
black core/ tests/

# Check style
pylint core/
flake8 core/

# Type checking
mypy core/
```

### **Code Example**
```python
"""Conjunction assessment module."""

from typing import Tuple
import numpy as np

class ConjunctionAssessor:
    """Compute collision probability between satellite and debris."""
    
    def __init__(self, min_pc_threshold: float = 1e-4):
        """Initialize with risk threshold.
        
        Args:
            min_pc_threshold: Minimum collision probability to trigger alert.
        """
        self.min_pc_threshold = min_pc_threshold
    
    def compute_probability(
        self,
        doca: float,
        uncertainty: float
    ) -> float:
        """Compute collision probability using Mahalanobis distance.
        
        Args:
            doca: Distance of closest approach (meters)
            uncertainty: Position uncertainty (sigma, meters)
        
        Returns:
            Collision probability (0.0 to 1.0)
        """
        # Implementation here
        pass
```

---

## 📖 **Documentation Standards**

### **Docstring Format (Google Style)**
```python
def compute_drag_coefficient(
    altitude_km: float,
    surface_roughness: float = 0.5
) -> float:
    """Compute atmospheric drag coefficient at given altitude.
    
    Uses MSISE-00 atmospheric model with surface properties.
    
    Args:
        altitude_km: Orbital altitude in kilometers.
        surface_roughness: Surface finish (0.0-1.0, default smooth).
    
    Returns:
        Drag coefficient (typically 2.0-2.5 for satellites).
    
    Raises:
        ValueError: If altitude < 200 km (too low) or > 2000 km.
    
    Example:
        >>> cd = compute_drag_coefficient(400, 0.5)
        >>> print(f"Cd = {cd:.3f}")
        Cd = 2.237
    
    References:
        - Picone, J. M., et al. (2002). NRLMSISE-00 Atmosphere Model
    """
    pass
```

### **README & Documentation**
- Use clear headings (H1-H4)
- Include code examples
- Link to related sections
- Add diagrams for complex concepts
- Keep technical language accessible

---

## 🔄 **Review Process**

### **Automated Checks**
Your PR will automatically run:
- Unit tests (`pytest`)
- Code quality (`pylint`, `flake8`)
- Type checking (`mypy`)
- Coverage reports

### **Manual Review**
Maintainers will review:
- **Correctness:** Does code do what it claims?
- **Design:** Is approach sound?
- **Testing:** Is coverage adequate?
- **Documentation:** Is change documented?
- **Performance:** Will it scale?

### **Feedback Cycle**
- Respond to reviewer comments within 1 week
- Make requested changes and push new commits
- Re-request review after changes

---

## 🏆 **Recognition**

Contributors are recognized in:
- **README.md** - Major contributors section
- **CHANGELOG.md** - Release notes
- **GitHub Contributors** - Automatic tracking
- **Project website** - Featured contributors

---

## 📋 **Development Workflow**

### **Issue → PR → Merge**
```
1. Open Issue (or find existing one)
   ├─ Describe problem/feature
   ├─ Include context
   └─ Get approval from maintainers
         ↓
2. Fork & Branch
   ├─ git checkout -b feature/name
   └─ Make changes with tests
         ↓
3. Push & Create PR
   ├─ Include reference to issue
   ├─ Describe changes
   └─ Wait for CI checks
         ↓
4. Code Review
   ├─ Respond to feedback
   ├─ Make revisions
   └─ Get approvals (≥ 2 reviewers)
         ↓
5. Merge
   ├─ Squash or rebase commits
   ├─ Update CHANGELOG.md
   └─ Branch auto-deleted
         ↓
6. Deploy
   ├─ Release to PyPI
   ├─ Tag version
   └─ Announce on social media
```

---

## 🚨 **Code of Conduct**

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful of different viewpoints
- Welcome newcomers and help them succeed
- Focus on constructive feedback
- Report inappropriate behavior to maintainers

Read full [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

---

## ❓ **Questions?**

- **GitHub Discussions:** Ask in [Discussions tab](https://github.com/mugilangs2009-cloud/differential-drag-collision-avoidance/discussions)
- **Issues:** Comment on related [Issues](https://github.com/mugilangs2009-cloud/differential-drag-collision-avoidance/issues)
- **Email:** Contact maintainers (see README)

---

## 🙏 **Thank You**

Every contribution—big or small—helps make space safer for everyone. We appreciate your effort!

**Happy coding! 🚀**
