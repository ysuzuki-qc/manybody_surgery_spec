# 2Dルーティング問題

## 背景

最も一般的なfault-tolerant quantum computing architectureでは、qubitはsurface codeで符号化され、各surface codeはphysical qubitの2次元配列上の正方形blockを占有する。複数のsurface-code qubitに対する演算はlattice surgeryで実装され、未使用のsurface-code blockを介して関連するlogical qubitを2次元空間内で接続する。routeを最適化することでinstruction-level parallelismを高め、algorithm全体の実行時間を短縮できる。この最適化問題は3次元版Tetrisとみなせる。本書ではlattice-surgery routingの基本規則を説明する。

## Lattice Surgery

ノード `(x_1, y_1), (x_2, y_2), ... (x_v, y_v)` からなる2次元gridの部分集合を考える。隣接するノードの一部、すなわち `|x_i-x_j| + |y_i-y_j| = 1` を満たす `(x_i, y_i)` と `(x_j, y_j)` は辺 `(i,j) \in E` で接続される。`v` 個のノードから `n` 個を選び、`n` 個のdata qubitを配置する。data qubitを保持するノードをdata node、残りをempty nodeと呼ぶ。lattice-surgery命令は、すべてのoperand data nodeを葉（辺を1本持つノード）、empty nodeをbranch（複数の辺を持つノード）とする木、すなわちSteiner treeを選ぶことで実行できる。
 
`1 <= x_i <= 8`、`1 <= y_i <= 3` を満たす24ノードの2次元gridを考え、`n=4` 個のdata nodeが `(2,2)`, `(3,2)`, `(5,3)`, `(7,2)` に配置されているとする。次の模式図でこの配置を表す。各整数は対応するindexのdata nodeを、`.` はempty nodeを表す。
```
. . . . . . . .

. 1 2 . . . 4 .

. . . . 3 . . .
```

lattice-surgery命令では、指定されたboundaryを介して複数のdata nodeをempty nodeの木で接続する。例えば `LATTICE_SURGERY [2 4] [V H]` は、第2data nodeへvertical boundary（上または下）から、第4data nodeへhorizontal boundary（左または右）から接続することを要求する。各data nodeには指定された向きのboundaryが2つあるため、適切ないずれかを選べる。実装例を次に示す。`*` は演算中に一時使用するempty node、`-` と `|` は使用する辺を表す。
```
. . *-*-*-* . . .
    |     |
. 1 2 . . *-4 .

. . . . 3 . . .
```

lattice-surgery命令の実装は一意ではない。同じ命令を次のようにも実行できる。lattice surgeryのlatencyは一定で、木の大きさには依存しない。
```
. . . . . *-*-*
          |   |
. 1 2 *-*-* 4-*
    | |
. . *-* 3 . . .
```

lattice surgeryは3つ以上のdata nodeにも作用できる。例えば `LATTICE_SURGERY [1 3 4] [H H H]` は次のように実装できる。
```
. . . . . . . .
               
*-1 2 *-*-*-4 .
|     |
*-*-*-*-3 . . .
```


### 命令の規則

以下では `LATTICE_SURGERY [1 3 4] [H H H]` を使って規則を説明する。選択したrouting graphは、その辺集合で表現できる。各命令に割り当てるrouting graphは次の規則をすべて満たさなければならない。

- **規則1：routing graphは木でなければならない。**

次のグラフは `(4,1)`, `(5,1)`, `(5,2)`, `(4,2)` を通るcycleを含むため無効である。
```
. . . *-* . . .
      | |       
*-1 2 *-*-*-4 .
|     |
*-*-*-*-3 . . .
```

次のグラフはdata node 3を通るcycleを含むため無効である。
```
. . . . . . . .
               
*-1 2 *-*-*-4 .
|     |   |
*-*-*-*-3-* . .
```

次のグラフは辺集合が非連結なので無効である。
```
. . . . . . . .
                 
*-1 2-*-*-*-4 .
|      
*-*-*-*-3 . . .
```

- **規則2：すべてのoperand nodeはrouting graphの葉でなければならない。**

次のグラフはoperand data node 3が接続されていないため無効である。
```
. . . . . . . .
               
*-1 2 *-*-*-4 .
|     |
*-*-*-* 3 . . .
```

