# UE5 新手操作指南：按 Unity 经验对照理解

适用版本：Unreal Engine 5.7 正式文档线。2026-06-01 查询到 UE 5.8 仍是 Preview；新项目学习和团队落地建议先按 5.7 正式文档理解，5.8 Preview 适合单独开测试项目观察新功能。

本文写给已经摸过 Unity 的人。内容重点放在 Unity 常用工作流到 UE5 的迁移：对象怎么组织、关卡怎么拆、脚本写在哪、蓝图和 C++ 怎么分工、输入怎么配、资源怎么管理、最后怎么打包。

---

## 1. Unity 经验速查表

| Unity 里的概念 | UE5 里的近似概念 | 实际使用差异 |
|---|---|---|
| Unity Hub | Epic Games Launcher | 管理引擎安装、项目、Marketplace/Fab 资源。 |
| Project | `.uproject` 项目 | UE 项目由 `.uproject`、`Content/`、`Config/`、`Source/` 等目录组成。 |
| Scene | Level / Map (`.umap`) | UE 的关卡文件常叫 Level 或 Map。一个游戏可以有多个 `.umap`。 |
| GameObject | Actor | 能放进 Level 的对象通常是 Actor，例如灯光、相机、Static Mesh、角色、触发器。 |
| Component | Component | UE 也有组件，但分得更细：Actor Component、Scene Component、Primitive Component。 |
| Transform | Scene Component 的 Transform | Actor 的空间位置通常由 Root Component 或 Scene Component 管。 |
| Prefab | Blueprint Class / C++ Class | UE 常先做一个 Blueprint Class 或 C++ Class，再把实例放进关卡。 |
| MonoBehaviour | Blueprint Graph / C++ Actor class | 玩法逻辑可以写在蓝图，也可以写 C++，团队项目常混用。 |
| Awake | Constructor / Construction Script | Constructor 偏 C++ 默认对象构造；Construction Script 在编辑器放置或属性变化时执行。 |
| Start | BeginPlay | 游戏开始或对象生成后进入玩法逻辑的常用入口。 |
| Update | Tick | 每帧执行；UE 里要谨慎开 Tick，能用事件就少 Tick。 |
| FixedUpdate | Physics Substep / Movement Component | UE 没有完全一一对应的 `FixedUpdate`，角色移动通常交给 Movement Component。 |
| Rigidbody | Physics simulation on Primitive Component | Static Mesh、Skeletal Mesh、Collider 类组件可开物理模拟。 |
| Collider | Collision Shape / Collision Preset | 碰撞由组件上的 Collision 设置、Object Type、Response 管。 |
| LayerMask | Object Channel / Trace Channel | UE 用 Collision Channel 和 Response 控制阻挡、重叠、忽略。 |
| Input Manager / Input System | Enhanced Input | UE5 推荐 Enhanced Input，用 Input Action 和 Mapping Context 管输入。 |
| ScriptableObject | Data Asset / Primary Data Asset | 道具、技能、怪物配置常用 Data Asset；大型资源加载可接 Asset Manager。 |
| Canvas / UI Toolkit | UMG / Widget Blueprint | UI 常用 UMG，界面资产是 Widget Blueprint。 |
| Animator | Animation Blueprint / Montage / State Machine | 角色动画逻辑常放 Animation Blueprint，攻击等片段常用 Montage。 |
| Particle System / VFX Graph | Niagara | UE5 主力特效系统，系统、发射器、模块、参数分层。 |
| Shader Graph | Material Editor | UE 材质是节点图，常用 Material Instance 暴露参数给美术调。 |
| NavMesh | NavMesh Bounds Volume | 放 NavMesh Bounds Volume 后构建导航，AI MoveTo 可用。 |
| Addressables / AssetBundle | Asset Manager / Pak / IoStore | 资源打包、加载和热更新体系更底层，项目早期先理解软引用和 Primary Asset。 |
| Build Settings | Platforms / Package Project | `Platforms` 菜单和 Project Settings 控制平台、Cook、Package、Deploy。 |
| Package Manager | Plugins / Fab | 插件在 `Edit > Plugins` 管理，资源从 Fab 或 Marketplace 引入。 |

---

## 2. 先建立 UE5 的工作模型

Unity 常见思路是：GameObject 放在 Scene 里，GameObject 上挂 Component，Component 里写逻辑。

UE5 的常见思路可以这样看：

```text
Project
├── Level / Map (.umap)
│   ├── Actor instance
│   ├── Actor instance
│   └── Actor instance
├── Blueprint Class / C++ Class
│   ├── Components
│   ├── Variables
│   └── Graph / C++ functions
└── Assets (.uasset)
```

真正做功能时，你会经常围绕这几个词思考：

