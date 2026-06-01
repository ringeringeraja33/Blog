# Godot 新手操作指南：按 Unity 经验对照理解

适用版本：Godot 4.6 正式分支。2026-06-01 查到的官方最新正式版是 4.6.3-stable，4.7 仍属于 beta。新项目建议使用正式版，避免教程、插件、导出模板和实际编辑器行为对不上。

本文写给已经摸过 Unity 的人。内容重点放在 Unity 常用判断到 Godot 的迁移：场景怎么拆、对象怎么组织、脚本挂在哪、输入怎么配、资源怎么做、最后怎么导出。

---

## 1. Unity 经验速查表

| Unity 里的概念 | Godot 里的近似概念 | 实际使用差异 |
|---|---|---|
| GameObject | Node | Godot 的 Node 自带明确职责，例如 `Sprite2D`、`Camera2D`、`CharacterBody2D`。很多时候先选合适节点，再加脚本扩展。 |
| Component | Node / Script | Unity 常把行为拆成组件挂到同一对象上；Godot 常把功能拆成子节点，也可以给节点挂脚本。 |
| Scene | Scene (`.tscn`) | Godot 的 Scene 既能表示关卡，也能表示角色、子弹、UI 面板、道具。它同时承担了一部分 Unity Scene 和 Prefab 的工作。 |
| Prefab | PackedScene / Scene instance | 保存为 `.tscn` 后，可以像 Prefab 一样实例化到其他 Scene 里。 |
| Transform | Node2D / Node3D transform | 2D 与 3D 节点体系分开，`Node2D` 管 2D，`Node3D` 管 3D。 |
| MonoBehaviour | Script attached to Node | GDScript 或 C# 脚本挂在节点上，生命周期由节点进入场景树后触发。 |
| Start | `_ready()` | 节点和子节点进入场景树后调用，常做引用缓存、初始化 UI、注册信号。 |
| Update | `_process(delta)` | 每帧调用，适合视觉更新、计时、普通逻辑。 |
| FixedUpdate | `_physics_process(delta)` | 固定物理帧调用，适合移动、碰撞、物理判断。 |
| Inspector serialized field | `@export var` | `@export` 变量会显示在 Inspector，适合调参。 |
| Input Manager / Input System action | Input Map action | 在 `Project > Project Settings > Input Map` 配动作名，再用代码读取。 |
| Event / UnityEvent / C# event | Signal | Godot 节点之间常用信号通信，按钮点击、碰撞进入、自定义事件都走这套。 |
| ScriptableObject | Resource | Godot 的 `Resource` 适合做配置、道具数据、技能数据、关卡参数。 |
| Tag | Groups | 节点可加入 Group，代码可按组查找或批量调用。 |
| LayerMask | Collision Layer / Mask | 物理对象有 Layer 和 Mask，Layer 表示自己在哪层，Mask 表示检测哪些层。 |
| Animator | AnimationPlayer / AnimationTree | `AnimationPlayer` 能动画化属性、调用方法；复杂状态机用 `AnimationTree`。 |
| Canvas / UI Toolkit | Control 节点体系 | UI 用 `Control` 及其子类，靠 Anchor、Container、Theme 管布局与样式。 |
| Build Settings | Export Presets | `Project > Export` 创建平台预设，需要先装对应版本的 Export Templates。 |
| Package Manager / Asset Store | AssetLib / Addons | Godot 插件通常放在 `addons/`，可从 AssetLib 或 GitHub 获取。 |

---

## 2. 先建立正确的 Godot 工作模型

Godot 项目由很多 Scene 组成。每个 Scene 是一棵 Node 树。游戏运行时，主 Scene 被加载进 SceneTree，随后你可以继续实例化角色、子弹、UI、特效等 Scene。

Unity 常见思路是“创建 GameObject，再给它堆组件”。Godot 常见思路是“选择一个有明确职责的节点作为根，再把其他职责拆成子节点”。例如一个 2D 玩家角色可以这样组织：

```text
Player (CharacterBody2D)
├── Sprite2D
├── CollisionShape2D
├── Camera2D
├── HurtBox (Area2D)
└── FootstepAudio (AudioStreamPlayer2D)
```