次のグラフはdata node 3が木の葉ではないため無効である。
```
. . . . . . . .
               
*-1 2 . . *-4 .
|         |
*-*-*-*-3-* . .
```

- **規則3：木のすべての葉はdata nodeでなければならない。**

次のグラフはempty node `(4,1)` で木が終端するため無効である。
```
. . . * . . . .
      |         
*-1 2 *-*-*-4 .
|     |
*-*-*-*-3 . . .
```

- **規則4：operandではないdata nodeを接続してはならない。**

次のグラフはoperandではないdata node 2が接続されているため無効である。
```
. . . . . . . .
               
*-1 2-*-*-*-4 .
|     |
*-*-*-*-3 . . .
```

- **規則5：すべてのoperand data nodeへ指定方向から接続しなければならない。**

次のグラフはoperand data node 3に垂直方向から接続しているため無効である。
```
. . . . . . . .
               
*-1 2 *-*-*-4 .
|     | |
*-*-*-* 3 * . .
```

要約すると、`各routing graphは、operand data nodeの指定されたboundaryで終端し、operandではないdata nodeを含まないSteiner treeでなければならない。`

### 並列実行

lattice-surgery命令の実行には1単位時間を要し、一時使用したempty nodeは実行後に解放される。taskはlattice-surgery命令列として与えられ、目的は総実行時間の最小化である。そのため、可能な限り多くの命令を並列実行してinstruction throughputを最大化する。

3つの命令があるとする。
```
1: LATTICE_SURGERY [1 3] [H H]
2: LATTICE_SURGERY [2 4] [V H]
3: LATTICE_SURGERY [2 3] [H H]
```
各命令に対するrouteの例を次に示す。
```
1: LATTICE_SURGERY [1 3] [H H]
. . . . . . . .
               
*-1 2 . . . 4 .
|          
*-*-*-*-3 . . .
```

```
2: LATTICE_SURGERY [2 4] [V H]
. . *-*-*-* . .
    |     |     
. 1 2 . . *-4 .
         
. . . . 3 . . .
```

```
3: LATTICE_SURGERY [2 3] [H H]
. . . . . . . .
                
. 1 2-* . . 4 .
      |  
. . . *-3 . . .
```

1番目と2番目のrouteは並列実行できる。
```
T=1
. . *-*-*-* . .
    |     |     
*-1 2 . . *-4 .
|        
*-*-*-*-3 . . .
```

最初の2命令が完了した後、3番目の命令を `T=2` で実行できる。
```
. . . . . . . .
                
. 1 2-* . . 4 .
      |  
. . . *-3 . . .
```

与えられた `m` 個の命令に対し、全命令の完了時間を最小にするrouting treeとscheduleを求める。

### 並列実行の規則

具体例を使って次の規則を説明する。

- **並列規則1：routing treeは同じ時刻に同じempty nodeを共有してはならない。**

次の2命令はempty node `(4,2)` を共有するため並列実行できない。
```
1: LATTICE_SURGERY [1 4] [V H]
. *-*-*-* . . . .
  |     |      
. 1 2 . *-*-4 .
   
. . . . 3 . . .

2: LATTICE_SURGERY [2 3] [H V]
. . . . . . . .
              
. 1 2-*-* . 4 .
        |
. . . . 3 . . .
```

- **並列規則2：routing treeは同じ時刻に異なる向きのboundaryを介して同じdata nodeを共有してはならない。**

次の2命令は共有data nodeへ異なる方向から接続するため並列実行できない。
```
1: LATTICE_SURGERY [1 2] [V V]

. *-* . . . . .
  | |          
. 1 2 . . . 4 .
   
. . . . 3 . . .

2: LATTICE_SURGERY [2 3] [H V]
. . . . . . . .
              
. 1 2-*-* . 4 .
        |
. . . . 3 . . .
```

同じ向きのboundaryを介してdata nodeを共有することは許される。したがって次の2命令は並列実行できる。
```
1: LATTICE_SURGERY [1 2] [V V]

. *-* . . . . .
  | |          
. 1 2 . . . 4 .
   
. . . . 3 . . .

2: LATTICE_SURGERY [2 3] [V H]
. . . . . . . .
              
. 1 2 . . . 4 .
    |    
. . *-*-3 . . .
```