| 词 | 用来回答的问题 |
|---|---|
| Actor | 这个东西要不要放进关卡，能不能被生成、移动、销毁。 |
| Component | 这个 Actor 由哪些部件组成，比如 Mesh、Camera、Collision、Audio。 |
| Blueprint Class | 这个对象能不能做成可复用类型，放很多实例到关卡里。 |
| Level / Map | 当前关卡里有哪些 Actor，它们初始摆在哪。 |
| GameMode | 这一关或这一种玩法规则是什么，默认玩家角色是谁。 |
| PlayerController | 玩家输入、相机、UI、控制权怎么处理。 |
| Pawn / Character | 玩家或 AI 在世界里的身体是什么。 |
| GameInstance | 跨关卡保留的数据和系统放哪里。 |
| Data Asset | 配置数据、道具数据、技能数据怎么做成资源。 |

一个典型第三人称角色 Blueprint 可以这样组织：

```text
BP_PlayerCharacter (Character)
├── CapsuleComponent
├── ArrowComponent
├── Mesh (SkeletalMeshComponent)
├── CameraBoom (SpringArmComponent)
├── FollowCamera (CameraComponent)
└── CharacterMovementComponent
```

`Character` 自带胶囊体、角色移动、跳跃、落地等基础能力。Unity 里你可能会自己组合 Rigidbody、Collider、Controller 脚本；UE 里第三人称、第一人称角色通常从 Character 开始。

---

## 3. 安装、创建项目、选择版本

### 3.1 安装入口

1. 安装 Epic Games Launcher。
2. 登录 Epic 账号。
3. 进入 Unreal Engine 页面。
4. 在 Library 里添加引擎版本。
5. 选择 UE 5.7 正式版本安装。

5.8 Preview 可以安装，但建议作为单独测试环境。项目一旦开始做内容，频繁升引擎版本会影响插件、蓝图、打包和团队同步。

### 3.2 创建项目

1. 打开 UE。
2. 在 Project Browser 里选择 `Games`。
3. 新手建议选 `Third Person` 或 `Blank`。
4. Blueprint / C++ 选择：
   - 只想快速理解编辑器和流程：选 Blueprint。
   - 已确定要写 C++：选 C++，也可以继续使用蓝图。
5. Target Platform 选择 Desktop 或 Mobile。
6. Quality Preset 选择 Maximum 或 Scalable。
7. Starter Content 按需要勾选。
8. 创建项目。

### 3.3 推荐目录

UE 里资源都在 `Content/` 下，团队项目要尽早定目录。

```text
Content/
├── _Game/
│   ├── Blueprints/
│   │   ├── Characters/
│   │   ├── Gameplay/
│   │   ├── UI/
│   │   └── Props/
│   ├── Maps/
│   ├── Data/
│   ├── Materials/
│   ├── Meshes/
│   ├── Animations/
│   ├── Niagara/
│   ├── Audio/
│   └── UI/
└── ThirdParty/
```

建议项目自己的资源统一放 `_Game/`。外部插件、示例包、市场资源放到单独目录，后期清理引用会轻松很多。

---

## 4. 编辑器界面按 Unity 怎么看

| UE5 区域 | Unity 近似区域 | 用途 |
|---|---|---|
| Viewport | Scene View / Game View | 摆放对象、看场景、模拟运行。 |
| Outliner | Hierarchy | 当前 Level 里的 Actor 列表。 |
| Content Browser | Project | 项目资源管理，`.uasset`、`.umap` 都在这里。 |
| Details | Inspector | 查看和编辑选中 Actor、Component 或资产属性。 |
| Place Actors | GameObject 创建菜单 | 拖灯光、相机、基础模型、触发器、体积等到场景。 |
| World Settings | Scene 设置 | 当前 Level 的 GameMode 覆盖、World Partition 等。 |
| Output Log | Console | 日志、蓝图报错、C++ 警告、控制台命令。 |
| Blueprint Editor | Visual scripting editor | 编辑蓝图组件、变量、函数、事件图。 |
| Material Editor | Shader Graph | 编辑材质节点。 |
| UMG Designer | UI Builder | 编辑 Widget Blueprint。 |

顶部常用菜单：

| 菜单 | 常用功能 |
|---|---|
| `File` | 新建关卡、保存、打包相关入口。 |
| `Edit > Project Settings` | 输入、碰撞、渲染、平台、地图与模式等设置。 |
| `Edit > Plugins` | 启用和禁用插件。 |
| `Window` | 打开 Outliner、Content Browser、World Settings、Levels 等窗口。 |
| `Tools` | C++ 类、调试、审计等工具入口。 |
| `Platforms` | Cook、Package、Launch、平台 SDK 状态。 |

---

## 5. 第一个可运行项目

### 5.1 用 Third Person 模板快速跑起来

1. 创建 Third Person Blueprint 项目。
2. 打开默认地图。
3. 点击顶部 `Play`。
4. 用 WASD 移动，鼠标控制视角，空格跳跃。
5. 选中场景里的 `BP_ThirdPersonCharacter` 或在 Content Browser 找到它。
6. 双击打开 Blueprint，查看 Components 和 Event Graph。

这一步的目标是看清楚：角色在 UE 里通常会做成一个 Blueprint Class，里面有组件树、变量和事件图。

### 5.2 新建自己的 Level

