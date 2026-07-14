# 2D Routing Problem

## Background

In the most standard fault-tolerant quantum-computing architecture, qubits are encoded with surface codes, which constitute a square block of two-dimensional array of qubits. The operations on multiple surface-code qubits are implemented using lattice surgery, which routes the relevant logical qubits through two-dimensional space using un-used surface-code blocks. To accelerate the operations, optimizing the routing sequence can therefore increase instruction-level parallelism and minimize algorithm execution time, which can be rephrased as a kind of 3D-variant Tetris. The aim of this document is to describe the rule of basic lattice surgery routing.

## Lattice-surgery

Consider a subset of two-dimensional grid of node `(x_1, y_1), (x_2, y_2), ... (x_v, y_v)`. Some pairs of neiboging nodes (i.e., `(x_i, y_i), (x_j, y_j)` such that `|x_i-x_j| + |y_i-y_j| = 1`) are connected by edges `(i,j) \in E`. We choose `n` nodes among `v` nodes and encode `n` qubit data into them. We say nodes with data are data nodes, and those without data are empty nodes. A lattice surgery instruction can be executed by choosing a tree graph that connects target target data nodes using empty nodes, i.e., Steiner tree.
 
Suppose there are two-dimensional grids with 24 nodes `1 <= x_i <= 8' and '1 <= y_i <= 3` and `n=4` data nodes are located at `(1,1), (2,1), (5,3), (7,2)`. This situation can be visualized with the following schematic, where an integer indicates the data node with the corresponding index, and `.` indicates empty node.
```
. . . . . . . .

. 1 2 . . . 4 .

. . . . 3 . . .
```

Lattice surgery is an instruction that demands connecting multiple data nodes with a tree of empty nodes with specific boundaries. For example, `LATTICE_SURGERY [2 4] [V H]` requests conencting 2nd and 4th data node with vertical (up or down) and horizontal (left or right) boundaries, respectively. Since there are two vertical edges and two horizontal edges, we can choose preferrable ones from them. One possible implementation of an instruction that connects qubit 2 vertically and qubit 4 horizontally is as follows, where `*` are empty nodes temporally used for this operation, and `-` and `|` are used edges.
```
. . *.*-*-*-. . .
    |     |
. 1 2 . . *-4 .

. . . . 3 . . .
```

A way of implementing the lattice surgery is not unique. The same instruction can also be executed as follows.
Note that the latency of lattice surgery is constant and independent of the size of the tree. 
```
. . . . . *-*-*
          |   |
. 1 2 *-*-* 4-*
    | |
. . *-* 3 . . .
```

Lattice sugery might act on more than two data nodes. An example is `LATTICE_SURGERY [1 3 4] [H H H]`. An example implementation of this instruction is as follows.
```
. . . . . . . .
               
*-1 2 *-*-*-4 .
|     |
*-*-*-*-3 . . .
```


### Rules for instructions
We show a list of rules using the example of `LATTICE_SURGERY [1 3 4] [H H H]`.
The chosen routing graph can be represented by a set of edges contained in the graph.
Each routing graph assigned for instructions must satisfy the following rule.

- **Rule 1. routing graph must be a tree**

The following is invalid as it contains loop around `(4,1),(5,1),(5,2),(4,2)`
```
. . . *-* . . .
      | |       
*-1 2 *-*-*-4 .
|     |
*-*-*-*-3 . . .
```

The following is invalid as it contains loop including data node 3.
```
. . . . . . . .
               
*-1 2 *-*-*-4 .
|     |   |
*-*-*-*-3-* . .
```

The following is invalid as this edgeset is disconnected.
```
. . . . . . . .
                 
*-1 2-*-*-*-4 .
|      
*-*-*-*-3 . . .
```

- **Rule 2. Every target node must be a leaf of a routing graph**

The following is invalid as target data node 3 is not connected.
```
. . . . . . . .
               
*-1 2 *-*-*-4 .
|     |
*-*-*-* 3 . . .
```

The following is invalid as data node 3 is not a leaf of a tree.
```
. . . . . . . .
               
*-1 2 . . *-4 .
|         |
*-*-*-*-3-* . .
```

- **Rule 3. Each leaf of a tree must be a node**

