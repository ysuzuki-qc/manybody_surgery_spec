# 2D Routing Problem

## Background

In the most common fault-tolerant quantum-computing architecture, qubits are encoded using surface codes, each of which occupies a square block in a two-dimensional array of physical qubits. Operations involving multiple surface-code qubits are implemented using lattice surgery, which connects the relevant logical qubits through two-dimensional space using unused surface-code blocks. Optimizing these routes can increase instruction-level parallelism and reduce the overall execution time of an algorithm. The resulting optimization problem can be viewed as a three-dimensional variant of Tetris. This document describes the basic rules of lattice-surgery routing.

## Lattice Surgery

Consider a subset of a two-dimensional grid consisting of nodes `(x_1, y_1), (x_2, y_2), ... (x_v, y_v)`. Some pairs of neighboring nodes—namely, `(x_i, y_i)` and `(x_j, y_j)` such that `|x_i-x_j| + |y_i-y_j| = 1`—are connected by edges `(i,j) \in E`. We choose `n` of the `v` nodes to hold `n` data qubits. Nodes that hold data qubits are called data nodes, and the remaining nodes are called empty nodes. A lattice-surgery instruction can be executed by selecting a tree that has all the operand data nodes as leaves (node with one edge) and empty nodes as branches (node with more than one edges); that is, by selecting a Steiner tree.
 
Suppose a two-dimensional grid has 24 nodes satisfying `1 <= x_i <= 8` and `1 <= y_i <= 3`, and `n=4` data nodes are located at `(2,2)`, `(3,2)`, `(5,3)`, and `(7,2)`. The following schematic illustrates this arrangement. Each integer denotes the data node with that index, and `.` denotes an empty node.
```
. . . . . . . .

. 1 2 . . . 4 .

. . . . 3 . . .
```

A lattice-surgery instruction requires multiple data nodes to be connected by a tree of empty nodes through specified boundaries. For example, `LATTICE_SURGERY [2 4] [V H]` requests a connection to the second data node through a vertical boundary (above or below) and to the fourth data node through a horizontal boundary (left or right). Because each data node has two boundaries of each specified orientation, either suitable boundary may be selected. One possible implementation is shown below, where `*` denotes an empty node temporarily used by the operation, and `-` and `|` denote the edges used.
```
. . *-*-*-* . . .
    |     |
. 1 2 . . *-4 .

. . . . 3 . . .
```

The implementation of a lattice-surgery instruction is not unique. The same instruction can also be executed as follows. Note that the latency of lattice surgery is constant and independent of the size of the tree.
```
. . . . . *-*-*
          |   |
. 1 2 *-*-* 4-*
    | |
. . *-* 3 . . .
```

Lattice surgery may act on more than two data nodes. For example, `LATTICE_SURGERY [1 3 4] [H H H]` can be implemented as follows.
```
. . . . . . . .
               
*-1 2 *-*-*-4 .
|     |
*-*-*-*-3 . . .
```


### Rules for Instructions

The following rules are illustrated using `LATTICE_SURGERY [1 3 4] [H H H]`. A selected routing graph can be represented by its set of edges. Every routing graph assigned to an instruction must satisfy the following rules.

- **Rule 1. The routing graph must be a tree.**

The following graph is invalid because it contains a cycle through `(4,1)`, `(5,1)`, `(5,2)`, and `(4,2)`.
```
. . . *-* . . .
      | |       
*-1 2 *-*-*-4 .
|     |
*-*-*-*-3 . . .
```

The following graph is invalid because it contains a cycle through data node 3.
```
. . . . . . . .
               
*-1 2 *-*-*-4 .
|     |   |
*-*-*-*-3-* . .
```

The following graph is invalid because its edge set is disconnected.
```
. . . . . . . .
                 
*-1 2-*-*-*-4 .
|      
*-*-*-*-3 . . .
```

- **Rule 2. Every operand node must be a leaf of the routing graph.**

The following graph is invalid because operand data node 3 is not connected.
```
. . . . . . . .
               
*-1 2 *-*-*-4 .
|     |
*-*-*-* 3 . . .
```

The following graph is invalid because data node 3 is not a leaf of the tree.
```
. . . . . . . .
               
*-1 2 . . *-4 .
|         |
*-*-*-*-3-* . .
```

- **Rule 3. Every leaf of the tree must be a data node.**

The following graph is invalid because the tree terminates at the empty node `(4,1)`.
```
. . . * . . . .
      |         
*-1 2 *-*-*-4 .
|     |
*-*-*-*-3 . . .
```