这里 `Player` 负责移动和角色状态，`Sprite2D` 负责显示，`CollisionShape2D` 负责碰撞形状，`Area2D` 负责检测受击范围。整棵树能直接看出职责分工。

新手最容易卡的点是 Scene 的粒度。建议按下面的标准拆：

| 要表达的内容 | 建议做法 |
|---|---|
| 一个完整关卡 | 一个 Scene，例如 `level_01.tscn` |
| 一个可复用角色 | 一个 Scene，例如 `player.tscn`、`slime.tscn` |
| 一个投射物或特效 | 一个 Scene，例如 `bullet.tscn`、`hit_fx.tscn` |
| 一个 UI 面板 | 一个 Scene，例如 `pause_menu.tscn`、`inventory_panel.tscn` |
| 一组静态配置 | Resource，例如 `weapon_data.tres` |

---

## 3. 下载、创建项目、选择版本

### 3.1 选哪个 Godot 包

Godot 下载页通常有两个主要版本：

| 下载项 | 适合谁 |
|---|---|
| Standard | 使用 GDScript 或 GDExtension，体积小，启动快，新手优先选它。 |
| .NET | 想用 C# 写脚本的人选它，需要本机有 .NET SDK。 |

如果你只是想快速理解 Godot，用 Standard + GDScript。你已有大量 C# 经验，可以选 .NET 版，但仍建议先把 Scene、Node、Signal 这套用 GDScript 跑一遍。

### 3.2 创建项目

1. 打开 Godot，进入 Project Manager。
2. 点击 `New Project`。
3. 填项目名和路径。
4. Renderer 选择：
   - `Forward+`：桌面端 3D、较高画质。
   - `Mobile`：移动端、性能优先。
   - `Compatibility`：老设备、Web 或兼容性优先。
5. 勾选 Git 元数据生成，Godot 会创建基础 `.gitignore` 和 `.gitattributes`。
6. 点击 Create & Edit。

### 3.3 推荐项目目录

```text
res://
├── scenes/
│   ├── levels/
│   ├── characters/
│   ├── ui/
│   └── fx/
├── scripts/
├── resources/
│   ├── configs/
│   ├── items/
│   └── skills/
├── art/
├── audio/
├── shaders/
└── addons/
```

Godot 里 `res://` 表示项目根目录。保存、加载项目资源时经常看到它。

---

## 4. 编辑器界面怎么对照 Unity 看

| Godot 区域 | Unity 近似区域 | 用途 |
|---|---|---|
| Scene Dock | Hierarchy | 当前 Scene 的 Node 树。 |
| FileSystem Dock | Project | 项目文件，所有资源都从这里进。 |
| Inspector | Inspector | 查看与编辑选中节点或资源的属性。 |
| Viewport | Scene View / Game View | 编辑 2D、3D、UI。 |
| Script Editor | IDE / 内置脚本编辑器 | 写 GDScript、看类文档、设断点。 |
| Output / Debugger | Console / Profiler | 日志、错误、调试、性能数据。 |
| Animation Panel | Animation Window | 编辑动画轨道、关键帧、方法调用。 |
| AssetLib | Asset Store 的轻量版 | 搜索插件和示例资源。 |

顶部常用入口：

| 菜单 | 常用功能 |
|---|---|
| `Project > Project Settings` | 项目设置、输入映射、自动加载、渲染、窗口尺寸。 |
| `Project > Export` | 创建导出平台预设，打包游戏。 |
| `Scene > New Scene` | 新建当前 Scene。 |
| `Debug` | 调试选项、可见碰撞形状、性能监视。 |
| `Editor > Editor Settings` | 编辑器外观、快捷键、外部编辑器配置。 |

---

## 5. 你的第一个 Scene

这一步对应 Unity 里“新建场景，放一个对象，运行看看”。

### 5.1 新建 UI Hello World

1. 左侧 Scene Dock 里点击 `User Interface`，Godot 会创建一个 `Control` 根节点。
2. 选中根节点，按 `Ctrl + A` 或点击 `Add Child Node`。
3. 搜索 `Label`，创建。
4. 选中 `Label`，在 Inspector 里找到 `Text`，填 `Hello Godot`。
5. 按 `Ctrl + S` 保存为 `res://scenes/ui/hello.tscn`。
6. 点击右上角 Run Current Scene，或按 `F6`。