The following is invalid as a tree is terminated at empty node `(4,1)`
```
. . . * . . . .
      |         
*-1 2 *-*-*-4 .
|     |
*-*-*-*-3 . . .
```

- **Rule 4. all the non-target nodes must not be connected**

The following is invalid as non-target data node 2 is connected
```
. . . . . . . .
               
*-1 2-*-*-*-4 .
|     |
*-*-*-*-3 . . .
```

- **Rule 5. all the data node must be touched from appropriate direction**

The following is invalid as target data node 3 is connected vertically
```
. . . . . . . .
               
*-1 2 *-*-*-4 .
|     | |
*-*-*-* 3 * . .
```

Briefly saying, the condition is that `each routing graph must be a Steiner tree that is terminated at the appopriate boundaries of data nodes and that does not contain non-target data nodes.`

### Parallel execution

Executing a lattice-surgery instruction takes one unit of time, and temporally used empty nodes will be released after execution.
Task will be provided as a sequence of lattice surgery instruction, and our mission is to minimize the execution time.
To this end, we would like to maximumze the instruction throughput by executing them in parallel as far as possible.

Suppose there are two instructions.
```
1: LATTICE_SURGERY [1 3] [H H]
2: LATTICE_SURGERY [2 4] [V H]
3: LATTICE_SURGERY [2 3] [H H]
```
A possible solution for each of them as follows
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

Then, the first and last routes can be executed in parallel.
```
T=1
. . *-*-*-* . .
    |     |     
*-1 2 . . *-4 .
|        
*-*-*-*-3 . . .
```

After finishing the first two instructions, we can perform the third instruction at T=2.
```
. . . . . . . .
                
. 1 2-* . . 4 .
      |  
. . . *-3 . . .
```

For provided `m` instructions, we need to find a sequence of trees to minimize the time to finish all the instructions.

### Rules in parallel execution
We show a list of rules using concrete examples.

- **Parallel rule 1. Routing trees must not share any empty node**

The following two cannot be executed in parallel as they share empty node at `(4,2)`
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

- **Parallel rule 2. Routing trees must not share data cell with different types of boundaries**

The following two cannot be executed in parallel as they share data node with different directions.
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

Note that sharing a certain data node with the same boundary types is allowed. The following two instructions can be executed in parallel.
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
The input is written in the following form.
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
q_{2,1} q_{2,2} ... q_{2,t_1}
p_{2,1} p_{2,2} ... p_{2,t_1}
...
t_m
q_{m,1} q_{m,2} ... q_{m,t_1}
p_{m,1} p_{m,2} ... p_{m,t_1}
```

Here, `v`, `e`, `n` and `m` are positive integers, which corresponds to the number of nodes, edges, data nodes, and instructions. `x_i` and `y_i` are a X- and Y- cordinate of the i-th node.
`w_{i,1}` and `w_{i,2}` indicates i-th edge connects the `w_{i,1}`-th and `w_{i,2}`-th nodes and satisfy `1 <= w_{i,1}, w_{i,2} <= v`.
`t_i` is the number of target data cells for i-th lattice surgery instructions and satisfy `2 <= t_i <= n`.
`q_{i,j}` is the index of j-th target data cell for i-th lattice-surgery instruction and satisfy `1 <= q_{i,j} <= n`. Each data node appears at most once at the operand of each instruction, i.e., if `j \neq j'` then `q_{i,j} \neq q_{i,j'}`.
`p_{i,j}` is the boundary of j-th target data cell for i-th lattice-surgery instruction and satisfy `p_{i,j} \in {H,V}`.


### Output
The output must be writte in the following form.
```
P_1 P_2 ... P_n
T_1 R_1 E_{1,1} E_{1,2} ... E_{1,R_1}
T_2 R_2 E_{2,1} E_{2,2} ... E_{2,R_2}
...
T_m R_m E_{m,1} E_{m,2} ... E_{m,R_m}
```

Here, `P_i` is the node of i-th qubit is located and must satisfy `1 <= P_i <= v`. As qubit are located in different place, if `i \neq i'` then `P_i \neq P_i'`.
`T_i` is the clock time of i-th lattice-surgery instruction will be executed and must satisfy `1 <= T_i` (the first clock time is 1). If `i < j` then `T_i <= T_j`.
`R_i` is the number of edges used for a routing tree of i-th lattice-surgery instruction and must satisfy `1 <= R_i <= e`.
`E_{i,j}` is the j-th edge included in the routing tree for the i-th lattice surgery instruction. As each edge can appear at most one time in a tree, if `j \neq j'` then `E_{i,j} \neq E_{i,j'}`. 

Each tree must satisfy all the Rules and Parallel Rules described the above. Trees that are executed at the same time must satisfy the rule 9,10 described the above. Our aim is to minimize `T_m`.


### Problem size
`v` and `n` must be at least 50 for the advantage of quantum computing, and 10,000 would be enough for most applications.
`m` would at least about 1,000 for the advantage of quantum computing, and at most 10^15 for meaningful applications.


## Problem simplification
The above definition is complicated, we can typically simplify the problem as follows. The following conditions are not necessarily assumed, but some papers employ them for simplifying the problem and focusing on the optimization.

- **Assumption 1: grid field**

Most architecture focuses on a case where nodes are located inside a certain rectangle region, and we can typically assume all the nearest-neighboring cells are connected by edges.
In such case, we can specify the `x_i, y_i, w_{i,j}` with two integers `w,h` instead of a list of node locations. For example `w=3, h=2` meas
```
6 7 n m
1 1
1 2
1 3
2 1
2 2
2 3
1 2
1 4
2 3
2 5
3 6
4 5
5 6
```


- **Assumption 2: fixed layouts**

We are typically requested to determine qubit placement, i.e., data node index to node index.
However, finding the best placement and finding the best routing is correlated and is difficult to solve at the same time.
To simplify the problem and focus on the routing problem only, we sometimes assume a fixed qubit layout.

While we want to compactly place data qubits, we also need to connect at least one of horizontal and vertical boundaries, 
With this reason, the following layouts are popular choices.
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
. 3 4 . 6 8 .
. . . . . . .
. 9 a . d e .
. b c . f g .
. . . . . . . 
```