## 入力と出力

### 入力
入力形式は次のとおりである。
```
v e n m
x_1 y_1
x_2 y_2
...
x_v y_v
w_{1,1} w_{1,2}
w_{2,1} w_{2,2}
...
w_{e,1} w_{e,2}
t_1
q_{1,1} q_{1,2} ... q_{1,t_1}
p_{1,1} p_{1,2} ... p_{1,t_1}
t_2
q_{2,1} q_{2,2} ... q_{2,t_2}
p_{2,1} p_{2,2} ... p_{2,t_2}
...
t_m
q_{m,1} q_{m,2} ... q_{m,t_m}
p_{m,1} p_{m,2} ... p_{m,t_m}
```

ここで `v`, `e`, `n`, `m` は、それぞれノード数、辺数、data node数、命令数を表す正整数である。`x_i`, `y_i` は第`i`ノードのx座標とy座標である。
`w_{i,1}`, `w_{i,2}` は、第`i`辺がnode `w_{i,1}` と `w_{i,2}` を接続することを表し、`1 <= w_{i,1}, w_{i,2} <= v` を満たす。
`t_i` は第`i` lattice-surgery命令のoperand data node数であり、`2 <= t_i <= n` を満たす。
`q_{i,j}` は第`i` lattice-surgery命令の第`j` operand data nodeのindexであり、`1 <= q_{i,j} <= n` を満たす。各data nodeは各命令のoperandに高々1回だけ現れる。すなわち `j \neq j'` ならば `q_{i,j} \neq q_{i,j'}` である。
`p_{i,j}` は第`i` lattice-surgery命令の第`j` operand data nodeのboundary orientationを指定し、`p_{i,j} \in {H,V}` を満たす。


### 出力
出力形式は次のとおりである。
```
P_1 P_2 ... P_n
T_1 R_1 E_{1,1} E_{1,2} ... E_{1,R_1}
T_2 R_2 E_{2,1} E_{2,2} ... E_{2,R_2}
...
T_m R_m E_{m,1} E_{m,2} ... E_{m,R_m}
```

`P_i` は第`i` qubitを配置するnodeであり、`1 <= P_i <= v` を満たす。異なるqubitは異なるnodeに配置されるため、`i \neq i'` ならば `P_i \neq P_i'` である。
`T_i` は第`i` lattice-surgery命令を実行するclock cycleであり、`1 <= T_i` を満たす（最初のclock cycleは1）。`i < j` ならば `T_i <= T_j` である。
`R_i` は第`i` lattice-surgery命令のrouting treeに含まれる辺数であり、`1 <= R_i <= e` を満たす。
`E_{i,j}` は第`i` lattice-surgery命令のrouting treeに含まれる第`j`辺であり、`1 <= E_{i,j} <= e` を満たす。各辺は木に高々1回だけ現れるため、`j \neq j'` ならば `E_{i,j} \neq E_{i,j'}` である。

各treeは上記の規則と並列規則をすべて満たさなければならない。同時刻に実行するtreeは2つの並列規則を満たさなければならない。目的は `T_m` の最小化である。


### 問題サイズ
quantum-computing advantageを示すには、`v` と `n` は少なくとも50程度が望ましく、ほとんどの用途では10,000以下で十分と考えられる。
同様に、実用上意味のある用途では `m` は約1,000以上、`10^15` 以下が想定される。


## 問題の単純化
上の定義は複雑なので、以下の仮定を使って問題を単純化することがある。これらは必須ではないが、最適化に焦点を当てるために採用する論文もある。

- **仮定1：長方形grid**

多くのarchitectureではnodeを長方形領域に配置し、すべてのnearest-neighbor pairを辺で接続する。この場合、node座標 `x_i, y_i` と辺 `w_{i,j}` の明示的なlistの代わりに、2つの整数 `w`, `h` で指定できる。例えば `w=3, h=2` は次を意味する。
```
6 7 n m
1 1
1 2
2 1
2 2
3 1
3 2
1 2
1 3
2 4
3 4
3 5
4 6
5 6
```


- **仮定2：固定layout**