### 5.2 设置主 Scene

1. 点击右上角 Run Project，或按 `F5`。
2. 第一次运行会提示选择 Main Scene。
3. 选择刚保存的 `hello.tscn`。
4. 之后按 `F5` 就会从这个 Scene 启动。

Unity 里 Build Settings 会记录启动场景列表；Godot 项目的主 Scene 记录在 `project.godot` 里，也可以在 `Project Settings > Application > Run > Main Scene` 改。

---

## 6. Node 和 Scene 的实际用法

### 6.1 选根节点

| 目标 | 常用根节点 |
|---|---|
| 2D 角色 | `CharacterBody2D` |
| 2D 静态物体 | `StaticBody2D` 或 `Node2D` |
| 2D 触发区域 | `Area2D` |
| 3D 角色 | `CharacterBody3D` |
| 3D 静态物体 | `StaticBody3D` 或 `Node3D` |
| UI 面板 | `Control` |
| 纯逻辑管理器 | `Node` |

如果根节点选错了，不一定要重做。右键节点可以 `Change Type`。不过根节点职责会影响整个 Scene 的理解成本，开始时多花十秒选对更划算。

### 6.2 实例化 Scene

保存后的 Scene 可以拖进另一个 Scene，也可以代码生成。

```gdscript
@export var bullet_scene: PackedScene

func shoot() -> void:
    var bullet = bullet_scene.instantiate()
    bullet.global_position = global_position
    get_tree().current_scene.add_child(bullet)
```

Unity 对照：这相当于 `Instantiate(prefab)`。差异在于 Godot 的 Scene 语义更宽，角色、UI、子弹、关卡块都可以是 Scene。

### 6.3 节点引用

常见写法：

```gdscript
@onready var sprite: Sprite2D = $Sprite2D
@onready var hurt_box: Area2D = $HurtBox
```

`$Sprite2D` 是 `get_node("Sprite2D")` 的简写。`@onready` 表示等节点进入场景树后再取引用，适合引用子节点。

如果节点路径改名会影响代码。常变动的节点可以用导出变量手动拖引用：

```gdscript
@export var target: Node2D
```

---

## 7. 脚本：GDScript 和 C# 怎么选

Godot 官方主要支持 GDScript 和 C#。GDScript 是为 Godot 定制的语言，语法接近 Python，运行时和生态都属于 Godot 自己。它和编辑器、文档、节点 API 的贴合度最高。

| 选择 | 优点 | 注意 |
|---|---|---|
| GDScript | 上手快，示例多，编辑器集成好，适合做玩法原型和中小型项目。 | 语法和 C# 不同，需要适应缩进、动态类型与可选静态类型。 |
| C# | Unity 开发者迁移成本低，工程化工具链成熟。 | 需要 .NET 版 Godot；部分平台支持和导出流程要额外确认。 |
| C++ / GDExtension | 适合性能热点、引擎扩展、接第三方库。 | 新手阶段少碰，先把玩法做起来。 |

### 7.1 生命周期对照

| Unity | Godot | 说明 |
|---|---|---|
| `Awake()` | `_enter_tree()` / `_init()` | 更早的初始化点。新手常用得少。 |
| `Start()` | `_ready()` | 节点和子节点准备好后执行。 |
| `Update()` | `_process(delta)` | 每帧逻辑。 |
| `FixedUpdate()` | `_physics_process(delta)` | 物理帧逻辑。 |
| `OnEnable()` | `_enter_tree()` | 节点进入场景树。 |
| `OnDisable()` | `_exit_tree()` | 节点离开场景树。 |
| `OnCollisionEnter` | body/area 相关信号 | 通过物理节点和信号处理。 |
| `OnGUI` | Control 节点 | UI 直接用节点树和主题系统做。 |

### 7.2 最小脚本示例

给 `CharacterBody2D` 挂一个脚本：

```gdscript
extends CharacterBody2D

@export var speed: float = 220.0

func _physics_process(delta: float) -> void:
    var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
    velocity = direction * speed
    move_and_slide()
```

配套操作：