1. `File > New Level`。
2. 选择 Basic 或 Empty。
3. 保存到 `Content/_Game/Maps/L_Test.umap`。
4. 打开 `Edit > Project Settings > Maps & Modes`。
5. 把 Editor Startup Map 和 Game Default Map 指到你的地图。

Unity 里常在 Build Settings 里指定场景。UE 里默认地图在 Maps & Modes 里配。

---

## 6. Actor、Component、Blueprint Class

### 6.1 Actor 是什么

Actor 是能放进 Level 的对象。灯光、相机、触发器、Static Mesh、角色都属于 Actor 或 Actor 子类。

常见 Actor：

| Actor | 用途 |
|---|---|
| `StaticMeshActor` | 场景静态模型，例如石头、墙、箱子。 |
| `SkeletalMeshActor` | 骨骼模型展示。 |
| `CameraActor` | 镜头。 |
| `PointLight` / `DirectionalLight` | 灯光。 |
| `TriggerBox` | 触发区域。 |
| `Character` | 适合人形或站立角色。 |
| `Pawn` | 可被玩家或 AI 控制的身体，适合载具、棋子、飞船等。 |

### 6.2 Component 的三类常见形态

| 类型 | 是否有 Transform | 用途 |
|---|---|---|
| Actor Component | 没有 | 纯逻辑能力，例如血量、背包、属性、任务。 |
| Scene Component | 有 | 有位置但不直接渲染，例如挂点、Spring Arm、音频位置。 |
| Primitive Component | 有 | 能渲染或参与碰撞，例如 Static Mesh、Skeletal Mesh、Box Collision。 |

Unity 里常用父子 GameObject 拆部件；UE 里一个 Actor 内部常用 Component 层级表达。需要真正独立生成、独立复制、独立生命周期时，再考虑多个 Actor。

### 6.3 Blueprint Class 近似 Prefab

Blueprint Class 可以理解成“可复用对象类型”。你编辑 `BP_Door`，关卡里所有 `BP_Door` 实例都会跟着更新。

常用 Blueprint 类型：

| 类型 | 用途 |
|---|---|
| Actor Blueprint | 门、道具、机关、投射物、交互物。 |
| Pawn Blueprint | 可被控制的身体。 |
| Character Blueprint | 带角色移动的 Pawn。 |
| PlayerController Blueprint | 玩家输入、HUD、控制权。 |
| GameMode Blueprint | 玩法规则和默认类。 |
| Widget Blueprint | UI 界面。 |
| Animation Blueprint | 骨骼动画状态机和动画图。 |

---

## 7. 蓝图和 C++ 怎么分工

UE5 的项目经常同时用蓝图和 C++。不要把“蓝图”等同于玩具，也不要把所有玩法都塞进 C++。

| 场景 | 建议 |
|---|---|
| 新手学习、快速验证玩法 | 蓝图优先。 |
| UI、关卡机关、可调参数多的交互物 | 蓝图很合适。 |
| 底层系统、复杂数据结构、性能热点 | C++ 更合适。 |
| 给策划和美术开放调参 | C++ 提供基类，蓝图派生调参数。 |
| 网络同步、存档、资源加载、战斗框架 | C++ 打底，蓝图接表现和小逻辑。 |

典型团队分工：

```text
C++:
  UAttributeComponent
  UInventoryComponent
  ABaseCharacter
  UItemDataAsset

Blueprint:
  BP_PlayerCharacter
  BP_SlimeEnemy
  BP_Chest
  WBP_Inventory
```

### 7.1 生命周期对照

| Unity | UE5 蓝图 / C++ | 说明 |
|---|---|---|
| `Awake()` | Constructor / `OnConstruction` / Construction Script | 初始化默认组件、编辑器阶段构造表现。 |
| `Start()` | `BeginPlay` | 玩法开始时执行。 |
| `Update()` | `Tick` | 每帧执行，默认可以关。 |
| `OnEnable()` | `BeginPlay` / Activate Component | UE 的激活逻辑视对象类型而定。 |
| `OnDisable()` | EndPlay / Deactivate Component | Actor 被移除、关卡切换、游戏停止时会进 EndPlay。 |
| `OnDestroy()` | Destroyed / EndPlay | 销毁时清理引用、解绑事件。 |
| `OnTriggerEnter` | BeginOverlap | 碰撞组件开启 Generate Overlap Events 后触发。 |
| `OnCollisionEnter` | Hit Event | 需要碰撞阻挡和相关事件设置。 |

### 7.2 蓝图事件图的基本读法

蓝图图里有两种线：

| 线 | 含义 |
|---|---|
| 白色执行线 | 控制执行顺序。 |
| 彩色数据线 | 传递变量、对象引用、数值、布尔值等。 |

常见节点：

| 节点 | 用途 |
|---|---|
| `Event BeginPlay` | 开始运行时初始化。 |
| `Event Tick` | 每帧逻辑。 |
| `Branch` | if 判断。 |
| `Cast To XXX` | 把对象当成某个类型访问。 |
| `Get Actor Location` | 获取 Actor 坐标。 |
| `Spawn Actor From Class` | 生成 Actor。 |
| `Destroy Actor` | 销毁 Actor。 |
| `Print String` | 调试输出。 |