While routing becomes trivial, the best known density letting each node expose one horizontal and vertical boundary as follows.
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

Several popular compliation schemes only generate lattice surgery instructions with two target qubit `t_i=2`.
One promising way to determine each lattice sugery tree is to assign the shortest tree in a greedy manner.
This is equal to minimum Steiner tree problem and known to be NP-hard, and we need to use approximated algorithms.
If we can assume `t_i=2`, this problem becomes shortest path finding, which can be solved with a polynomial time.


- **Assumption 4: same boundary**

Several popular compliation schemes only generate lattice surgery instructions toucing the same types of boundaries, i.e., `p_{i,1} = p_{i,2} = ... p_{i,R_i}`
As the direction of boundaries are not essential for solving the routing problems, this simplifies the solver and allows us to focus on the routing problem.


## Problem extension

The following extensions are theoretically available, while problem definitions become complicated.

- **Extention 1: Rotation**

Every data cell can perform ROTATION instruction, which rotates the orientation of qubits with 90 degrees.
This operation consumes any empty node connected to the data node, and take two clock time.
After the operation, all the boundary types of all the following instructions will be flipped as V<->H.
Suppose the following instructions.
```
LATTICE_SUGERY [1,2] [H H]
LATTICE_SUGERY [1,2] [V V]
LATTICE_SUGERY [1,2] [H H]

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
LATTICE_SUGERY [1,2] [H H]
ROTATION 1 U
LATTICE_SUGERY [1,2] [H V]
LATTICE_SUGERY [1,2] [V H]

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



- **Extention 2: Moving logical qubit**

We are allowed to insert MOVE instruction, which changes the position of data node from a certain node to another.
MOVE instruction takes one clocks and consumes empty nodes on a path between original and target nodes.
If the boundary type of connecting paths to original and target nodes are different, the boundary types of the following operations are flipped V<->H.

```
LATTICE_SUGERY [1,2] [H H]
MOVE 1 [(2,2), (1,2)]
LATTICE_SUGERY [1,2] [V V]
LATTICE_SUGERY [1,2] [H H]

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
LATTICE_SUGERY [1,2] [H H]
MOVE 1 [(2,2), (1,1)]
LATTICE_SUGERY [1,2] [H V]
LATTICE_SUGERY [1,2] [V H]

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