1. 打开 `Project > Project Settings > Input Map`。
2. 添加 `move_left`、`move_right`、`move_up`、`move_down`。
3. 分别绑定 A/D/W/S 或方向键。
4. 角色根节点使用 `CharacterBody2D`，并添加 `CollisionShape2D`。

`move_and_slide()` 使用节点的 `velocity` 移动角色，并处理碰撞滑动。它是 Godot 角色移动的常用入口。

### 7.3 Inspector 可调参数

```gdscript
@export var max_hp: int = 100
@export var move_speed: float = 5.5
@export var display_name: String = "Player"
@export var weapon_data: Resource
```

`@export` 对 Unity 开发者最像 `[SerializeField] public/private field`。它让策划、美术、关卡编辑人员能直接在 Inspector 改参数。

---

## 8. 输入系统

Godot 推荐先定义动作名，再在代码里读动作。这样键盘、手柄、触屏映射可以统一处理。

### 8.1 配置入口

路径：`Project > Project Settings > Input Map`

常见动作命名：

```text
move_left
move_right
move_up
move_down
jump
attack
interact
pause
```

### 8.2 代码读取

```gdscript
func _process(delta: float) -> void:
    if Input.is_action_just_pressed("attack"):
        attack()

    if Input.is_action_pressed("interact"):
        try_interact()
```

```gdscript
var axis := Input.get_axis("move_left", "move_right")
var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
```

Unity 对照：这更接近 Unity 新 Input System 的 Action 名，代码里不需要到处判断具体按键。

---

## 9. 信号：Godot 里最常用的解耦方式

Signal 是 Godot 的事件机制。按钮按下、计时结束、Area 检测进入、动画结束，都可以通过信号通知其他节点。

### 9.1 编辑器里连接信号

1. 选中一个 Button。
2. Inspector 旁边切到 `Node` 面板。
3. 找到 `pressed()` 信号。
4. 双击，选择接收脚本的节点。
5. Godot 会生成回调函数。

生成示例：

```gdscript
func _on_start_button_pressed() -> void:
    start_game()
```

### 9.2 自定义信号

```gdscript
extends Node

signal hp_changed(current: int, max_value: int)

var hp := 100
var max_hp := 100

func take_damage(amount: int) -> void:
    hp = max(hp - amount, 0)
    hp_changed.emit(hp, max_hp)
```

UI 脚本连接它：

```gdscript
func bind_player(player: Node) -> void:
    player.hp_changed.connect(_on_player_hp_changed)

func _on_player_hp_changed(current: int, max_value: int) -> void:
    $HpBar.value = float(current) / max_value
```

Unity 对照：它像 C# event、UnityEvent、委托回调的组合。Godot 项目里，信号很常见，尤其适合 UI、角色状态、交互、刷怪、关卡事件。

---

## 10. 物理、碰撞、检测

Godot 的 2D 和 3D 物理节点分开。2D 节点名通常带 `2D`，3D 节点名通常带 `3D`。

| 用途 | 2D 节点 | 3D 节点 |
|---|---|---|
| 可控角色 | `CharacterBody2D` | `CharacterBody3D` |
| 刚体 | `RigidBody2D` | `RigidBody3D` |
| 静态碰撞 | `StaticBody2D` | `StaticBody3D` |
| 触发检测 | `Area2D` | `Area3D` |
| 碰撞形状 | `CollisionShape2D` | `CollisionShape3D` |
| 射线检测 | `RayCast2D` | `RayCast3D` |

### 10.1 Layer 和 Mask

每个物理对象通常有两组设置：

| 设置 | 含义 |
|---|---|
| Collision Layer | 自己属于哪些层。 |
| Collision Mask | 自己会检测哪些层。 |

例子：玩家 Layer 是 `Player`，敌人攻击 Area 的 Mask 勾 `Player`，这样敌人攻击检测只关心玩家。

### 10.2 Area 用法

`Area2D` / `Area3D` 常用于：

- 捡道具。
- 交互范围。
- 受击盒和攻击盒。
- 进入区域触发剧情。
- 传送点。

连接 `body_entered` 或 `area_entered` 信号即可处理进入事件。

---

## 11. Resource：Godot 里的数据资产

如果你在 Unity 里用 ScriptableObject 管道具、技能、怪物配置，Godot 对应思路是 Resource。

