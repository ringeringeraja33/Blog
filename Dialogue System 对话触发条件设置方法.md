# 核心逻辑

Dialogue System 里可以用变量记录剧情状态，再用条件控制某段对话是否出现。

- `Variables`：负责存状态。
- `Script`：负责改变状态。
- `Conditions`：负责根据状态决定对话能不能出现或执行。

# 1. 先建变量

在 `Variables` 面板里新增一个变量，例如：

```lua
ZKKnowTHESon
```

推荐设置：

- `Type`：`Boolean`
- `Initial Value`：`False`

这个变量用来记录玩家是否已经知道某件事、触发过某段剧情、完成过某个条件。

# 2. 在需要解锁的对话节点加 Conditions

选中需要被条件限制的对话节点，在右侧 `Conditions` 里写：

```lua
Variable["ZKKnowTHESon"] == true
```

意思是：只有当 `ZKKnowTHESon` 为 `true` 时，这条对话才会出现或执行。

`False Condition Action` 建议设为：

```
Block
```

意思是：条件不满足时，直接挡住这条对话分支。

# 3. 在前面的对话节点里设置变量

在玩家获得信息、完成对话、触发剧情的节点里，找到 `Script` 字段，写：

```lua
Variable["ZKKnowTHESon"] = true
```

意思是：当这句对话执行后，把变量改成 `true`，后续带这个条件的对话就能触发。

# 4. 常用写法

布尔判断：

```lua
Variable["DiffDialogue"] == true
Variable["DiffDialogue"] == false
```

布尔赋值：

```lua
Variable["DiffDialogue"] = true
Variable["DiffDialogue"] = false
```

数字判断：

```lua
Variable["BarkValue1"] >= 1
Variable["BarkValue1"] == 3
```

数字赋值：

```lua
Variable["BarkValue1"] = 1
Variable["BarkValue1"] = Variable["BarkValue1"] + 1
```

# 5. 示例流程

假设玩家听到这句：

```
咦？你是……我之前见到的就是你的儿子吧。
```

在这个节点的 `Script` 里写：

```lua
Variable["ZKKnowTHESon"] = true
```

之后另一个需要前置信息的节点，在 `Conditions` 里写：

```lua
Variable["ZKKnowTHESon"] == true
```

这样这条后续对话就只会在玩家已经知道“儿子”这件事之后触发。