通常はdata-qubit indexからnode indexへのmapping、すなわちqubit placementも決定する必要がある。しかしplacementとroutingは相互依存し、同時最適化が難しい。routingだけに集中するため、固定qubit layoutを仮定することがある。

data qubitを密に配置する一方、各data qubitのhorizontal boundaryとvertical boundaryを少なくとも1つずつ利用可能にする必要がある。そのため、次のlayoutがよく用いられる。
```
1-in-4 location (25% density)
. . . . . . . 
. 1 . 2 . 3 .
. . . . . . .
. 4 . 5 . 6 .
. . . . . . .
. 7 . 8 . 9 .
. . . . . . . 
```

```
4-in-9 location (44% density)
. . . . . . . 
. 1 2 . 5 6 .
. 3 4 . 7 8 .
. . . . . . .
. 9 a . d e .
. b c . f g .
. . . . . . . 
```

各data nodeがhorizontal boundaryとvertical boundaryをともに露出する既知の最密layoutを次に示す。ただしroutingの自由度は大きく制限される。
```
1-in-2 location (50% density)
. . . . . . . . .
. 6 7 . . 1 2 . .
. . 8 9 . . 3 4 .
. . . a b . . 5 .
. g . . c d . . .
. h i . . e f . .
. . . . . . . . .
```

ROTATIONとMOVE演算を使用できる場合（extension節参照）、次のようなより高密度のlayoutを選べる。
```
2-in-3 location (66% density)
. . . . . . . 
. 1 2 . b c .
. 3 4 . d e .
. 5 6 . f g .
. 7 8 . h i .
. 9 a . j k .
```

```
line-scan location (100% density)
1 2 3 4 5
6 7 8 9 a
. . . . .
b c d e f
g h i j k
```

```
point-scan location (100% density)
1 2 3 4 5
6 7 8 9 a
b c d e .
f g h i j
k l m n o
```


- **仮定3：two-body measurement**

一般的なcompilation schemeの中には、operand qubitが2つ（`t_i=2`）のlattice-surgery命令だけを生成するものがある。各命令へ最短treeをgreedyに割り当てる方法が考えられる。一般にはminimum Steiner tree問題でありNP-hardなので、approximation algorithmが必要になる。しかし `t_i=2` ならshortest-path問題へ帰着し、polynomial timeで解ける。


- **仮定4：同じboundary**

一般的なcompilation schemeの中には、同じ向きのboundaryだけに接続するlattice-surgery命令、すなわち `p_{i,1} = p_{i,2} = ... = p_{i,t_i}` だけを生成するものがある。boundary orientationはrouting問題の本質ではないため、この仮定によってsolverを単純化できる。


## 問題の拡張

次の拡張は理論上可能だが、問題定義はより複雑になる。

- **拡張1：Rotation**

各data nodeは、qubit orientationを90度回転させる `ROTATION` 命令を実行できる。この演算はdata nodeに隣接するempty nodeを占有し、2 clock cycleを要する。その後の全命令ではboundary orientationが交換される（`V <-> H`）。次の命令を考える。
```
LATTICE_SURGERY [1,2] [H H]
LATTICE_SURGERY [1,2] [V V]
LATTICE_SURGERY [1,2] [H H]

T=1
. . . . 
  
. 1-2 .

. . . .

T=2
. *-* . 
  | |
. 1 2 .

. . . .

T=3
. . . . 
     
. 1-2 .

. . . .

```
`T=2` にROTATION命令を挿入できる。
```
LATTICE_SURGERY [1,2] [H H]
ROTATION 1
LATTICE_SURGERY [1,2] [H V]
LATTICE_SURGERY [1,2] [V H]

T=1
. . . . 
   
. 1-2 .

. . . .

T=2
. * . . 
  |  
. 1 2 .

. . . .

T=3
. * . . 
  |     
. 1 2 .

. . . .

T=4
*-*-* . 
|   |   
*-1 2 .

. . . .


T=5
. *-*-* 
  |   | 
. 1 2-*

. . . .

```



- **拡張2：Logical qubitの移動**