---

## 8. Gameplay Framework：UE 新手最该补的一块

Unity 里你可以从任意 MonoBehaviour 开始写，项目小的时候也能跑。UE 里 Gameplay Framework 更强，先理解它能少绕很多路。

| 类 | 作用 |
|---|---|
| GameInstance | 游戏启动到退出期间一直存在，跨地图保留。适合全局系统、存档入口、在线服务入口。 |
| GameMode | 当前玩法规则，只在服务端存在。决定默认 Pawn、PlayerController、HUD 等类。 |
| GameState | 当前局内公共状态，可复制给客户端。适合队伍分数、任务阶段、全局计时。 |
| PlayerController | 玩家控制器，处理输入、相机、UI、控制 Pawn。死亡重生时可以保持。 |
| Pawn | 可被 Controller 控制的身体。 |
| Character | Pawn 子类，带胶囊体和 CharacterMovement，适合常规人物。 |
| PlayerState | 单个玩家的可复制状态，例如分数、名字、队伍、等级。 |
| HUD / Widget | 显示界面。现代项目多用 UMG Widget。 |

一个玩家进游戏的典型关系：

```text
GameMode
└── 生成 PlayerController
    └── Possess Pawn / Character
        ├── 接收移动指令
        ├── 播放动画
        └── 和世界交互
```

新手常见问题是把输入、UI、角色状态、关卡规则全部写进 Character。更清楚的拆法：

| 内容 | 放哪 |
|---|---|
| 移动、跳跃、受击、攻击触发 | Character / Pawn |
| 输入映射、切换控制对象、打开 UI | PlayerController |
| 当前玩法规则、出生点、胜负条件 | GameMode |
| 跨地图数据、设置、存档入口 | GameInstance |
| 队伍分数、任务阶段、公共计时 | GameState |
| 单玩家分数、名字、队伍 | PlayerState |

---

## 9. Enhanced Input 输入系统

UE5 推荐用 Enhanced Input。它的核心是四个东西：

| 概念 | 用途 |
|---|---|
| Input Action | 玩家能做什么，例如 Move、Look、Jump、Attack。 |
| Input Mapping Context | 某套输入映射，例如默认操作、菜单操作、载具操作。 |
| Input Modifier | 改输入值，例如取反、归一化、死区。 |
| Input Trigger | 判断触发条件，例如按下、长按、组合键。 |

### 9.1 建议命名

```text
IA_Move
IA_Look
IA_Jump
IA_Attack
IA_Dodge
IA_Interact
IA_Pause

IMC_Default
IMC_Menu
IMC_Vehicle
```

### 9.2 配置流程

1. 在 Content Browser 右键。
2. 选择 `Input > Input Action`，创建 `IA_Move`。
3. 再创建 `Input Mapping Context`，命名 `IMC_Default`。
4. 打开 `IMC_Default`，添加 `IA_Move`。
5. 绑定 WASD、手柄左摇杆等。
6. 在 PlayerController 或 Character BeginPlay 里 Add Mapping Context。
7. 在蓝图里绑定 Input Action 事件。

### 9.3 Unity 对照

Unity 新 Input System 里你会建 Action Map 和 Action。UE 的 Mapping Context 接近 Action Map，Input Action 接近 Action。区别是 UE 的 Mapping Context 可以按玩法状态动态加减，比如角色走路、潜行、载具、菜单使用不同输入上下文。

---

## 10. 碰撞、Overlap、Trace

UE 的碰撞由两部分组成：

| 概念 | 含义 |
|---|---|
| Object Type | 自己是什么类型，例如 Pawn、WorldStatic、WorldDynamic。 |
| Response | 遇到其他类型时阻挡、重叠还是忽略。 |

常见响应：

| Response | 效果 |
|---|---|
| Block | 阻挡，会挡住移动或射线。 |
| Overlap | 不阻挡，但触发重叠事件。 |
| Ignore | 互相忽略。 |

### 10.1 Unity 对照

| Unity | UE5 |
|---|---|
| Collider + Is Trigger | Collision Enabled + Overlap Response |
| Rigidbody 碰撞 | Simulate Physics + Collision |
| Layer Collision Matrix | Project Settings > Collision |
| Raycast LayerMask | Trace Channel / Object Channel |
| OnTriggerEnter | OnComponentBeginOverlap |
| OnCollisionEnter | OnComponentHit |

### 10.2 新手排查碰撞

1. 选中组件，看 Collision Presets。
2. 确认 Collision Enabled 是否允许 Query 或 Physics。
3. 确认双方 Response 是否一个愿意 Overlap 或 Block。
4. Overlap 事件要开 Generate Overlap Events。
5. Hit 事件需要合适的阻挡和事件设置。
6. 用控制台命令或视图模式查看碰撞形状。

---

## 11. Data Asset：配置数据怎么做

