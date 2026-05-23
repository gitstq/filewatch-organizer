# 📁 FileWatch-Organizer

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-orange.svg)]()

**🌍 [English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)**

</div>

---

<a name="english"></a>
## 🇺🇸 English

### 🎉 Project Introduction

**FileWatch-Organizer** is a lightweight, zero-dependency file system intelligent monitoring and auto-organization engine. It solves the daily pain point of messy file management by automatically monitoring folder changes and intelligently organizing files based on customizable rules.

**Key Differentiators:**
- 🚀 **Zero Dependencies** - Pure Python standard library, no external packages
- 🖥️ **Cross-Platform** - Works on Windows, macOS, and Linux
- ⚡ **Lightweight** - Minimal resource usage, perfect for background monitoring
- 🎯 **Rule-Based** - Flexible organization strategies via YAML/JSON configuration
- 📊 **TUI Dashboard** - Beautiful terminal interface for real-time monitoring

### ✨ Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| 📡 **Real-time Monitoring** | Watch folders for create/modify/delete/move events | ✅ |
| 📂 **Smart Organization** | Auto-sort by file type, date, size, or custom patterns | ✅ |
| 🔍 **Duplicate Detection** | Find and remove duplicate files by hash or name/size | ✅ |
| 🏷️ **Project Detection** | Automatically detect and organize by project type | ✅ |
| 📦 **Archive Support** | Auto-archive old files based on age thresholds | ✅ |
| 🎨 **TUI Dashboard** | Interactive terminal UI with live statistics | ✅ |
| 🔧 **CLI Interface** | Full command-line control with multiple subcommands | ✅ |
| 📝 **Configurable** | JSON-based configuration with preset templates | ✅ |

### 🚀 Quick Start

#### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/filewatch-organizer.git
cd filewatch-organizer

# Install in development mode
pip install -e .

# Or install directly
pip install .
```

#### Basic Usage

```bash
# Initialize configuration
filewatch-organizer config --init

# Watch a directory
filewatch-organizer watch ~/Downloads

# Organize files by type
filewatch-organizer organize ~/Downloads --by-type

# Apply preset configuration
filewatch-organizer preset downloads --path ~/Downloads

# Launch TUI dashboard
filewatch-organizer tui
```

#### Using Presets

```bash
# Downloads folder preset (organizes by type and date)
filewatch-organizer preset downloads --path ~/Downloads

# Workspace preset (organizes by project type)
filewatch-organizer preset workspace --path ~/Projects

# Documents preset (organizes by category)
filewatch-organizer preset documents --path ~/Documents
```

### 📖 Detailed Usage Guide

#### Watch Command

```bash
# Watch with auto-organize
filewatch-organizer watch ~/Downloads --auto-organize

# Watch multiple paths
filewatch-organizer watch ~/Downloads ~/Desktop --recursive
```

#### Organize Command

```bash
# Organize by file type
filewatch-organizer organize ~/Downloads --by-type

# Organize by date
filewatch-organizer organize ~/Downloads --by-date

# Remove duplicates
filewatch-organizer organize ~/Downloads --dedup

# Dry run (preview changes)
filewatch-organizer organize ~/Downloads --by-type --dry-run
```

#### Configuration

Configuration is stored in `~/.config/filewatch-organizer/config.json`:

```json
{
  "watch_paths": [
    {"path": "/home/user/Downloads", "recursive": true}
  ],
  "organization_rules": [
    {
      "name": "sort_images",
      "enabled": true,
      "action": "organize_by_type",
      "target_folder": "{watch_path}/Images"
    }
  ],
  "file_types": {
    "images": [".jpg", ".png", ".gif"],
    "documents": [".pdf", ".docx"]
  }
}
```

### 💡 Design Philosophy

**Why FileWatch-Organizer?**

1. **Simplicity First** - No complex setup, works out of the box
2. **Privacy Focused** - All processing happens locally, no cloud
3. **Developer Friendly** - Easy to extend with custom rules
4. **Resource Efficient** - Polling-based monitoring with minimal CPU usage

**Technical Highlights:**
- Pure Python standard library (no pip dependencies)
- Thread-safe file operations
- Debounced event handling to prevent duplicates
- Hash-based deduplication (MD5/SHA256)

### 📦 Packaging & Deployment

#### Build from Source

```bash
# Build wheel
python -m build

