# Lattice Surgery Schedule Optimization

## Background

In the most standard fault-tolerant quantum-computing architecture, qubits are encoded with surface codes, which constitute a square block of two-dimensional array of qubits. The operations on multiple surface-code qubits are implemented using lattice surgery, which routes the relevant logical qubits through two-dimensional space using un-used surface-code blocks. To accelerate the operations, optimizing the routing sequence can therefore increase instruction-level parallelism and minimize algorithm execution time, which can be rephrased as a kind of 3D-variant Tetris. The aim of this document is to describe the rule of lattice surgery used in [K. Hamada et al., Efficient and high-performance routing of lattice-surgery paths on three-dimensional lattice](https://arxiv.org/abs/2401.15829) without using the words of quantum computing. 

## 2D Routing Problem

### Lattice-surgery rules

Consider a subset of two-dimensional grid of node `(x_1, y_1), (x_2, y_2), ... (x_v, y_v)`. Some pairs of nearest-neighboring nodes are connected by edges `(i,j) \in E` if `|x_i-x_j| + |y_i-y_j| = 1`.
 We choose `n` nodes among `v` nodes and place `n` data on them. We say nodes with data are data nodes, and those without data are empty nodes. A lattice surgery instruction can be rephrased as connecting multiple target data nodes using a path with empty nodes.
 
### Concrete example of lattice surgery

Suppose there are two-dimensional grids with 24 nodes `(1,1), ... (8,3)` and `n=4` data nodes are located. This situation can be visualized with the following schematic, where an integer `i` indicates the i-th data node, and `.` indicates empty node.

```
. . . . . . . .

. 1 2 . . . 4 .

. . . . 3 . . .
```

Lattice surgery is an instruction that demand connecting multiple data nodes with a tree of empty nodes with specific directions.
For example `LATTICE_SURGERY [2 4] [V H]` requests conencting 2nd and 4th data node with vertical and horizontal edges, respectively. Since there are two vertical edges and two horizontal edges, we can choose preferrable ones from them.
One possible implementation of an instruction that connects qubit 2 vertically and qubit 4 horizontally is as follows, where `*` are empty nodes temporally used for this operation, and `-` and `|` are used edges between nodes.
```
. . *.*-*-*-. . .
    |     |
. 1 2 . . *-4 .

. . . . 3 . . .
```

A way of implementing the lattice surgery is not unique. The same instruction can also be executed as follows:
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


### Rules for single instruction
Using the example of `LATTICE_SURGERY [1 3 4] [H H H]`, we show several invalid cases.

- Rule1. all the target nodes must be connected

The following is invalid as target data node 3 is not connected.
```
. . . . . . . .
               
*-1 2 *-*-*-4 .
|     |
*-*-*-* 3 . . .
```

- Rule2. all the non-target nodes must not be connected

The following is invalid as non-target data node 2 is connected
```
. . . . . . . .
               
*-1 2-*-*-*-4 .
|     |
*-*-*-*-3 . . .
```

- Rule3. all the target nodes must be connected only at once

The following is invalid as target data node 3 is connected twice
```
. . . . . . . .
               
*-1 2 *-*-*-4 .
|     |   |
*-*-*-*-3-* . .
```

- Rule4. all the data node must be touched from appropriate direction

The following is invalid as target data node 3 is connected vertically
```
. . . . . . . .
               
*-1 2 *-*-*-4 .
|     | |
*-*-*-* 3 * . .
```

- Rule5. the path must not contain any loop

The following is invalid as it contains loop around `(4,1),(5,1),(5,2),(4,2)`
```
. . . *-* . . .
      | |       
*-1 2 *-*-*-4 .
|     |
*-*-*-*-3 . . .
```

- Rule6. the path must be connected

The following is invalid as its path is fragmented to two.
```
. . . *-*-*-*-*
      |       |  
*-1 2 *-*-*-4-*
|      
*-*-*-*-3 . . .
```

- Rule7. Each leaf of path must be a node

The following is invalid as a path is terminated at `(4,1)`
```
. . . * . . . .
      |         
*-1 2 *-*-*-4 .
|     |
*-*-*-*-3 . . .
```

- Rule8. Each target node must be a leaf of a path.

The following is invalid as data node 3 is not a leaf of a path.
```
. . . . . . . .
               
*-1 2 . . *-4 .
|         |
*-*-*-*-3-* . .
```


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
. . . . . . . .
               
*-1 2 . . . 4 .
|          
*-*-*-*-3 . . .
```

```
. . *-*-*-* . .
    |     |     
. 1 2 . . *-4 .
         
. . . . 3 . . .
```

```
. . . . . . . .
                
. 1 2-* . . 4 .
      |  
. . . *-3 . . .
```

Then, the first and last path can be executed in parallel.
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

For provided `m` instructions, we need to find a sequence to paths to minimize the time to finish all the instructions.

### Rules in parallel execution

We will show several invalid cases with concrete examples.

- Rule9. Path must not share any empty node

The following two cannot be executed in parallel as they share empyt node at `(4,2)`
```
1: LATTICE_SURGERY [1 4] [V H]
. *-*-*. . . . .
  |   |        
. 1 2 *-*-*-4 .
   
. . . . 3 . . .

2: LATTICE_SURGERY [2 3] [H V]
. . . . . . . .
              
. 1 2-*-* . 4 .
        |
. . . . 3 . . .
```

- Rule10. Path must not share data cell with different types of boundaries

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

Note that sharing a certain data node with the same boundary types is allowed.
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

Here, `v`, `e`, `n` and `m` are positive integers, which corresponds to the number of nodes, edges, data nodes, and instructions.
`x_i` and `y_i` are a X- and Y- cordinate of the i-th node.
`w_{i,1}` and `w_{i,2}` indicates i-th edge connects the `w_{i,1}`-th and `w_{i,2}`-th nodes and satisfy `1 <= w_{i,1}, w_{i,2} <= v`.
`t_i` is the number of target data cells for i-th lattice surgery instructions and satisfy `2 <= t_i <= n`.
`q_{i,j}` is the index of j-th target data cell for i-th lattice-surgery instruction and satisfy `1 <= q_{i,j} <= n`. Each data node appears at most once at the operand of instructions, i.e., if `j \neq j'` then `q_{i,j} \neq q_{i,j'}`.
`p_{i,j}` is the boundary of j-th target data cell for i-th lattice-surgery instruction and satisfy `p_{i,j} \in {H,V}`.

### Output

The output must be writte in the following form.

```
P_1 P_2 ... P_n
T_1 R_1 E_{1,1} E_{1,2} ... E_{1,R_0}
T_2 R_2 E_{2,1} E_{2,2} ... E_{2,R_0}
...
T_m R_m E_{m,1} E_{m,2} ... E_{m,R_m}
```

Here, `P_i` is the node of i-th qubit is located and must satisfy `1 <= P_i <= n`. As qubit are located in different place, if `i \neq i'` then `P_i \neq P_i'`.
`T_i` is the clock time of i-th lattice-surgery instruction will be executed and must satisfy `1 <= T_i` (clock start from 1). If `i < j` then `T_i <= T_j`.
`R_i` is the number of edges used for a path of i-th lattice-surgery instruction and must satisfy `1 <= R_i <= e`.
`E_{i,j}` is the j-th edge included in the path for the i-th lattice surgery instruction. As each edge can appear at most one time in a path, if `j \neq j'` then `E_{i,j} \neq E_{i,j'}`. 

Each path must satisfy the rule 1-8 described the above. Paths that are executed at the same time must satisfy the rule 9,10 described the above.
The target is to minimize `T_m`.


### Problem size
`v` and `n` must be at least 50 for the advantage of quantum computing, and 10,000 would be enough for most applications.
`m` would at least about 1,000 for the advantage of quantum computing, and at most 10^15 for meaningful applications.


## Problem simplification
The above definition is complicated, we can typically simplify the problem as follows. The following conditions are not necessarily assumed, but some papers employ them for simplifying the problem and focusing on the optimization.

- Assumption 1 grid field: there are two integers `w,h` and every positions `1<=x_i<=w` and `1<=y_i<=h` will appear in nodes. The edge connect every nearest neighboring nodes.
- Assumption 2 two-body measurement: we are allowed to assume `t_i=2`.
- Assumption 3 uniform boundary types: We assume lattice surgery always connects the same types of boundaries. For every i, we assume `p_{i,1} = p_{i,2} = ... p_{i,t_i}`.
- Assumption 4 fixed locations: In addition to assumption 1, we assume specific location patterns. The popular layout is as follows.

```
1-in-4 location
. . . . . . . 
. 1 . 2 . 3 .
. . . . . . .
. 4 . 5 . 6 .
. . . . . . .
. 7 . 8 . 9 .
. . . . . . . 
```

```
4-in-9 location
. . . . . . . 
. 1 2 . 5 6 .
. 3 4 . 6 8 .
. . . . . . .
. 9 10. 1314.
. 1112. 1516.
. . . . . . . 
```


## Problem extension

The following operations can be extended to perform further optimization.

- Extention 1: Rotation

Every data cell can perform ROTATION instruction, which rotates the orientation of qubits with 90 degrees.
This operation consumes any empty node connected to the data node, and take two clocks.
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



- Extention 2: Moving logical qubit

We are allowed to insert MOVE instruction, which changes the position of data node from a certain node to another.
MOVE instruction takes one clocks and consumes path between original and target nodes.
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

- Extention 3: Reordering lattice surgery instruction

We are allowed to reorder the sequence of quantum operations.
This can be achieved if the following conditions are satisfied for the consecutive instructions.

1. Let Q be a subset of data nodes that both two lattice surgery operations act on.
2. Let T be the number of the data nodes in Q that are accessed through different types of faces, namely H and V.
3. If and only if the number of T is even, their order can be swapped without changing the behavior.

`LATTICE_SUGERY [0 1] [H H]` and `LATTICE_SUGERY [2 3] [H H]` can be reordered as they do not have overlapping targets.
`LATTICE_SUGERY [0 1] [H H]` and `LATTICE_SUGERY [1 2] [H H]` can be reordered as they share data node 1 but access with the same boundary.
`LATTICE_SUGERY [0 1] [H H]` and `LATTICE_SUGERY [1 2] [V H]` cannot be reordered as they share data node 1 and access with the different boundary.
`LATTICE_SUGERY [0 1] [H H]` and `LATTICE_SUGERY [0 1] [V V]` can be reordered as they share data node 1 and access with the different boundary twice.



## 3D Routing

Equivalent circuit transformations allow routing to span multiple time units. For example, to connect qubits 1 and 2 in

```
.......
.1...2.
.......
```

perform the following during the first unit of time:

```
.......
.1**.2.
.......
```

and then the following during the second:

```
.......
.1.**2.
.......
```

This establishes the connection between qubits 1 and 2. Such movement across time may occur any number of times in either the past or future direction. For example, a horizontal connection between logical qubits 1 and 2 can be implemented with these three time steps:

```
..........**......
.1.*****...*....2.
...........***....
```

```
..........*.......
.1**...*.....***2.
.............*....
```

```
........***.......
.1.....**.......2.
..................
```

Allowing such connections makes instruction order ambiguous, so order is defined as follows. Instruction A precedes instruction B if, for every qubit acted upon by both A and B, the time at which A touches that qubit is earlier than the time at which B touches it.

For consecutive instructions that may be reordered, their order may differ from qubit to qubit. For instructions that cannot be reordered, any execution that does not satisfy the condition above has a different effect, even if reordering were hypothetically allowed. For example, it is valid to execute “connect qubits 1 and 2 horizontally” followed by “connect qubits 1 and 2 vertically” as follows:

```
.**..
.*...
.1.2.
.....
```

```
..*..
.....
.1*2.
.....
```

```
..**.
...*.
.1.2.
.....
```

Instructions that can run in parallel can always be reordered, so ambiguity in their order is likewise harmless.

By contrast, it is incorrect to execute the non-reorderable instructions “connect qubits 1, 2, and 3 horizontally” and “connect qubits 1, 2, and 3 vertically” as follows:

```
.****..
.*.*...
.1.2.3.
.......
.......
```

```
....*..
.......
.1*2*3.
..*.*..
..***..
```

```
....**.
.....*.
.1.2.3.
.......
.......
```

### Placement in 2.5 dimensions

The discussion above assumes a two-dimensional mapping, but one may instead consider a specified number of stacked two-dimensional layers. The usual lattice-surgery rules apply between two logical qubits in the same layer. A path between qubits in different layers may move between layers. For example, the following operation between two logical qubits on different layers is permitted:

```
......
.1*.3.
......
=========
......
.4.*2.
......
```

Connections at layer-transition points may not cross. For example, the following instructions cannot execute in parallel:

```
......
.1.*3.
......
=========
......
.4*.2.
......
```

The following can execute in parallel:

```
...*..
.1.*3.
......
=========
..*...
.4*.2.
......
```

Furthermore, in a 2.5-dimensional placement, a logical CNOT can be performed in zero time between logical qubits at the same coordinates in different layers. In the following placement, logical CNOTs between qubits 1 and 3 or between qubits 2 and 3 can be performed in zero time:

```
......
.1..3.
......
=========
......
.4..2.
......
```

### Distributed processing

Assume that each chip has size `(w,h)`, small enough that assigning all logical qubits to one chip is difficult. The logical qubits may instead be distributed across multiple chips.

Logical communication between chips is very slow and can be defined as follows. Allocate one empty edge block on each of the two chips to be connected. Each such pair has a counter that increases by 1 whenever `T` time units elapse. Consuming one count enables a lattice-surgery operation across the chips. A typical value of `T` may be around 1000, though no standard metric exists yet.

For example, assign communication blocks on the left and right edges of two chips, denoted by `E`:

```
...
1.E
...
===
...
E.2
...
```

After `T` time units, the instruction “connect logical qubits 1 and 2 horizontally” can consume a count and execute as follows:

```
...
1*E
...
===
...
E*2
...
```

Multiple communication pairs may be created. As an initial assumption, all chips may be treated as fully connected.

In practice, full connectivity among many chips is probably extremely difficult, so designing an efficient distributed-network topology is desirable when possible. One might also argue that if using more chips with slower unit times (effectively, slower clock periods) does not greatly reduce performance, power consumption can be reduced without applying as much pressure to maximize speed.

### Dynamic scheduling

Lattice-surgery scheduling is generally expected to be performed statically before execution. At runtime, however, some blocks may turn out to be unavailable for various reasons. Recomputing all lattice-surgery paths fast enough to keep pace with execution is impractical; one unit of runtime is roughly `20 us` to `30 ms`. A placement should therefore establish routing rules in advance so that fast dynamic scheduling remains possible even when some regions become unavailable. (The frequency of such failures is currently unknown.)

A practical approach to dynamic scheduling typically divides the large overall memory into small sectors that can each be searched quickly, then optimizes processing within each sector at runtime. Is there an allocation scheme that enables this kind of dynamic scheduling without imposing substantial performance overhead?

---

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