- **Extention 3: Reordering lattice surgery instruction**

We are allowed to reorder the sequence of quantum operations.
This can be achieved if the following conditions are satisfied for the consecutive instructions.

1. Let Q be a subset of data nodes that both two lattice surgery operations act on.
2. Let T be the number of the data nodes in Q that are accessed through different types of faces, namely H and V.
3. If and only if the number of T is even, their order can be swapped without changing the behavior.

- `LATTICE_SUGERY [0 1] [H H]` and `LATTICE_SUGERY [2 3] [H H]` can be reordered as they do not have overlapping targets.
- `LATTICE_SUGERY [0 1] [H H]` and `LATTICE_SUGERY [1 2] [H H]` can be reordered as they share data node 1 but access with the same boundary.
- `LATTICE_SUGERY [0 1] [H H]` and `LATTICE_SUGERY [1 2] [V H]` cannot be reordered as they share data node 1 and access with the different boundary.
- `LATTICE_SUGERY [0 1] [H H]` and `LATTICE_SUGERY [0 1] [V V]` can be reordered as they share data node 1 and access with the different boundary twice.

When we allow reordering, we can quickly check whether a certain instruction is ready for execution by creating a dependency graph in advance.
A denepdency graph is a directional graph where each node corresponds to an instruction, and edge connects nodes A to B if the instruction B must be executed after instruction A.
Once we create this graph, we can judge whether we can execute the instruction A by checking all the parents of instruction A are finished.

- **Extention 4: Magic states**

In practice, we sometimes needs to use magic-state to achieve a universal fault-tolerant quantum computation.
We can anytime allocate or deallocate magic-state factory at a certain position. Once we allocate magic-state factory, we cannot use that node for lattice surgery.
For simplicity, we assume magic-state factories consumes 2x2 connected regions of node network.
Once allocated, that node can repeat trials to generate a resource called magic state. This trial can be executed in each clock time and succeeds with a certain probability `p`.

Each lattice surgery instruction has additional argument `M \in [0,1]`. If `M=1`, this must be connected to magic states. The boundary to connect magic-state factory is arbitrary.
Once we connect it to magic-state factory, we need to temporally allocate additional node neighboring to the magic-state node. This node will be removed after `R` clock time.
The value `p` and `R` are constant and given as a problem.

```
R=3
p=0.1
LATTICE_SUGERY [0 1] [H H] 1

T=1 create magic state factory at 2x2 region of (6,1),(6,2),(7,1),(7,2).
Since this instrution consumes a magic state, we need to wait for successful generation.
. . . . . M M

. 0 . 1 . M M

. . . . . . .


T=7, suppose that magic-factory succeeds magic-state generation
. . . . . M M

. 0 . 1 . M M

. . . . . . .

T=8, suppose that magic-factory succeeds magic-state generation
. . *-*-*-M M
    |
. 0-*-1 . M M

. . . . . . .
```

Actual magic-state generation procedure is complicated. Please see [A game of surface codes](https://arxiv.org/pdf/1808.02892) for more details.
(Technically saying, the above definition uses Auto-corrected pi/8 rotation in Fig.17, and 2x2 block corresponds to left top 2x2 region in Fig.17(c) step 2. We assume magic-state is generated by [magic-state cultivation](https://arxiv.org/abs/2409.17595), and its distillation is included in a program.)

- **Extention 5: Clifford gates**

We can also execute logical Hadamard and Phase gates to the data in a data node.
We can execute logical Hadamard gates with zero time-clock, and all the boundaries of the following instructions will be fliped. If we want to let them back to the original boundary, we need to perform ROTATION, which takes two clock time. An instruction form is as follows. 
```
HADAMARD 3
```
Essentially, we can remove all the HADAMARD instruction by flipping the boundary type for all the subsequent instructions.

We can execute logical X-Phase and Z-Phase gate (corresponding to pi/4 rotation with X- and Z-axis) with a single-time clock. We assume method by [Hirai et al](https://arxiv.org/abs/2604.13632) and it takes one clock time. This instruction temporally dominates a neighboring block like ROTATION, but the additional node must be neighboring to the data node with the horizontal or vertically connected, which will be specified by the instruction. A form of instruction is 
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