# Install from wheel
pip install dist/filewatch_organizer-1.0.0-py3-none-any.whl
```

#### Run Without Installation

```bash
python -m filewatch_organizer --help
```

### 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
## 🇨🇳 简体中文

### 🎉 项目介绍

**FileWatch-Organizer** 是一款轻量级、零依赖的文件系统智能监控与自动整理引擎。它解决了日常文件管理混乱的痛点，通过自动监控文件夹变化并根据可自定义规则智能整理文件。

**核心差异化亮点：**
- 🚀 **零依赖** - 纯Python标准库，无需外部包
- 🖥️ **跨平台** - 支持Windows、macOS和Linux
- ⚡ **轻量级** - 资源占用极低，适合后台监控
- 🎯 **基于规则** - 通过YAML/JSON配置灵活的整理策略
- 📊 **TUI仪表板** - 美观的终端界面，实时监控

### ✨ 核心特性

| 特性 | 描述 | 状态 |
|------|------|------|
| 📡 **实时监控** | 监控文件夹的创建/修改/删除/移动事件 | ✅ |
| 📂 **智能整理** | 按文件类型、日期、大小或自定义模式自动分类 | ✅ |
| 🔍 **重复检测** | 通过哈希或名称/大小查找并删除重复文件 | ✅ |
| 🏷️ **项目检测** | 自动检测并按项目类型整理 | ✅ |
| 📦 **归档支持** | 基于年龄阈值自动归档旧文件 | ✅ |
| 🎨 **TUI仪表板** | 交互式终端UI，实时统计 | ✅ |
| 🔧 **CLI界面** | 完整的命令行控制，多个子命令 | ✅ |
| 📝 **可配置** | 基于JSON的配置，预设模板 | ✅ |

### 🚀 快速开始

#### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/filewatch-organizer.git
cd filewatch-organizer

# 开发模式安装
pip install -e .

# 或直接安装
pip install .
```

#### 基本用法

```bash
# 初始化配置
filewatch-organizer config --init

# 监控目录
filewatch-organizer watch ~/Downloads

# 按类型整理文件
filewatch-organizer organize ~/Downloads --by-type

# 应用预设配置
filewatch-organizer preset downloads --path ~/Downloads

# 启动TUI仪表板
filewatch-organizer tui
```

#### 使用预设

```bash
# 下载文件夹预设（按类型和日期整理）
filewatch-organizer preset downloads --path ~/Downloads

# 工作区预设（按项目类型整理）
filewatch-organizer preset workspace --path ~/Projects

# 文档预设（按类别整理）
filewatch-organizer preset documents --path ~/Documents
```

### 📖 详细使用指南

#### 监控命令

```bash
# 监控并自动整理
filewatch-organizer watch ~/Downloads --auto-organize

# 监控多个路径
filewatch-organizer watch ~/Downloads ~/Desktop --recursive
```

#### 整理命令

```bash
# 按文件类型整理
filewatch-organizer organize ~/Downloads --by-type

# 按日期整理
filewatch-organizer organize ~/Downloads --by-date

# 删除重复文件
filewatch-organizer organize ~/Downloads --dedup

# 试运行（预览更改）
filewatch-organizer organize ~/Downloads --by-type --dry-run
```

#### 配置

配置存储在 `~/.config/filewatch-organizer/config.json`：

```json
{
  "watch_paths": [
    {"path": "/home/user/Downloads", "recursive": true}
  ],
  "organization_rules": [
    {
      "name": "sort_images",
      "enabled": true,
      "action": "organize_by_type",
      "target_folder": "{watch_path}/Images"
    }
  ],
  "file_types": {
    "images": [".jpg", ".png", ".gif"],
    "documents": [".pdf", ".docx"]
  }
}
```

### 💡 设计理念

**为什么选择FileWatch-Organizer？**

1. **简约优先** - 无需复杂设置，开箱即用
2. **注重隐私** - 所有处理都在本地进行，不上云
3. **开发者友好** - 易于使用自定义规则扩展
4. **资源高效** - 基于轮询的监控，CPU占用极低

**技术亮点：**
- 纯Python标准库（无pip依赖）
- 线程安全的文件操作
- 防抖事件处理，防止重复
- 基于哈希的去重（MD5/SHA256）

### 📦 打包与部署

#### 从源码构建

```bash
# 构建wheel
python -m build

# 从wheel安装
pip install dist/filewatch_organizer-1.0.0-py3-none-any.whl
```

#### 免安装运行

```bash
python -m filewatch_organizer --help
```

### 🤝 贡献指南

欢迎贡献！请遵循以下步骤：
1. Fork仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

### 📄 开源协议

本项目采用MIT协议开源 - 详见 [LICENSE](LICENSE) 文件。

---

<a name="繁體中文"></a>
## 🇹🇼 繁體中文

### 🎉 專案介紹

