# GITS 在线体验

在浏览器终端里体验 gits：检查缺包、按清单下载、解压拍平、复制交付文件、复用缓存。

[![在 Codespaces 中打开](https://github.com/codespaces/badge.svg)](https://codespaces.new/jgz-123/Gits-test)

## 第 1 步：打开云端环境

1. 登录 GitHub，点击上方 **在 Codespaces 中打开** 按钮。
2. 页面上点击 **Create codespace**。首次创建需要等待环境自动准备；无需手动安装 gits。
3. 浏览器会打开类似 VS Code 的界面。等初始化完成后，选择顶部菜单 **Terminal → New Terminal**（终端 → 新建终端）。如果菜单折叠，先点击左上角的菜单按钮。
4. 下方出现终端后，从第 2 步开始，逐条复制命令，按 Enter 执行。终端的默认目录为 `.playground/project`。

Codespaces 是云端 Linux 开发环境，需要 GitHub 账号，使用受账号额度和计费设置限制。先使用默认机器即可。官方说明：[Codespaces 介绍](https://docs.github.com/en/codespaces/about-codespaces/what-are-codespaces)。

## 第 2 步：逐条执行这三条命令

**① 查看初始状态**

```bash
gis status --lean -m setup.manifest
```

首次执行应看到 `2 missing packages`，表示示例需要的两个包还没有下载。这是预期结果。

**② 下载并准备交付文件**

```bash
gis update --lean -m setup.manifest --no-obj
```

应看到 `Succeed packages num: 2`，然后执行 `demo-runtime` 和 `demo-assets` 的复制规则。

**③ 检查结果**

```bash
python "$GITS_PLAYGROUND_ROOT/playground/verify.py"
```

应看到 `0 missing packages`、两条 `copy ... OK!`，最后一行以 `PASS:` 开头。这就表示本次测试通过。

## 第 3 步：体验缓存与查看产物

再执行一次第 ② 条命令，应看到 `Total lean packages num: 0`，表示复用已下载的包。

查看清单和交付文件：

```bash
cat setup.manifest
find workspace -type f
cat workspace/runtime.txt
cat workspace/data/labels.txt
```

清单只有三行：

```text
[VS2019]
demo-runtime==1.0: copy bin/* to ./workspace/
demo-assets==1.0: copy data/* to ./workspace/data/
```

第一行是演示包的匹配标签；后两行声明包版本和复制规则。这里在 Linux 上验证文件交付，不执行 Windows SDK。

## 测试结束

打开 [你的 Codespaces 列表](https://github.com/codespaces)，找到该环境，点击右侧 `…` → **Stop codespace**。不再使用时可以删除该测试环境。

## 遇到问题

- `gis: command not found`：先确认初始化已完成，然后关闭终端并重新打开。可从仓库根目录重新执行 `bash .devcontainer/setup.sh`，完成后再新建终端。
- 提示找不到 manifest：执行 `cd "$GITS_PLAYGROUND_ROOT/.playground/project"` 后重试。
- 第一次就是 `0 missing packages`：你之前已更新过，缓存仍在，属于正常情况。新建一个 Codespace 可以从首次下载开始体验。
- 初始化失败：查看创建日志。需要手动重试时，从仓库根目录执行 `bash .devcontainer/setup.sh`；初始化依赖安装需要联网。

## 此演示的范围

此仓库是 GITS 的独立体验版本，包含真实 CLI 源码和两个自动生成的文本测试包。参数解析、清单解析、选包、版本匹配、解压、拍平、复制和状态检查执行真实逻辑；SSH/SFTP 通过本地文件适配器代替。无需团队服务器账号，不包含生产配置，不执行模型推理。

## 可选：Windows 本地运行

已有 Python 3.10 或更高版本时，在仓库根目录的 **PowerShell** 中逐行执行：

```powershell
python -m venv .playground/venv
& .playground/venv/Scripts/python.exe -m pip install -r playground/requirements.txt
& .playground/venv/Scripts/python.exe playground/bootstrap.py
& .playground/venv/Scripts/python.exe playground/run.py status --lean -m setup.manifest
& .playground/venv/Scripts/python.exe playground/run.py update --lean -m setup.manifest --no-obj
& .playground/venv/Scripts/python.exe playground/verify.py
```

本地方式不需要 GitHub Codespaces 或 Docker。全部演示文件生成在 `.playground` 中。