- **Rule 4. No non-operand data node may be connected.**

The following graph is invalid because non-operand data node 2 is connected.
```
. . . . . . . .
               
*-1 2-*-*-*-4 .
|     |
*-*-*-*-3 . . .
```

- **Rule 5. Every operand data node must be approached from the specified direction.**

The following graph is invalid because operand data node 3 is connected vertically.
```
. . . . . . . .
               
*-1 2 *-*-*-4 .
|     | |
*-*-*-* 3 * . .
```

In short, `each routing graph must be a Steiner tree whose leaves terminate at the specified boundaries of the operand data nodes and that contains no non-operand data nodes.`

### Parallel Execution

Executing a lattice-surgery instruction takes one unit of time, and the empty nodes used temporarily by the instruction are released afterward. A task is provided as a sequence of lattice-surgery instructions, and the objective is to minimize the total execution time. To this end, we maximize instruction throughput by executing as many instructions in parallel as possible.

Suppose there are three instructions.
```
1: LATTICE_SURGERY [1 3] [H H]
2: LATTICE_SURGERY [2 4] [V H]
3: LATTICE_SURGERY [2 3] [H H]
```
A possible route for each instruction is shown below.
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

The first and second routes can then be executed in parallel.
```
T=1
. . *-*-*-* . .
    |     |     
*-1 2 . . *-4 .
|        
*-*-*-*-3 . . .
```

After the first two instructions finish, the third instruction can be executed at `T=2`.
```
. . . . . . . .
                
. 1 2-* . . 4 .
      |  
. . . *-3 . . .
```

For a given set of `m` instructions, we must find routing trees and a schedule that minimize the time required to complete all instructions.

### Rules for Parallel Execution

The following rules are illustrated with concrete examples.

- **Parallel Rule 1. Routing trees must not share any empty node at the same time**

The following two instructions cannot be executed in parallel because their trees share the empty node at `(4,2)`.
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

- **Parallel Rule 2. Routing trees must not share a data node through boundaries of different orientations at the same time**

The following two instructions cannot be executed in parallel because they approach a shared data node from different directions.
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

Sharing a data node through boundaries of the same orientation is allowed. Therefore, the following two instructions can be executed in parallel.
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


## Input and Output

### Input
The input has the following format.
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

Here, `v`, `e`, `n`, and `m` are positive integers denoting the numbers of nodes, edges, data nodes, and instructions, respectively. `x_i` and `y_i` are the x- and y-coordinates of the `i`-th node.
`w_{i,1}` and `w_{i,2}` indicate that the `i`-th edge connects nodes `w_{i,1}` and `w_{i,2}`, where `1 <= w_{i,1}, w_{i,2} <= v`.
`t_i` is the number of operand data nodes in the `i`-th lattice-surgery instruction and satisfies `2 <= t_i <= n`.
`q_{i,j}` is the index of the `j`-th operand data node in the `i`-th lattice-surgery instruction and satisfies `1 <= q_{i,j} <= n`. Each data node appears at most once among the operands of an instruction; that is, if `j \neq j'`, then `q_{i,j} \neq q_{i,j'}`.
`p_{i,j}` specifies the boundary orientation of the `j`-th operand data node in the `i`-th lattice-surgery instruction and satisfies `p_{i,j} \in {H,V}`.


### Output
The output must have the following format.
```
P_1 P_2 ... P_n
T_1 R_1 E_{1,1} E_{1,2} ... E_{1,R_1}
T_2 R_2 E_{2,1} E_{2,2} ... E_{2,R_2}
...
T_m R_m E_{m,1} E_{m,2} ... E_{m,R_m}
```

Here, `P_i` is the node at which the `i`-th qubit is located and must satisfy `1 <= P_i <= v`. Because different qubits occupy different nodes, if `i \neq i'`, then `P_i \neq P_i'`.
`T_i` is the clock cycle in which the `i`-th lattice-surgery instruction is executed and must satisfy `1 <= T_i` (the first clock cycle is 1). If `i < j`, then `T_i <= T_j`.
`R_i` is the number of edges in the routing tree for the `i`-th lattice-surgery instruction and must satisfy `1 <= R_i <= e`.
`E_{i,j}` is the `j`-th edge in the routing tree for the `i`-th lattice-surgery instruction and must satisfy `1 <= E_{i,j} <= e`. Each edge may appear at most once in a tree; thus, if `j \neq j'`, then `E_{i,j} \neq E_{i,j'}`.

Each tree must satisfy all Rules and Parallel Rules described above. Trees executed at the same time must satisfy both Parallel Rules. The objective is to minimize `T_m`.