### 11.1 自定义 Resource

```gdscript
extends Resource
class_name WeaponData

@export var id: StringName
@export var display_name: String
@export var damage: int = 10
@export var cooldown: float = 0.3
@export var icon: Texture2D
```

创建后可保存为：

```text
res://resources/items/sword_basic.tres
```

角色脚本里引用：

```gdscript
@export var weapon: WeaponData

func attack() -> void:
    print("%s deals %s damage" % [weapon.display_name, weapon.damage])
```

### 11.2 Resource 适合放什么

| 数据类型 | 适合程度 |
|---|---|
| 武器配置 | 很适合 |
| 技能配置 | 很适合 |
| 怪物数值 | 很适合 |
| 关卡参数 | 很适合 |
| 运行时全局状态 | 一般，常用 Autoload 管 |
| 大表格数据 | 可行；如果已有 CSV/JSON 流程，可继续用导入脚本转换 |

对于配置表项目，推荐把“策划表原始数据”和“Godot 可编辑 Resource”分层处理。原始表继续作为策划源，构建或导入时生成 `.tres`、`.res` 或 JSON，项目运行时读生成物。

---

## 12. Autoload：全局单例

Autoload 可以把某个脚本或 Scene 注册为全局访问对象。入口在 `Project > Project Settings > Globals > Autoload`。

常见用途：

| 单例 | 用途 |
|---|---|
| `GameState` | 当前存档、关卡进度、全局状态。 |
| `AudioManager` | 跨场景音乐、音效播放。 |
| `SceneLoader` | 切场景、异步加载、加载界面。 |
| `ConfigDB` | 加载策划配置、查询表数据。 |
| `EventBus` | 跨系统广播少量全局事件。 |

示例：

```gdscript
extends Node

var coins: int = 0

func add_coins(amount: int) -> void:
    coins += amount
```

注册名为 `GameState` 后，可在任意脚本中访问：

```gdscript
GameState.add_coins(10)
```

不要把所有逻辑都塞进 Autoload。它适合全局服务和跨场景状态，具体玩法逻辑仍放在对应 Scene 和节点脚本里。

---

## 13. UI：Control、Anchor、Container、Theme

Godot UI 全部基于 `Control` 节点。Unity 里你会关心 Canvas、RectTransform、LayoutGroup；Godot 里对应 Anchor、Size Flags、Container、Theme。

### 13.1 常用 UI 节点

| 节点 | 用途 |
|---|---|
| `Control` | UI 基类，适合作为面板根。 |
| `Label` | 文本。 |
| `Button` | 按钮。 |
| `TextureRect` | 图片显示。 |
| `Panel` / `PanelContainer` | 面板背景。 |
| `ProgressBar` | 血条、进度条。 |
| `HBoxContainer` / `VBoxContainer` | 横向、纵向自动布局。 |
| `GridContainer` | 网格布局。 |
| `MarginContainer` | 外边距。 |
| `ScrollContainer` | 滚动区域。 |

### 13.2 UI 布局习惯

1. 根节点用 `Control`。
2. 全屏 UI 先点 Layout，选择 `Full Rect`。
3. 面板内尽量用 Container 管布局，少手摆坐标。
4. 字体、颜色、按钮样式放到 Theme，避免每个控件单独调。
5. 用信号处理按钮点击，不要在 `_process` 里轮询按钮状态。

---

## 14. 动画与 Timeline 思维

Godot 的 `AnimationPlayer` 可以动画化节点属性，也可以在时间轴上调用方法。它不只做角色动作，也适合 UI 动效、门开关、镜头移动、机关事件。

| Unity | Godot |
|---|---|
| Animation Clip | AnimationPlayer 里的 Animation |
| Animator Controller | AnimationTree |
| Timeline 调方法 | AnimationPlayer 方法轨 |
| DOTween/Tween | Tween API |

常用组合：

- 简单 UI 动效：`Tween`。
- 角色帧动画：`AnimatedSprite2D` 或 `AnimationPlayer`。
- 角色状态混合：`AnimationTree`。
- 剧情机关：`AnimationPlayer` 动画属性和调用方法。

---

## 15. 音频

Godot 音频节点按空间类型拆：

