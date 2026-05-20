# 发布到 PyPI

本文档说明如何将 `runninghub-sdk` 发布到 PyPI。

当前仓库的发布方式有两个特点：

- 包版本不是手动写在 `pyproject.toml` 里，而是由 `setuptools-scm` 根据 Git tag 自动生成。
- 仓库已经提供了 GitHub Actions 工作流 `.github/workflows/publish.yml`，推送 `v*` tag 后会自动构建并发布到 PyPI。

## 1. 发布前提

请先确认以下条件：

- 你拥有该项目对应的 PyPI 项目权限。
- 你已经在 GitHub 仓库的 `Settings -> Secrets and variables -> Actions` 中配置好 `PYPI_API_TOKEN`。
- 本地环境可以正常执行 Python 打包命令。
- 当前工作区根目录就是本项目目录。

建议先升级打包工具：

```bash
python -m pip install --upgrade pip build twine setuptools setuptools-scm wheel
```

或者直接安装项目开发依赖：

```bash
pip install -e .[dev]
```

## 2. 版本规则

本项目在 `pyproject.toml` 中使用了以下配置：

```toml
[project]
dynamic = ["version"]

[tool.setuptools_scm]
tag_regex = "^v(?P<version>.*)$"
local_scheme = "no-local-version"
```

这意味着：

- 版本号来自 Git tag。
- tag 必须使用 `v` 前缀，例如 `v0.1.0`、`v1.2.3`。
- 发布到 PyPI 的实际版本号会去掉前缀，变成 `0.1.0`、`1.2.3`。
- `local_scheme = "no-local-version"` 可以避免生成带 `+gHASH` 的本地版本号，减少 PyPI 拒收风险。

发布前可以先看一下现有 tag：

```bash
git tag --list
```

## 3. 本地构建与校验

正式发布前，建议先在本地完成一次完整构建检查。

先清理旧产物：

```bash
rm -rf build dist src/*.egg-info
```

再执行构建：

```bash
python -m build
```

检查生成结果：

```bash
python -m twine check dist/*
```

如需确认当前版本号是否符合预期，可以查看生成文件名，例如：

```bash
ls dist/
```

## 4. 推荐发布方式：GitHub Actions 自动发布

仓库已包含自动发布工作流：

- 构建触发条件：推送 `v*` tag
- 工作流文件：`.github/workflows/publish.yml`
- 发布凭证：GitHub Secret `PYPI_API_TOKEN`

推荐流程如下。

### 4.1 确保代码已提交

```bash
git status
git push origin main
```

如果默认分支不是 `main`，请替换成实际分支名。

### 4.2 创建并推送版本 tag

以发布 `0.1.0` 为例：

```bash
git tag v0.1.0
git push origin v0.1.0
```

推送后，GitHub Actions 会自动执行以下步骤：

1. 检出代码并拉取 tag。
2. 安装 `build` 和 `twine`。
3. 清理旧的构建产物。
4. 执行 `python -m build`。
5. 执行 `python -m twine check dist/*`。
6. 使用 `PYPI_API_TOKEN` 上传到 PyPI。

### 4.3 查看发布结果

在 GitHub 仓库的 `Actions` 页面查看 `Publish Python Package` 工作流是否成功。

成功后，可以在 PyPI 页面验证新版本是否已上线。

## 5. 手动发布方式

如果你暂时不想通过 GitHub Actions，也可以在本地手动上传。

仍然建议先打 tag，让本地构建出的版本与仓库历史保持一致：

```bash
git tag v0.1.0
```

然后执行：

```bash
rm -rf build dist src/*.egg-info
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

上传时如果使用 API Token，用户名填写：

```text
__token__
```

密码填写你的 PyPI API Token。

如果你已经配置了 `~/.pypirc`，也可以直接复用已有配置。

## 6. 可选：先发布到 TestPyPI 验证

如果是首次发布，或者你刚调整过打包配置，建议先走一遍 TestPyPI。

```bash
rm -rf build dist src/*.egg-info
python -m build
python -m twine check dist/*
python -m twine upload --repository testpypi dist/*
```

安装验证示例：

```bash
pip install -i https://test.pypi.org/simple/ runninghub-sdk
```

如果项目依赖无法从 TestPyPI 完整解析，可以补充官方 PyPI 源：

```bash
pip install \
  -i https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  runninghub-sdk
```

## 7. 常见问题

### 7.1 版本号不对

常见原因：

- 没有打 tag。
- tag 格式不是 `v1.2.3`。
- 本地仓库 tag 没有拉全。

可先执行：

```bash
git fetch --tags
git describe --tags --always
```

### 7.2 PyPI 拒绝上传已存在版本

PyPI 不允许覆盖同版本文件。如果 `0.1.0` 已经上传，就必须发布新版本，例如 `0.1.1`。

### 7.3 构建结果里带有异常本地版本后缀

本项目已经通过 `local_scheme = "no-local-version"` 规避这类问题。如果仍然出现异常版本，先清理旧产物后重新构建：

```bash
rm -rf build dist src/*.egg-info
python -m build
```

### 7.4 GitHub Actions 发布失败

重点检查：

- `PYPI_API_TOKEN` 是否存在且有效。
- 触发的 ref 是否为 `refs/tags/v*`。
- 构建产物是否通过 `twine check`。

## 8. 推荐发布清单

每次发布前，按这个顺序检查：

1. 代码已经合并并推送。
2. `README.md` 和示例代码处于可发布状态。
3. 本地执行过 `python -m build` 和 `python -m twine check dist/*`。
4. 确认目标版本号未在 PyPI 上发布。
5. 创建并推送 `v*` tag。
6. 到 GitHub Actions 查看发布结果。

如果团队采用自动发布，建议只保留 GitHub Actions 作为正式发布入口，本地手动上传仅作为应急方案。