### Problem size
To demonstrate a quantum-computing advantage, `v` and `n` should be at least 50; values up to 10,000 should be sufficient for most applications.
Similarly, `m` should be at least approximately 1,000 and at most `10^15` for applications of practical interest.


## Problem simplification
The definition above is complex, so the problem is often simplified using the assumptions below. These assumptions are optional, but some papers use them to isolate the optimization problem.

- **Assumption 1: rectangular grid**

Most architectures place nodes in a rectangular region, with edges connecting all nearest-neighbor pairs. In this case, the coordinates `x_i, y_i` and edges `w_{i,j}` can be specified by two integers, `w` and `h`, rather than by explicit lists of nodes and edges. For example, `w=3, h=2` means
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


- **Assumption 2: fixed layouts**

We are typically required to determine the qubit placement; that is, the mapping from data-qubit indices to node indices. However, placement and routing are interdependent and difficult to optimize simultaneously. To focus exclusively on routing, we sometimes assume a fixed qubit layout.

Although data qubits should be placed compactly, at least one horizontal and one vertical boundary of each data qubit must remain accessible. For this reason, the following layouts are popular choices.
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

The densest known layout in which every data node exposes both a horizontal and a vertical boundary is shown below, although routing then becomes highly constrained.
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

If we are allowed to use ROTATION and MOVE operations (see extension section), we can choose more compact layouts as follows.
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


- **Assumption 3: two-body measurement**

Several popular compilation schemes generate only lattice-surgery instructions with two operand qubits (`t_i=2`). One promising approach is to greedily assign a shortest tree to each instruction. In general, this is the minimum Steiner tree problem, which is NP-hard and therefore requires approximation algorithms. When `t_i=2`, however, it reduces to a shortest-path problem that can be solved in polynomial time.


- **Assumption 4: same boundary**

Several popular compilation schemes generate only lattice-surgery instructions that touch boundaries of the same orientation; that is, `p_{i,1} = p_{i,2} = ... = p_{i,t_i}`. Because boundary orientation is not essential to the core routing problem, this assumption simplifies the solver.


## Problem extension

The following extensions are theoretically possible, although they make the problem definition more complex.

- **Extension 1: Rotation**

Every data node can execute a `ROTATION` instruction, which rotates the qubit orientation by 90 degrees. This operation occupies an empty node adjacent to the data node and takes two clock cycles. Afterward, the boundary orientations in all subsequent instructions are exchanged (`V <-> H`). Consider the following instructions.
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
We can insert ROTATION instructions at T=2.
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



- **Extension 2: Moving a logical qubit**

We may insert a `MOVE` instruction, which moves a data qubit from one node to another. A `MOVE` instruction takes one clock cycle and occupies the empty nodes along a path between the original and destination nodes. If the path connects to the original and destination nodes through boundaries of different orientations, the boundary orientations of subsequent operations are exchanged (`V <-> H`).

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

- **Extension 3: Reordering lattice-surgery instructions**

We may reorder a sequence of quantum operations when two consecutive instructions satisfy the following conditions.

1. Let `Q` be the set of data nodes on which both lattice-surgery operations act.
2. Let `T` be the number of data nodes in `Q` that the two operations access through different boundary orientations (`H` and `V`).
3. The operations can be swapped without changing their behavior if and only if `T` is even.

- `LATTICE_SURGERY [0 1] [H H]` and `LATTICE_SURGERY [2 3] [H H]` can be reordered because they have no overlapping operand data nodes.
- `LATTICE_SURGERY [0 1] [H H]` and `LATTICE_SURGERY [1 2] [H H]` can be reordered because they access their shared data node, node 1, through the same boundary orientation.
- `LATTICE_SURGERY [0 1] [H H]` and `LATTICE_SURGERY [1 2] [V H]` cannot be reordered because they access their shared data node, node 1, through different boundary orientations.
- `LATTICE_SURGERY [0 1] [H H]` and `LATTICE_SURGERY [0 1] [V V]` can be reordered because they access shared data nodes through different boundary orientations twice.

When we allow reordering, we can quickly check whether a certain instruction is ready for execution by creating a dependency graph in advance.
A dependency graph is a directed graph in which each node represents an instruction and an edge from `A` to `B` indicates that instruction `B` must be executed after instruction `A`. Once this graph has been constructed, an instruction is ready to execute if all its predecessors have finished.

- **Extension 4: Magic states**