Unity 的 ScriptableObject 在 UE 里可以对照 Data Asset 或 Primary Data Asset。

适合放 Data Asset 的内容：

| 数据 | 说明 |
|---|---|
| 道具配置 | 名字、图标、描述、稀有度、堆叠数。 |
| 武器配置 | 伤害、攻速、特效、音效、命中规则。 |
| 技能配置 | 冷却、消耗、目标类型、表现资源。 |
| 怪物配置 | 血量、攻击、掉落表、AI 类型。 |
| 任务配置 | 目标、奖励、文本、触发条件。 |

C++ 示例：

```cpp
UCLASS(BlueprintType)
class UWeaponDataAsset : public UPrimaryDataAsset
{
    GENERATED_BODY()

public:
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    FName WeaponId;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    FText DisplayName;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    int32 Damage = 10;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    float Cooldown = 0.3f;
};
```

蓝图项目也能用 Data Asset。做法是创建继承 Data Asset 的蓝图类，添加变量，再创建具体数据实例。

配置表项目可以保持“策划源表”和“引擎运行资产”分层：Excel/CSV/JSON 作为源数据，通过工具生成 Data Asset、Data Table 或 JSON。UE 运行时读取生成结果，减少手填错误。

---

## 12. Data Table、Curve Table、软引用

UE 还常用 Data Table 管结构化表格数据。它更像一张运行时可查询表。

| 资源 | 适合内容 |
|---|---|
| Data Asset | 单个配置对象，可关联图标、Mesh、蓝图类等资源。 |
| Primary Data Asset | 需要 Asset Manager 管理加载、卸载、打包规则的配置对象。 |
| Data Table | 大量同结构行数据，例如怪物数值表、等级经验表。 |
| Curve Table | 随等级、时间、阶段变化的曲线数值。 |

软引用也很重要：

| 引用 | 特点 |
|---|---|
| Hard Reference | 引用对象会跟着加载，简单直接。 |
| Soft Object Reference | 只保存路径，需要时再加载。 |
| Soft Class Reference | 适合配置里引用可生成的蓝图类。 |

大型项目里，资源加载问题常来自硬引用链过长。新手阶段先记住：配置资产里引用大模型、大 UI、大特效时，要想一下是否需要软引用。

---

## 13. UI：UMG 和 Widget Blueprint

UE 的 UI 常用 UMG。一个 UI 页面通常是 Widget Blueprint。

常见控件：

| 控件 | 用途 |
|---|---|
| Canvas Panel | 自由布局，适合 HUD 根节点。 |
| Vertical Box / Horizontal Box | 横纵布局。 |
| Overlay | 多层叠放。 |
| Border | 背景框。 |
| Text Block | 文本。 |
| Button | 按钮。 |
| Image | 图片。 |
| Progress Bar | 血条、进度条。 |
| Scroll Box | 滚动区域。 |
| Uniform Grid Panel | 背包格子。 |

### 13.1 创建 HUD

1. Content Browser 右键。
2. 选择 `User Interface > Widget Blueprint`。
3. 命名 `WBP_HUD`。
4. 打开后在 Designer 里摆 Text、Progress Bar。
5. 在 PlayerController BeginPlay 中 `Create Widget`。
6. 调 `Add to Viewport`。

### 13.2 UI 数据更新

不要每帧从 UI 里硬查角色状态。更常见做法：

| 方式 | 适合场景 |
|---|---|
| 事件分发器 Event Dispatcher | 血量、弹药、任务状态变化。 |
| 蓝图接口 Blueprint Interface | UI 和玩法对象松耦合通信。 |
| PlayerController 持有 HUD 引用 | 玩家本地 UI 统一管理。 |
| ViewModel / MVVM | 复杂 UI 项目可以使用。 |

---

## 14. 动画系统

UE 角色动画常用这些资产：

| 资产 | 用途 |
|---|---|
| Skeletal Mesh | 带骨骼的模型。 |
| Skeleton | 骨架资源。 |
| Animation Sequence | 单段动画。 |
| Animation Blueprint | 动画逻辑图。 |
| State Machine | 待机、走、跑、跳等状态切换。 |
| Blend Space | 根据速度、方向混合动画。 |
| Montage | 攻击、受击、技能等可插入播放的动画片段。 |
| Anim Notify | 动画帧事件，例如伤害判定、脚步声、特效点。 |

Unity 对照：

| Unity | UE5 |
|---|---|
| Animator Controller | Animation Blueprint + State Machine |
| Animation Clip | Animation Sequence |
| Blend Tree | Blend Space |
| Animation Event | Anim Notify |
| Timeline | Level Sequence |

新手建议先拆三层：

1. Character 蓝图管玩法状态，例如是否奔跑、是否攻击。
2. Animation Blueprint 读取角色速度、落地状态、攻击状态。
3. Montage 和 Notify 处理攻击窗口、特效、音效。

---

## 15. 材质、材质实例、贴图

UE 材质是节点图。材质决定表面如何受光、反射、透明、发光。