| 节点 | 用途 |
|---|---|
| `AudioStreamPlayer` | 非空间音频，常用于 BGM、UI 音效。 |
| `AudioStreamPlayer2D` | 2D 空间音频。 |
| `AudioStreamPlayer3D` | 3D 空间音频。 |

音量、混响、压缩、分组混音走 Audio Bus。可以在底部 Audio 面板里管理，例如：

```text
Master
├── BGM
├── SFX
└── UI
```

游戏设置里的音乐、音效音量通常就是调对应 Bus 的音量。

---

## 16. 导入资源

把图片、音频、模型拖进项目目录后，Godot 会自动导入。选中资源后，Inspector 会显示 Import 设置。

常见导入设置：

| 资源 | 关注项 |
|---|---|
| 图片 | Filter、Repeat、Mipmaps、Texture Type |
| 像素图 | 关闭 Filter，避免发糊 |
| 音频 | Loop、压缩格式、导入质量 |
| 3D 模型 | 材质、动画、骨骼、碰撞生成 |
| 字体 | 动态字体、fallback、字号 |

Godot 4.1 以后建议 Git 忽略 `.godot/`，因为它主要存项目缓存数据。源资源、`.tscn`、`.gd`、`.tres`、`project.godot` 需要纳入版本控制。

---

## 17. 导出游戏

入口：`Project > Export`

### 17.1 基本步骤

1. 安装当前 Godot 版本对应的 Export Templates。
2. 打开 `Project > Export`。
3. 点击 `Add`，选择平台，例如 Windows、Linux、macOS、Android、Web。
4. 设置图标、包名、签名、架构等平台参数。
5. 点击 `Export Project`。

### 17.2 Unity 对照

| Unity Build | Godot Export |
|---|---|
| Build Settings 选平台 | Export Preset 选平台 |
| Player Settings | Project Settings + Export Preset |
| Addressables / AssetBundle | PCK / ZIP pack，可做补丁、DLC、Mod |
| Development Build | Debug export / Release export |

移动端和主机平台要额外确认 SDK、签名、商店要求。主机平台通常需要第三方移植服务或平台授权流程。

---

## 18. 插件、AssetLib、编辑器扩展

Godot 插件通常在项目的 `addons/` 目录里。启用路径：

```text
Project > Project Settings > Plugins
```

常见插件类型：

- 编辑器工具，例如对话编辑器、关卡工具、导入器。
- 运行时库，例如行为树、状态机、存档系统。
- 第三方 SDK 接入，例如 Steam、广告、统计。

AssetLib 可以直接从编辑器里浏览插件，但不少高质量插件也在 GitHub。引入插件前先看 Godot 版本兼容性，尤其是 4.5、4.6、4.7 beta 之间的差异。

---

## 19. 调试和性能查看

Godot 内置调试工具足够做日常开发：

| 工具 | 用途 |
|---|---|
| Output | 打印日志、错误、警告。 |
| Debugger | 断点、调用栈、变量查看。 |
| Remote Scene Tree | 运行时查看实际节点树。 |
| Profiler | 查看脚本、物理、渲染耗时。 |
| Monitors | FPS、内存、对象数量等指标。 |
| Visible Collision Shapes | 运行时显示碰撞形状。 |

常用排查顺序：

1. 看 Output 是否有红色错误。
2. 用 Remote Scene Tree 确认节点有没有生成、路径是否正确。
3. 打开 Visible Collision Shapes 看碰撞体位置。
4. 用断点确认信号是否触发。
5. 用 Profiler 找每帧耗时高的函数。

---

## 20. 新手练习路线

### 第 1 天：编辑器和 Scene

- 新建项目。
- 做一个 `main.tscn`。
- 放 `Label`、`Button`。
- 按按钮改变文字。
- 学会保存 Scene、设置 Main Scene、运行当前 Scene。

### 第 2 天：2D 角色

- 创建 `player.tscn`。
- 根节点用 `CharacterBody2D`。
- 加 `Sprite2D` 和 `CollisionShape2D`。
- 配 Input Map。
- 写移动脚本。

### 第 3 天：实例化

- 创建 `bullet.tscn`。
- 玩家按攻击键生成子弹。
- 子弹移动并在离开屏幕后销毁。
- 理解 PackedScene、instantiate、add_child。