In practice, magic states are needed for universal fault-tolerant quantum computation. A magic-state factory may be allocated or deallocated at a chosen location. While a factory is allocated, its nodes cannot be used for lattice surgery. For simplicity, we assume that each factory occupies a connected `2 x 2` region of the node network. Once allocated, a factory can attempt to generate a magic state during every clock cycle, with success probability `p` per attempt.

Each lattice-surgery instruction has an additional argument `M \in {0,1}`. If `M=1`, the instruction must be connected to a magic-state factory; the factory boundary used for this connection is unrestricted. Once the connection is made, an additional node adjacent to the magic-state node must be allocated temporarily. This allocation is released after `R` clock cycles. The constants `p` and `R` are given as part of the problem.

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

Actual magic-state generation procedure is complicated. Please see [A game of surface codes](https://arxiv.org/pdf/1808.02892) for more details.
(More precisely, the definition above uses the autocorrected pi/8 rotation in Fig. 17, and the `2 x 2` block corresponds to the upper-left `2 x 2` region in step 2 of Fig. 17(c). We assume that magic states are generated by [magic-state cultivation](https://arxiv.org/abs/2409.17595) and that distillation is included in the program.)

- **Extension 5: Clifford gates**

We can also execute logical Hadamard and Phase gates to the data in a data node.
Logical Hadamard gates take zero clock cycles, and they exchange the boundary orientations of all subsequent instructions. Restoring the original orientations requires a `ROTATION`, which takes two clock cycles. The instruction format is
```
HADAMARD 3
```
Essentially, we can remove all the HADAMARD instruction by flipping the boundary type for all the subsequent instructions.

Logical X-phase and Z-phase gates, corresponding to pi/4 rotations about the X and Z axes, can be executed in one clock cycle. We assume the method of [Hirai et al.](https://arxiv.org/abs/2604.13632). Like `ROTATION`, this instruction temporarily occupies an adjacent block. The instruction specifies whether that block must be horizontally or vertically adjacent to the data node. Its format is
```
PHASE 3 H
```



## Known Papers on Lattice Surgery

Lattice-surgery optimization is NP-hard, so heuristic solutions are required.
https://arxiv.org/abs/1702.00591

With a sufficiently fixed architecture, the problem can be reduced to the NP-hard quadratic assignment problem and solved by brute force using a solver.
https://arxiv.org/abs/1805.11127

Two well-known reviews on the theory of complete lattice-surgery-based computers appeared at approximately the same time:
https://arxiv.org/abs/1808.06709
https://arxiv.org/abs/1808.02892

The latter, *Game of Surface Codes*, is systematic and widely read. These two papers are often referenced for catalogs of implementations of operations other than lattice surgery. The second half of *Game of Surface Codes* describes a way to simplify compilation using the Pauli-based computation framework. Pauli-based computation was first introduced in:
https://arxiv.org/abs/1506.01396

*Game of Surface Codes* notes that parallelism can be increased by enlarging the ancillary space without concern for overhead. This idea first appeared in:
https://arxiv.org/abs/1210.4626

Existing software for compiling lattice surgery includes:

- OpenSurgery: https://github.com/alexandrupaler/opensurgery
- LatticeSurgeryCompiler: https://github.com/latticesurgery-com/lattice-surgery-compiler

The following paper discusses time-axis optimization in detail. The technique used here is the long-range Bell measurement in Figure 6(a). The paper is systematic and isolates portions of the problem for optimization. It also shows that maximizing magic-state consumption can be reduced to a maximum-matching problem on a bipartite graph.
https://arxiv.org/abs/2110.11493

The following paper discusses arranging qubits in 2.5 dimensions:
https://arxiv.org/abs/2009.01982

Although not as costly as logical T gates, logical Y measurements and logical S gates are also quite time-consuming in the surface code. Implementations both with and without twists have been investigated:
https://arxiv.org/abs/2109.02746
https://arxiv.org/abs/2201.05678

As an example claiming heuristic optimization for a concrete algorithm, the following work optimized a chemistry application using defect braiding, the dominant technique before lattice surgery. Figure 25 shows the optimization result and Table VIII lists its parameters, but even this information is insufficient for reproduction. The source code is not public.
https://arxiv.org/abs/1805.03662

The following subsequent paper uses lattice surgery. Figure 10 shows the logical-qubit placement, and the paper states that optimization was performed, but the lack of details makes reproduction difficult.
https://arxiv.org/abs/2011.03494

Understanding that paper requires reading the following work on which it is based:
https://arxiv.org/abs/1610.06546

The following paper provides an optimization example for a concrete application in condensed-matter physics:
https://arxiv.org/abs/2210.14109