**FileWatch-Organizer** 是一款輕量級、零依賴的檔案系統智能監控與自動整理引擎。它解決了日常檔案管理混亂的痛點，通過自動監控資料夾變化並根據可自定義規則智能整理檔案。

**核心差異化亮點：**
- 🚀 **零依賴** - 純Python標準庫，無需外部套件
- 🖥️ **跨平台** - 支援Windows、macOS和Linux
- ⚡ **輕量級** - 資源佔用極低，適合背景監控
- 🎯 **基於規則** - 通過YAML/JSON配置靈活的整理策略
- 📊 **TUI儀表板** - 美觀的終端介面，即時監控

### ✨ 核心特性

| 特性 | 描述 | 狀態 |
|------|------|------|
| 📡 **即時監控** | 監控資料夾的建立/修改/刪除/移動事件 | ✅ |
| 📂 **智能整理** | 按檔案類型、日期、大小或自定義模式自動分類 | ✅ |
| 🔍 **重複檢測** | 通過雜湊或名稱/大小查找並刪除重複檔案 | ✅ |
| 🏷️ **專案檢測** | 自動檢測並按專案類型整理 | ✅ |
| 📦 **歸檔支援** | 基於年齡閾值自動歸檔舊檔案 | ✅ |
| 🎨 **TUI儀表板** | 互動式終端UI，即時統計 | ✅ |
| 🔧 **CLI介面** | 完整的命令列控制，多個子命令 | ✅ |
| 📝 **可配置** | 基於JSON的配置，預設模板 | ✅ |

### 🚀 快速開始

#### 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/filewatch-organizer.git
cd filewatch-organizer

# 開發模式安裝
pip install -e .

# 或直接安裝
pip install .
```

#### 基本用法

```bash
# 初始化配置
filewatch-organizer config --init

# 監控目錄
filewatch-organizer watch ~/Downloads

# 按類型整理檔案
filewatch-organizer organize ~/Downloads --by-type

# 應用預設配置
filewatch-organizer preset downloads --path ~/Downloads

# 啟動TUI儀表板
filewatch-organizer tui
```

#### 使用預設

```bash
# 下載資料夾預設（按類型和日期整理）
filewatch-organizer preset downloads --path ~/Downloads

# 工作區預設（按專案類型整理）
filewatch-organizer preset workspace --path ~/Projects

# 文件預設（按類別整理）
filewatch-organizer preset documents --path ~/Documents
```

### 📖 詳細使用指南

#### 監控命令

```bash
# 監控並自動整理
filewatch-organizer watch ~/Downloads --auto-organize

# 監控多個路徑
filewatch-organizer watch ~/Downloads ~/Desktop --recursive
```

#### 整理命令

```bash
# 按檔案類型整理
filewatch-organizer organize ~/Downloads --by-type

# 按日期整理
filewatch-organizer organize ~/Downloads --by-date

# 刪除重複檔案
filewatch-organizer organize ~/Downloads --dedup

# 試運行（預覽更改）
filewatch-organizer organize ~/Downloads --by-type --dry-run
```

#### 配置

配置存儲在 `~/.config/filewatch-organizer/config.json`：

```json
{
  "watch_paths": [
    {"path": "/home/user/Downloads", "recursive": true}
  ],
  "organization_rules": [
    {
      "name": "sort_images",
      "enabled": true,
      "action": "organize_by_type",
      "target_folder": "{watch_path}/Images"
    }
  ],
  "file_types": {
    "images": [".jpg", ".png", ".gif"],
    "documents": [".pdf", ".docx"]
  }
}
```

### 💡 設計理念

**為什麼選擇FileWatch-Organizer？**

1. **簡約優先** - 無需複雜設定，開箱即用
2. **注重隱私** - 所有處理都在本地進行，不上雲
3. **開發者友善** - 易於使用自定義規則擴展
4. **資源高效** - 基於輪詢的監控，CPU佔用極低

**技術亮點：**
- 純Python標準庫（無pip依賴）
- 執行緒安全的檔案操作
- 防抖事件處理，防止重複
- 基於雜湊的去重（MD5/SHA256）

### 📦 打包與部署

#### 從原始碼構建

```bash
# 構建wheel
python -m build

# 從wheel安裝
pip install dist/filewatch_organizer-1.0.0-py3-none-any.whl
```

#### 免安裝執行

```bash
python -m filewatch_organizer --help
```

### 🤝 貢獻指南

歡迎貢獻！請遵循以下步驟：
1. Fork倉庫
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 建立Pull Request

### 📄 開源協議

本專案採用MIT協議開源 - 詳見 [LICENSE](LICENSE) 檔案。

---

<div align="center">

**Made with ❤️ by FileWatch Team**

</div>
