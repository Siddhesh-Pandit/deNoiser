# Which Documentation Should I Read?

Quick guide to help you find the right documentation.

```
                    ┌─────────────────────┐
                    │   Are you a...?     │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
         ┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
         │ Basic User  │ │ Advanced │ │ Developer  │
         │ (Just want  │ │   User   │ │ (Want to   │
         │  to use it) │ │ (Customize)│ modify code)│
         └──────┬──────┘ └────┬─────┘ └─────┬──────┘
                │              │              │
                │              │              │
         ┌──────▼──────────────▼──────────────▼──────┐
         │                                            │
         │  📄 START_HERE.md                          │
         │  (Read this first - 5 minutes)             │
         │                                            │
         └──────┬──────────────┬──────────────┬──────┘
                │              │              │
                │              │              │
         ┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
         │   DONE! ✅  │ │ USAGE.md │ │ All docs   │
         │             │ │ (Advanced│ │ (Everything)│
         │             │ │ features)│ │            │
         └─────────────┘ └──────────┘ └────────────┘
```

---

## By User Type

### 🎯 Basic User (90% of users)

**Goal:** Just want to denoise some images

**Read:**
1. **START_HERE.md** ← That's it!

**Don't Read:**
- ❌ Everything else (unless you have problems)

---

### 🔧 Advanced User

**Goal:** Want to customize settings, understand filters

**Read:**
1. **START_HERE.md** (get started)
2. **USAGE.md** (learn advanced features)

**Optional:**
- CHANGELOG.md (see what's new)

---

### 👨‍💻 Developer

**Goal:** Want to modify code or build executables

**Read:**
1. **START_HERE.md** (get started)
2. **README.md** (project overview)
3. **USAGE.md** (understand features)
4. **BUILD_INSTRUCTIONS.md** (if building executables)
5. **DEPENDENCY_AUDIT.md** (if modifying dependencies)

---

## By Problem

### "I can't get it installed"

**Windows:**
1. Try **START_HERE.md** first
2. Still stuck? → **WINDOWS_INSTALL.md** (detailed troubleshooting)

**Mac/Linux:**
1. Try **START_HERE.md** first
2. Still stuck? → **README.md** (troubleshooting section)

---

### "I don't know which settings to use"

**Read:** **START_HERE.md** → Use presets (📷 Photos, 📄 Documents, 🌙 Low-Light)

**Want to understand more?** → **USAGE.md** (filter explanations)

---

### "I want to understand what each filter does"

**Read:** **USAGE.md** → "How It Works" section

---

### "I want to build my own .exe"

**Read:** **BUILD_INSTRUCTIONS.md**

---

### "I'm getting errors"

**Windows:** **WINDOWS_INSTALL.md** → Troubleshooting section

**Other:** **USAGE.md** → Troubleshooting section

---

## Complete Documentation List

### For Users

| File | Who Needs It | Time |
|------|-------------|------|
| **START_HERE.md** | Everyone | 5 min |
| **USAGE.md** | Advanced users | 20 min |
| **QUICKSTART_WINDOWS.md** | Windows users (alternative to START_HERE) | 5 min |
| **WINDOWS_INSTALL.md** | Windows troubleshooting | 15 min |

### For Developers

| File | Purpose |
|------|---------|
| **README.md** | Project overview |
| **BUILD_INSTRUCTIONS.md** | Building executables |
| **DEPENDENCY_AUDIT.md** | Dependency reference |
| **CHANGELOG.md** | Version history |

### Meta (You Don't Need These)

| File | Purpose |
|------|---------|
| **INSTALLATION_SUMMARY.md** | Overview of all docs |
| **WHICH_DOCS_TO_READ.md** | This file |
| **COMMIT_MESSAGE.md** | For maintainers |
| **GITHUB_RELEASE.md** | For maintainers |

---

## Quick Decision Tree

```
Do you just want to use the app?
├─ YES → Read START_HERE.md only
└─ NO
   │
   Do you want to customize settings?
   ├─ YES → Read START_HERE.md + USAGE.md
   └─ NO
      │
      Do you want to modify the code?
      ├─ YES → Read all developer docs
      └─ NO → Why are you here? 😄
```

---

## TL;DR

**99% of users only need:** **START_HERE.md**

Everything else is optional or for specific situations.