data qubitをあるnodeから別のnodeへ移動する `MOVE` 命令を挿入できる。`MOVE` は1 clock cycleを要し、元のnodeとdestination nodeを結ぶpath上のempty nodeを占有する。pathが元のnodeとdestination nodeへ異なる向きのboundaryから接続する場合、後続演算のboundary orientationは交換される（`V <-> H`）。

```
LATTICE_SURGERY [1,2] [H H]
MOVE 1 [(2,2), (1,2)]
LATTICE_SURGERY [1,2] [V V]
LATTICE_SURGERY [1,2] [H H]

T=1
. . . . 
   
. 1-2 .

. . . .

T=2
. . . . 
     
*-1 2 .

. . . .

T=3
.-.-. . 
|   |  
1 . 2 .

. . . .

T=4
. . . . 
     
1-*-2 .

. . . .
```

```
LATTICE_SURGERY [1,2] [H H]
MOVE 1 [(2,2), (1,1)]
LATTICE_SURGERY [1,2] [H V]
LATTICE_SURGERY [1,2] [V H]

T=1
. . . . 
   
. 1-2 .

. . . .

T=2
* . . . 
|     
*-1 2 .

. . . .

T=3
1-.-. . 
    |  
. . 2 .

. . . .

T=4
1 . . . 
|    
*-*-2 .

. . . .
```

- **拡張3：lattice-surgery命令の並べ替え**

連続する2命令が次の条件を満たす場合、quantum operation列を並べ替えられる。

1. `Q` を、両方のlattice-surgery operationが作用するdata nodeの集合とする。
2. `T` を、`Q` 内で2演算が異なるboundary orientation（`H`, `V`）から接続するdata nodeの数とする。
3. `T` が偶数である場合、かつその場合に限り、動作を変えずに2演算を交換できる。

- `LATTICE_SURGERY [0 1] [H H]` と `LATTICE_SURGERY [2 3] [H H]` は共通のoperand data nodeを持たないため交換できる。
- `LATTICE_SURGERY [0 1] [H H]` と `LATTICE_SURGERY [1 2] [H H]` は、共有data node 1へ同じboundary orientationから接続するため交換できる。
- `LATTICE_SURGERY [0 1] [H H]` と `LATTICE_SURGERY [1 2] [V H]` は、共有data node 1へ異なるboundary orientationから接続するため交換できない。
- `LATTICE_SURGERY [0 1] [H H]` と `LATTICE_SURGERY [0 1] [V V]` は、共有data nodeへ異なるboundary orientationから2回接続するため交換できる。

並べ替えを許す場合、dependency graphを事前に作ることで、命令が実行可能かを高速に判定できる。
dependency graphは各nodeが命令に対応するdirected graphであり、instruction BをAの後に実行する必要がある場合、AからBへ辺を張る。このgraphの構築後は、命令のすべてのpredecessorが完了していれば実行可能と判定できる。

- **拡張4：Magic state**

universal fault-tolerant quantum computationにはmagic stateが必要である。任意の位置にmagic-state factoryを配置または撤去できる。factoryの配置中、そのnodeはlattice surgeryに使用できない。簡単のため、各factoryはnode networkの連結な `2 x 2` 領域を占有すると仮定する。配置後、factoryは各clock cycleにmagic state生成を試み、各試行は確率 `p` で成功する。

各lattice-surgery命令は追加引数 `M \in {0,1}` を持つ。`M=1` の場合、命令をmagic-state factoryへ接続しなければならず、接続に使うfactory boundaryは任意である。接続時にはmagic-state nodeに隣接する追加nodeを一時的に確保し、`R` clock cycle後に解放する。定数 `p`, `R` は問題の一部として与えられる。

```
R=3
p=0.1
LATTICE_SURGERY [0 1] [H H] 1

T=1 create magic state factory at 2x2 region of (6,1),(6,2),(7,1),(7,2).
Because this instruction consumes a magic state, execution must wait until one has been generated successfully.
. . . . . M M

. 0 . 1 . M M

. . . . . . .


T=7, suppose that magic-factory succeeds magic-state generation
. . . . . M M

. 0 . 1 . M M

. . . . . . .

T=8
. . *-*-*-M M
    |
. 0-*-1 . M M

. . . . . . .
```