### 第 4 天：信号和 UI

- 创建 `hud.tscn`。
- 玩家定义 `hp_changed` 信号。
- HUD 监听玩家血量变化。
- 按钮控制暂停或重新开始。

### 第 5 天：配置数据

- 自定义 `WeaponData` Resource。
- 创建两把武器 `.tres`。
- 玩家脚本引用不同 WeaponData。
- 在 Inspector 切武器测试伤害和冷却。

### 第 6 天：导出

- 安装 Export Templates。
- 建 Windows 导出预设。
- 生成一次可执行文件。
- 检查窗口标题、图标、资源是否加载正常。

---

## 21. Unity 使用者容易误解的点

| 误区 | 建议 |
|---|---|
| 把所有行为都写在一个超大脚本里 | 用节点和 Scene 拆职责。角色、武器、UI、特效分开。 |
| 所有通信都用 `get_parent()` 找对象 | 优先用信号、导出引用、Group、Autoload。 |
| 把 Scene 只当关卡 | 角色、道具、UI、子弹都可以是 Scene。 |
| 把 Resource 当运行时状态容器 | Resource 更适合作为配置资产；运行时状态用节点或 Autoload 管。 |
| UI 全靠手动坐标 | 用 Container、Anchor、Theme。 |
| 一开始就全项目 C# | 先用 GDScript 跑通 Godot 工作流，再决定语言。 |
| 忽略导出模板版本 | Export Templates 必须匹配当前 Godot 版本。 |
| 不开可见碰撞形状 | 2D/3D 碰撞问题先看形状，别只看代码。 |

---

## 22. 建议记住的快捷键

| 快捷键 | 作用 |
|---|---|
| `F5` | 运行项目 Main Scene |
| `F6` | 运行当前 Scene |
| `F8` | 停止运行 |
| `Ctrl + S` | 保存当前 Scene |
| `Ctrl + Shift + S` | 保存全部 |
| `Ctrl + A` | 添加子节点，焦点在 Scene Dock 时常用 |
| `Ctrl + P` | 快速打开文件 |
| `Ctrl + Shift + F` | 全项目搜索 |

---

## 23. 继续学习时优先看哪些官方页

- Godot 下载归档：确认当前正式版本。
- Godot 4.6 官方文档首页：按正式分支查资料。
- Introduction to Godot：理解 Godot 能做什么。
- Overview of Godot's key concepts：Scene、Node、SceneTree、Signal。
- Nodes and Scenes：第一个 Scene 的官方入门。
- GDScript reference：语法和脚本能力。
- InputMap：输入动作配置和 API。
- Singletons Autoload：全局服务和跨场景状态。
- Exporting projects：导出项目。
- Version control systems：Git 忽略文件和 LFS 建议。

---

## 24. 一句话抓主线

Unity 经验可以帮你理解对象、生命周期、输入、物理、资源和导出；进入 Godot 后，先把 Scene、Node、Signal、Resource、Autoload 五个词用熟。能用这五个词描述清楚一个功能，Godot 项目的结构就不会乱。

---

## 参考来源

- Godot 4.6.3 stable 下载页：https://godotengine.org/download/archive/4.6.3-stable
- Godot 4.6.3 官方维护版公告：https://godotengine.org/article/maintenance-release-godot-4-6-3/
- Godot 4.6 官方文档首页：https://docs.godotengine.org/en/stable/
- Introduction to Godot：https://docs.godotengine.org/en/stable/getting_started/introduction/introduction_to_godot.html
- Overview of Godot's key concepts：https://docs.godotengine.org/en/stable/getting_started/introduction/key_concepts_overview.html
- Nodes and Scenes：https://docs.godotengine.org/en/stable/getting_started/step_by_step/nodes_and_scenes.html
- GDScript reference：https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_basics.html
- InputMap：https://docs.godotengine.org/en/stable/classes/class_inputmap.html
- Singletons Autoload：https://docs.godotengine.org/en/stable/tutorials/scripting/singletons_autoload.html
- Exporting projects：https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html
- Version control systems：https://docs.godotengine.org/en/stable/tutorials/best_practices/version_control_systems.html