常见输入：

| 输入 | 含义 |
|---|---|
| Base Color | 基础颜色。 |
| Metallic | 金属度。 |
| Roughness | 粗糙度。 |
| Normal | 法线。 |
| Emissive Color | 自发光。 |
| Opacity / Opacity Mask | 透明或遮罩。 |

### 15.1 材质实例的价值

不要为每个颜色变化都复制一份完整材质。常见做法：

1. 做一个母材质 `M_Prop_Master`。
2. 暴露颜色、粗糙度、贴图等参数。
3. 创建 Material Instance，例如 `MI_Prop_Red`、`MI_Prop_Blue`。
4. 美术在实例里调参数，避免频繁重编译材质。

Unity 对照：材质实例有点像同一个 Shader 下的不同 Material 参数集，但 UE 的 Material Instance 层级和参数覆盖用得更频繁。

---

## 16. Lumen、Nanite、World Partition

这是 UE5 最容易听到的三类大功能。

### 16.1 Lumen

Lumen 是 UE5 的动态全局光照和反射系统。它让室内外间接光、颜色反弹、动态灯光变化更自然。

适合：

- 桌面端和主机项目。
- 动态时间、动态灯光、开放场景。
- 需要少烘焙或不烘焙光照的流程。

注意：

- 移动端和低配平台要单独评估。
- 室内镜面、高频小光源、透明反射会吃性能。
- 项目一开始就要定渲染目标和 Scalability 档位。

### 16.2 Nanite

Nanite 是虚拟化几何体系统。它能处理高面数静态网格，减少传统 LOD 工作量。

适合：

- 高面数静态模型。
- 岩石、建筑、雕塑、环境资产。
- 大量细节但形变不强的模型。

注意：

- 部分材质和渲染路径对 Nanite 有限制。
- 透明材质、强形变、部分特效类网格要看限制。
- 仍然需要关注材质复杂度、纹理内存、实例数量。

### 16.3 World Partition

World Partition 用于大世界关卡管理。它把大地图分成网格，根据距离自动加载和卸载。

适合：

- 开放世界。
- 大地图多人协作。
- 需要 One File Per Actor 的团队编辑流程。

小关卡、线性关卡、室内 Demo 不一定急着用。先把普通 Level、Actor、GameMode、打包跑通，再决定是否上 World Partition。

---

## 17. Niagara 特效

Niagara 是 UE5 的主力 VFX 系统。

核心概念：

| 概念 | 用途 |
|---|---|
| Niagara System | 一个完整特效，例如爆炸、火焰、传送门。 |
| Emitter | 一个发射器，例如烟、火星、光点。 |
| Module | 具体行为，例如速度、颜色、生命周期、碰撞。 |
| Parameter | 外部传入或内部控制的变量。 |

Unity 对照：

| Unity | UE5 |
|---|---|
| Particle System | Niagara System / Emitter |
| VFX Graph | Niagara Graph |
| Shader 参数控制 VFX | Niagara Parameter + Material Parameter |

常见用法：

- 子弹命中特效。
- 角色技能轨迹。
- 环境烟尘、火焰、雨雪。
- UI 里的局部粒子表现。
- 和蓝图联动，根据伤害类型改颜色、大小、材质。

---

## 18. 音频

UE 音频资源导入后通常会成为 Sound Wave。蓝图里可以直接 Play Sound，也可以 Spawn Sound 得到 Audio Component 继续控制。

常见资产和概念：

| 名称 | 用途 |
|---|---|
| Sound Wave | 导入后的基础音频资源。 |
| Sound Cue | 组合、随机、调制等旧式音频逻辑资源。 |
| MetaSound | 节点式程序音频和交互音频。 |
| Sound Attenuation | 3D 音频衰减、空间化规则。 |
| Sound Class | 音频分类，例如 BGM、SFX、UI。 |
| Sound Mix / Submix | 混音、效果处理。 |
| Audio Component | 可动态控制播放、停止、参数、附着位置。 |

简单规则：

- UI 音效用 2D 播放。
- 场景里的声源用空间音频和 Attenuation。
- 循环声用 Audio Component 控制。
- 音量设置走 Sound Class 或 Submix。

---

## 19. 资源导入和 Content Browser

UE 项目资源大多会变成 `.uasset`。导入模型、贴图、音频后，不要在资源管理器里随便移动文件，优先在 Content Browser 里移动，让引用关系跟着更新。

常见导入：

| 资源 | 注意点 |
|---|---|
| Static Mesh | 碰撞、LOD、Nanite、材质槽。 |
| Skeletal Mesh | Skeleton、Physics Asset、动画导入。 |
| Texture | sRGB、Compression、Mipmaps、贴图类型。 |
| Audio | 格式、循环、衰减、压缩。 |
| FBX / USD | 单位、轴向、材质、动画拆分。 |

### 19.1 Redirector

移动或重命名资源后，UE 会留下 Redirector。团队项目要定期：

```text
Content Browser 右键目录 > Fix Up Redirectors in Folder
```