実際のmagic-state生成手順は複雑である。詳細は [A game of surface codes](https://arxiv.org/pdf/1808.02892) を参照されたい。
（より正確には、上の定義はFig. 17のautocorrected pi/8 rotationを使用し、`2 x 2` blockはFig. 17(c) step 2の左上 `2 x 2` 領域に対応する。magic stateは [magic-state cultivation](https://arxiv.org/abs/2409.17595) で生成され、distillationはprogramに含まれると仮定する。）

- **拡張5：Clifford gate**

data node内のdataにlogical Hadamard gateとPhase gateも実行できる。
logical Hadamard gateは0 clock cycleで実行され、後続する全命令のboundary orientationを交換する。元のorientationへ戻すには、2 clock cycleを要する `ROTATION` が必要である。命令形式は次のとおりである。
```
HADAMARD 3
```
本質的には、後続命令のboundary typeをすべて反転することで、HADAMARD命令をすべて除去できる。

logical X-phase gateとZ-phase gateは、それぞれX軸、Z軸まわりのpi/4回転に対応し、1 clock cycleで実行できる。[Hirai et al.](https://arxiv.org/abs/2604.13632) の手法を仮定する。`ROTATION` と同様に、この命令は隣接blockを一時占有する。命令は、そのblockがdata nodeの水平方向または垂直方向のどちらに隣接すべきかを指定する。形式は次のとおりである。
```
PHASE 3 H
```



## Lattice Surgeryに関する既知の論文

lattice-surgery optimizationはNP-hardなのでheuristic解法が必要である。
https://arxiv.org/abs/1702.00591

architectureを十分に固定すると、問題をNP-hardなquadratic assignment problemへ帰着し、solverによるbrute forceで解ける。
https://arxiv.org/abs/1805.11127

完全なlattice-surgery-based computerの理論に関する著名なreviewがほぼ同時期に2本発表されている。
https://arxiv.org/abs/1808.06709
https://arxiv.org/abs/1808.02892

後者の *Game of Surface Codes* は体系的で広く読まれている。これら2論文はlattice surgery以外のoperation実装のcatalogとしてよく参照される。*Game of Surface Codes* の後半ではPauli-based computation frameworkによってcompilationを単純化する方法を説明している。Pauli-based computationを最初に導入した論文は次である。
https://arxiv.org/abs/1506.01396

*Game of Surface Codes* は、ancillary spaceを拡大すればoverheadを気にせずparallelismを高められると述べている。この考えが最初に現れた論文は次である。
https://arxiv.org/abs/1210.4626

lattice surgeryをcompileする既存softwareには次がある。

- OpenSurgery: https://github.com/alexandrupaler/opensurgery
- LatticeSurgeryCompiler: https://github.com/latticesurgery-com/lattice-surgery-compiler

次の論文はtime-axis optimizationを詳しく論じる。ここで使われる手法はFigure 6(a)のlong-range Bell measurementである。この論文は体系的で、問題の一部を切り分けて最適化する。またmagic-state consumptionの最大化がbipartite graph上のmaximum-matching問題へ帰着できることも示す。
https://arxiv.org/abs/2110.11493

次の論文はqubitを2.5次元に配置する方法を論じる。
https://arxiv.org/abs/2009.01982

logical T gateほど高コストではないが、surface codeにおけるlogical Y measurementとlogical S gateも相当に時間がかかる。twistを使う実装と使わない実装の両方が研究されている。
https://arxiv.org/abs/2109.02746
https://arxiv.org/abs/2201.05678

具体的algorithmに対するheuristic optimizationの例として、次の研究はlattice surgery以前の主要手法であるdefect braidingを用いたchemistry applicationを最適化した。Figure 25に最適化結果、Table VIIIにparameterが示されるが、再現には情報が不足しておりsource codeも公開されていない。
https://arxiv.org/abs/1805.03662

次の後続論文はlattice surgeryを使用する。Figure 10にlogical-qubit placementが示され、最適化を行ったと記載されているが、詳細不足のため再現は困難である。
https://arxiv.org/abs/2011.03494

この論文を理解するには、その基礎となる次の研究を読む必要がある。
https://arxiv.org/abs/1610.06546

次の論文はcondensed-matter physicsの具体的applicationに対する最適化例を示す。
https://arxiv.org/abs/2210.14109
