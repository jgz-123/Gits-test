# GITS C++ 在线体验

体验完整流程：**首次缺依赖编译失败 → gis update 补齐依赖 → 编译运行成功**。

[![在 Codespaces 中打开](https://github.com/codespaces/badge.svg)](https://codespaces.new/jgz-123/Gits-test)

## 1. 创建环境

登录 GitHub，点击上方按钮，再点击 Create codespace。等待初始化完成后，选择 Terminal → New Terminal。终端默认位于 `.playground/project`，C++ 编译器、CMake 和 gis 已准备好。

## 2. 先编译，体验缺少依赖

逐条输入并按 Enter：

```bash
cmake -S . -B build
cmake --build build
```

第一条应成功，第二条应报 **缺少 demo_math.hpp**。这是预期的缺依赖状态。

## 3. 用 gits 补齐依赖

```bash
gis status --lean -m setup.manifest
gis update --lean -m setup.manifest --no-obj
```

首次状态为 `1 missing packages`；更新会下载 demo-math，并将头文件复制到 `workspace/include/`。

## 4. 再次编译、运行

```bash
cmake --build build
./build/delivery_smoke
```

输出应为 **2 + 3 = 5**。完整验证命令：

```bash
python "$GITS_PLAYGROUND_ROOT/playground/verify.py" --build
```

最后显示 `PASS: built and ran C++ example: 2 + 3 = 5` 即通过。再次 update 应下载 0 个包。

## 更新已有环境

在终端执行 `git pull --ff-only`，再按 Ctrl + Shift + P，选择 Codespaces: Rebuild Container。完成后新建终端。新示例使用 demo-math，旧文本测试包无需清理。

如果已经下载过 demo-math，构建会直接成功。可以运行以下命令，在独立临时工作区重新验证完整的缺依赖流程：

```bash
python "$GITS_PLAYGROUND_ROOT/playground/test_demo.py"
```

[完整说明、示例修改方法和本地运行步骤](playground/README.md)

## 范围

此示例运行真实的 gits 源码和 C++ 编译器，SSH/SFTP 由本地文件适配器代替。依赖包包含跨平台 C++ 头文件，不需要生产服务器账号。所有生成内容位于 `.playground/`。

Codespaces 使用 GitHub 账号的云端额度。测试结束可在 [Codespaces 列表](https://github.com/codespaces)中停止环境。