这样可以减少旧引用、打包警告和资源路径混乱。

---

## 20. 打包、Cook、Package

UE 打包常见词：

| 词 | 含义 |
|---|---|
| Cook | 把资源转换成目标平台可用格式。 |
| Build | 编译代码。 |
| Package | 生成可运行包。 |
| Deploy | 部署到设备。 |
| Pak / IoStore | 打包后的资源容器。 |

### 20.1 Windows 打包基础流程

1. 打开 `Edit > Project Settings`。
2. 检查 `Maps & Modes` 的默认地图。
3. 检查 `Project > Packaging` 设置。
4. 顶部菜单进入 `Platforms > Windows`。
5. 选择 Shipping 或 Development。
6. 点击 Package Project。
7. 打包完成后运行生成目录里的 exe。

### 20.2 Unity 对照

| Unity | UE5 |
|---|---|
| Build Settings | Platforms / Project Settings |
| Player Settings | Project Settings |
| Development Build | Development Configuration |
| Release Build | Shipping Configuration |
| Build AssetBundles | Cook + Pak / IoStore |
| Addressables Profile | Asset Manager + Packaging Rules |

---

## 21. 调试和性能查看

UE 的调试入口很多，新手先记这些：

| 工具 | 用途 |
|---|---|
| Output Log | 日志、错误、控制台命令。 |
| Print String | 蓝图快速输出。 |
| Blueprint Debugger | 断点、单步、看变量。 |
| Visual Logger | AI、移动、碰撞等可视化记录。 |
| Collision View / Show Collision | 看碰撞形状。 |
| Stat 命令 | `stat fps`、`stat unit`、`stat gpu`。 |
| Unreal Insights | CPU、线程、加载、网络等深入分析。 |
| Reference Viewer | 看资源引用链。 |
| Size Map | 看资源体积和内存风险。 |

常用控制台命令：

```text
stat fps
stat unit
stat gpu
show collision
showdebug enhancedinput
```

排查顺序：

1. 先看 Output Log 的红色错误。
2. 蓝图逻辑用断点和 Print String。
3. 输入问题用 `showdebug enhancedinput`。
4. 碰撞问题先显示碰撞形状。
5. 卡顿先看 `stat unit` 判断 CPU、GPU、Game Thread、Draw Thread。
6. 资源过大用 Reference Viewer 和 Size Map。

---

## 22. 源控制和团队协作

UE 项目文件体积大，二进制资源多，团队协作要比 Unity 更早规划。

### 22.1 建议纳入版本控制

```text
Config/
Content/
Source/
Plugins/
*.uproject
```

### 22.2 常见忽略

```text
Binaries/
DerivedDataCache/
Intermediate/
Saved/
.vs/
```

### 22.3 Git 和 Perforce

| 方案 | 适合 |
|---|---|
| Git + LFS | 小团队、二进制资源规模可控。 |
| Perforce | 大团队、大量美术资源、需要文件锁。 |

UE 的 `.uasset` 是二进制文件，合并冲突很难手工处理。关卡协作建议使用 One File Per Actor、World Partition 或严格分工。

---

## 23. 新手练习路线

### 第 1 天：编辑器和模板

- 创建 Third Person 项目。
- 运行默认角色。
- 找到 `BP_ThirdPersonCharacter`。
- 看 Components、Event Graph、默认输入。
- 新建并保存一个自己的 Level。

### 第 2 天：Actor 和 Blueprint

- 创建 `BP_Door`。
- 添加 Static Mesh 和 Box Collision。
- 玩家靠近时触发 Overlap。
- 按 Interact 打开门。
- 在 Details 里暴露门打开角度和速度。

### 第 3 天：Enhanced Input

- 创建 `IA_Interact`。
- 创建或修改 `IMC_Default`。
- 绑定键盘 E 和手柄按钮。
- 在 Character 或 PlayerController 里响应输入。
- 打印当前可交互对象名称。

### 第 4 天：UI

- 创建 `WBP_HUD`。
- 添加血条、金币文本、提示文本。
- PlayerController 创建并显示 HUD。
- 角色血量变化时更新血条。

### 第 5 天：Data Asset

- 创建 `DA_Weapon_Sword` 和 `DA_Weapon_Axe`。
- 配伤害、冷却、图标。
- 角色引用当前武器数据。
- 攻击时读取 Data Asset 参数。

### 第 6 天：动画和特效

- 打开角色 Animation Blueprint。
- 看移动状态机。
- 做一个攻击 Montage。
- 用 Anim Notify 触发 Niagara 特效和音效。

### 第 7 天：打包

- 检查默认地图。
- 清理 Redirector。
- 用 Development 打包 Windows。
- 运行打包产物。
- 检查输入、UI、资源加载、日志。

---

## 24. Unity 使用者常见卡点

