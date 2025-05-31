# 比特币区块高度监控与铸造自动化工具

这是一个由两个主要组件组成的 Python 工具：
1. 区块高度监控程序 (`mempool_monitor.py`)
2. 铸造自动化程序 (`mint_automation.py`)

**重要安全提示：请务必使用一个全新的、专门用于铸造的矿工钱包私钥，切勿使用您存放大量资产的钱包私钥。**

## 功能特性

### 区块监控程序 (`mempool_monitor.py`)
- 监控比特币区块高度，可设定目标区块
- 达到目标区块时，发送邮件通知（需配置）
- 达到目标区块时，播放自定义提示音（需提供 `.wav` 文件）
- 可随时通过 Ctrl+C 安全停止监控程序

### 铸造自动化程序 (`mint_automation.py`)
- 使用 Selenium 自动化填写网页上的私钥、Gas 费率和接收地址
- 自动化点击网页上的"查询矿工钱包可Mint数量"和"开始铸造"按钮
- 支持通过配置文件管理敏感信息

## 先决条件

在运行此工具之前，请确保您的系统已安装以下软件：

- Python 3.6 或更高版本
- pip (Python 包安装工具)
- Git (用于克隆仓库)
- Google Chrome 浏览器 (或与您的 Selenium WebDriver 兼容的其他浏览器)
- 对应您的浏览器的 WebDriver (例如 ChromeDriver)。请确保 WebDriver 的可执行文件在您的系统 PATH 中，或者您可以修改代码指定其路径。

## 设置步骤

1.  **克隆仓库:**

    ```bash
    git clone <您的仓库地址>
    cd <您的仓库文件夹名称>
    ```

2.  **安装 Python 依赖:**

   ```bash
   pip install -r requirements.txt
   ```

3.  **安装和配置 WebDriver:**
    -   下载对应您浏览器版本的 WebDriver（例如 ChromeDriver: [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)）。
    -   将下载的 WebDriver 可执行文件放置在系统 PATH 中，或者记下其完整路径，稍后在 `mint_automation.py` 文件中修改 `webdriver.Chrome()` 的调用，指定 `executable_path` 参数。

4.  **配置敏感信息:**
    -   在项目根目录创建一个名为 `config.env` 的文件（如果还没有的话）。
    -   由于 `config.env` 已被 `.gitignore` 忽略，您可以安全地在此文件中存放敏感配置。
    -   复制以下内容到 `config.env` 文件中，并根据您的实际情况填写对应的值：

    ```env
    # 目标区块高度：程序将监控并在此区块或之后执行自动化操作
    TARGET_BLOCK_HEIGHT=899999 # 替换为您想要监控的目标区块高度

    # 邮件通知配置 (可选，如果不需要邮件通知可不配置或留空)
    SMTP_SERVER=smtp.qq.com # 您的 SMTP 服务器地址
    SMTP_PORT=587         # 您的 SMTP 服务器端口
    SENDER_EMAIL=your_email@example.com # 发送邮件的邮箱地址
    RECEIVER_EMAIL=your_email@example.com # 接收邮件的邮箱地址
    SMTP_PASSWORD=your_email_password # 发送邮件邮箱的授权码或密码

    # 铸造收货地址：自动化程序将填写的接收铸造资产的地址
    RECEIVE_ADDRESS=your_receive_address # 替换为您的比特币接收地址

    # Gas 费率：自动化程序将填写的 Gas 费率 (sat/vB)
    GAS_FEE_RATE=3 # 替换为您想要的 Gas 费率

    # 矿工钱包私钥：用于在网页上签名的私钥 (请务必使用专用新钱包的私钥！)
    MINTER_PRIVATE_KEY=your_miner_private_key # 替换为您的矿工钱包 WIF 私钥
    ```

5.  **添加自定义提示音 (可选):**
    -   如果您想使用自定义声音提醒，请准备一个 `.wav` 格式的音频文件。
    -   将该文件重命名为 `mempo.wav` 并放置在项目根目录。

## 如何运行

### 运行区块监控程序

运行 `mempool_monitor.py` 来开始区块高度监控：

   ```bash
   python mempool_monitor.py
   ```

程序将开始监控区块高度，并在终端输出当前高度和距离目标的区块数。一旦达到或超过 `TARGET_BLOCK_HEIGHT`，程序将播放提示音并发送邮件通知（如果已配置）。

您可以在程序运行时随时按下 `Ctrl + C` 来安全地停止监控。

### 运行铸造自动化程序

运行 `mint_automation.py` 来执行自动化铸造操作：

```bash
python mint_automation.py
```

程序将启动浏览器，自动执行填写信息和点击按钮的步骤。自动化完成后，浏览器将关闭（除非在测试模式下运行）。

### 测试自动化步骤

如果您只想测试网页自动化部分是否正常工作，可以使用 `test_mint_automation_steps.py` 脚本：

   ```bash
python test_mint_automation_steps.py
```

这个脚本会直接执行 `mint_automation.py` 中的自动化步骤，并且为了方便您观察和调试，执行完毕后浏览器将**保持开启**。您需要手动关闭浏览器窗口。

## 注意事项

-   **安全性是关键：** 再次强调，请绝对不要在 `config.env` 中使用您主要资产钱包的私钥。创建一个新的、专用于此目的的钱包。
-   **网页结构变化：** Selenium 脚本依赖于网页的 HTML 结构（通过元素的 ID 来定位）。如果目标网页的结构发生变化，您可能需要更新 `mint_automation.py` 文件中的元素定位器。
    -   您可以使用浏览器的开发者工具 (通常按 F12) 来检查网页元素的 ID 或其他属性，以便更新代码。
-   **网络和加载时间：** 自动化脚本中包含了一些 `time.sleep()` 和显式等待。如果您的网络较慢或网站加载时间较长，可能需要调整等待时间或添加更多的显式等待。
-   **模态框和弹窗：** 自动化脚本包含了处理"确认铸造"模态框的逻辑。如果网站有其他 unexpected 的弹窗或交互，可能需要修改脚本来处理。
-   **错误处理：** 脚本包含基本的错误处理，但您可以根据需要增加更详细的错误日志和处理逻辑。

希望这份 README 对您和其他使用者有所帮助！如果您在使用过程中遇到任何问题，可以根据错误信息和日志输出进行排查。 