| 卡点 | 处理建议 |
|---|---|
| 把 Actor 当成纯 GameObject 容器 | Actor 可以直接继承和写逻辑，也可以挂组件。Blueprint Class 是常用复用单位。 |
| 在 Level Blueprint 写大量通用玩法 | Level Blueprint 适合关卡专属逻辑；可复用玩法放 Actor Blueprint、Component 或 Subsystem。 |
| 到处开 Tick | 能用事件、Timer、Overlap、Input Action 就少开 Tick。 |
| 角色逻辑全塞 Character | 输入放 PlayerController，规则放 GameMode，跨地图数据放 GameInstance。 |
| 硬引用所有资源 | 大资源、可选资源、异步加载资源考虑 Soft Reference。 |
| UI 绑定每帧查数据 | 用事件分发器或控制器主动推送更新。 |
| 随便移动 `.uasset` 文件 | 在 Content Browser 里移动，并 Fix Up Redirectors。 |
| 直接上开放世界全家桶 | 先用普通 Level 跑通基础玩法，再上 World Partition、Data Layers。 |
| 只看蓝图节点不看日志 | Output Log 是第一排查入口。 |
| 忽略打包测试 | 编辑器能跑不代表打包能跑，资源引用和路径问题常在打包阶段暴露。 |

---

## 25. 快捷键和操作习惯

| 操作 | 快捷键 |
|---|---|
| 保存当前资产 | `Ctrl + S` |
| 保存全部 | `Ctrl + Shift + S` |
| 内容浏览器搜索 | Content Browser 搜索框 |
| 复制 Actor | `Ctrl + W` 或 `Alt + 拖动` |
| 聚焦选中对象 | `F` |
| 运行 | `Alt + P` |
| 停止运行 | `Esc` 或停止按钮 |
| 世界坐标/本地坐标切换 | Viewport 顶部坐标按钮 |
| 移动/旋转/缩放 | `W` / `E` / `R` |

---

## 26. 继续学习时优先看哪些官方页

- UE 5.7 Release Notes：确认当前正式版本功能范围。
- Unity to Unreal Engine Overview：按 Unity 经验迁移编辑器和概念。
- Game Objects in Unreal Engine：理解 Actor、UObject、Component。
- Gameplay Framework：理解 GameMode、Pawn、Controller、GameInstance。
- Blueprints Visual Scripting：学习蓝图类型、事件图、变量、函数。
- Enhanced Input：学习 Input Action、Mapping Context、Trigger、Modifier。
- Data Assets：学习配置资源。
- UMG UI：学习 Widget Blueprint 和 HUD。
- Collision Overview：学习 Object Type、Response、Overlap、Hit。
- Materials：学习材质节点和材质实例。
- Lumen、Nanite、World Partition：理解 UE5 的渲染和大世界能力边界。
- Packaging and Cooking Games：学习 Cook、Package、Deploy。

---

## 27. 一句话抓主线

Unity 经验可以帮你理解对象、组件、输入、UI、资源和打包；进入 UE5 后，先把 Actor、Component、Blueprint Class、Gameplay Framework、Enhanced Input、Data Asset 这几块用熟。能用这些词描述清楚一个功能，UE 项目结构会清楚很多。

---

## 参考来源

- Unreal Engine 5.7 Release Notes：https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-7-release-notes
- Unreal Engine 5.8 Preview 公告：https://forums.unrealengine.com/t/unreal-engine-5-8-preview/2721597
- Unity to Unreal Engine Overview：https://dev.epicgames.com/documentation/en-us/unreal-engine/unity-to-unreal-engine-overview
- Game Objects in Unreal Engine：https://dev.epicgames.com/documentation/unreal-engine/game-objects-in-unreal-engine
- Unreal Engine Terminology：https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-terminology
- Gameplay Framework：https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-framework-in-unreal-engine
- Blueprints Visual Scripting：https://dev.epicgames.com/documentation/en-us/unreal-engine/blueprints-visual-scripting-in-unreal-engine
- Enhanced Input：https://dev.epicgames.com/documentation/unreal-engine/enhanced-input-in-unreal-engine
- Data Assets：https://dev.epicgames.com/documentation/en-us/unreal-engine/data-assets-in-unreal-engine
- Working with Assets：https://dev.epicgames.com/documentation/en-us/unreal-engine/working-with-assets-in-unreal-engine
- Collision Overview：https://dev.epicgames.com/documentation/unreal-engine/collision-in-unreal-engine---overview
- Creating User Interfaces With UMG and Slate：https://dev.epicgames.com/documentation/en-us/unreal-engine/creating-user-interfaces-with-umg-and-slate-in-unreal-engine
- Creating Visual Effects in Niagara：https://dev.epicgames.com/documentation/en-us/unreal-engine/creating-visual-effects-in-niagara-for-unreal-engine
- Materials：https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-materials
- Lumen：https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine
- Nanite：https://dev.epicgames.com/documentation/unreal-engine/nanite-virtualized-geometry-in-unreal-engine
- World Partition：https://dev.epicgames.com/documentation/unreal-engine/world-partition-in-unreal-engine
- Packaging and Cooking Games：https://dev.epicgames.com/documentation/unreal-engine/packaging-and-cooking-games-in-unreal-engine
