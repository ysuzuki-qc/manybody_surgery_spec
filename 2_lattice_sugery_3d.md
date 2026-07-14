# 3D Routing Problem

## Background

This document describes how the 2D routing problem can be extended to three-dimensional space. It is based on [K. Hamada et al., *Efficient and High-Performance Routing of Lattice-Surgery Paths on a Three-Dimensional Lattice*](https://arxiv.org/abs/2401.15829).


## Extension to 3D Routing
Consider the many-body lattice-surgery instruction `LATTICE_SURGERY [2 3] [V V]` on the following layout.
```
. . . . . . . . .

1 . 2 . 3 . 4 . 5
```

A simple routing result for this situation is as follows.
```
. . *-*-* . . . .
    |   |
1 . 2 . 3 . 4 . 5
```

Alternatively, we can execute this instruction over two clock cycles as follows.
```
T=1
. . . ^-* . . . .
        |
1 . 2 . 3 . 4 . 5
T=2
. . *-v . . . . .
    |    
1 . 2 . 3 . 4 . 5
```
Here, `^` indicates that the graph continues into the next clock cycle, and `v` marks the other endpoint of a movement along the time axis (the z-axis). If the position `(x,y)` at clock cycle `T` is represented as `(x,y,T)`, this routing tree consists of `(5,2,1)`, `(5,1,1)`, `(4,1,1)`, `(4,1,2)`, `(3,1,2)`, and `(3,2,2)`. Several rules govern movement along the time axis; see the rules section for details.


## Application of 3D Routing
Suppose there are three sequential instructions.
```
LATTICE_SURGERY [1 2] [V V]
LATTICE_SURGERY [2 3] [H H]
LATTICE_SURGERY [3 4 5] [V V V]
```
on the following layout.
```
. . . . . . . . .

1 . 2 . 3 . 4 . 5
```

The best routing in the original problem is as follows.
```
LATTICE_SURGERY [1 2] [V V]
T=1
*-*-* . . . . . .
|   |
1 . 2 . 3 . 4 . 5

LATTICE_SURGERY [2 3] [H H]
T=2
. . . . . . . . .
         
1 . 2-*-3 . 4 . 5

LATTICE_SURGERY [3 4 5] [V V V]
T=3
. . . . *-*-*-*-*
        |   |   |
1 . 2 . 3 . 4 . 5
```

Using the technique described above, we can reduce the execution time to two clock cycles.
```
LATTICE_SURGERY [1 2] [V V]
T=1
*-*-* . . . . . .
|   |
1 . 2 . 3 . 4 . 5

LATTICE_SURGERY [2 3] [H H]
T=1
. . . . . . . . .
         
1 . 2 ^-3 . 4 . 5
T=2
. . . . . . . . .
        
1 . 2-v 3 . 4 . 5

LATTICE_SURGERY [3 4 5] [V V]
T=1
. . . . . ^-*-*-*
            |   |
1 . 2 . 3 . 4 . 5
T=2
. . . . *-v . . .
        |        
1 . 2 . 3 . 4 . 5
```

## Rules for 3D Routing

Every lattice-surgery instruction must satisfy the following requirements. Three-dimensional routes inherit the same five basic rules as two-dimensional routes.

- **Rule 1. The routing graph must be a tree.**
- **Rule 2. Every operand node must be a leaf of the routing graph.**
- **Rule 3. Every leaf of the tree must be a data node.**
- **Rule 4. No non-operand data node may be connected.**
- **Rule 5. Every operand data node must be approached from the specified direction.**

In addition, the routing tree must satisfy the conditions below. To state them, we first define three concepts: forks, kinks, and segments. A fork is a node of degree greater than two in a 3D tree. For example, `(3,1,1)`, `(4,1,2)`, and `(7,1,2)` are forks in the graph below; the other nodes are not.
```
Coordinate
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . . . . . . . .
 |           
2| 1 . 2 . 3 . 4 . 5
 |
3| . . . . . . . . .


T=1
   1 2 3 4 5 6 7 8 9
  -------------------
1| *-*-*-^ . . . . .
 | |   |     
2| 1 . 2 . 3 . 4 . 5
 |
3| . . . . . . . . .


T=2
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . . ^-* . ^-*-*
 |         |   |   |
2| 1 . 2 . 3 . 4 . 5
 |
3| . . . . . . . . .


T=3
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . . v-*-*-v . .
 |           
2| 1 . 2 . 3 . 4 . 5
 |
3| . . . . . . . . .
```

If a fork is not connected to top (node at T+1) or bottom (node at T-1) nodes, i.e., all the connectional is spatial, it is called a spatial fork. Any fork with an edge in the time direction is called a temporal fork. In the example above, `(3,1,1)` is a spatial fork, whereas `(4,1,2)` and `(7,1,2)` are temporal forks.

- **3D Rule 1. The routing graph must contain no temporal forks.**

Next, we introduce kinks and segments. Consider a 3D routing tree with no temporal forks. Each connected subgraph consisting of z-axis edges is a nonbranching sequence of the form `^...v` whose endpoints connect to movements in the xy-plane. Such a sequence is called a kink if the directions of the xy-plane edges at its two endpoints differ by 90 or 270 degrees.

The following example contains three z-axis movements.
Z-move 1: `(2,2,1), (2,2,2)`
Z-move 2: `(4,1,1), (4,1,2), (4,1,3)`
Z-move 3: `(7,1,2), (7,1,3)`

```
Coordinate
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . . . . . . . .
 |           
2| 1 . 2 . 3 . 4 . 5
 |
3| . . . . . . . . .


T=1
   1 2 3 4 5 6 7 8 9
  -------------------
1| . *-*-^ . . . . .
 |   | |     
2| 1 ^ 2 . 3 . 4 . 5
 |
3| . . . . . . . . .


T=2
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . . ^ . . ^ . .
 |             |    
2| 1-v 2 . 3 . 4 . 5
 |
3| . . . . . . . . .


T=3
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . . v-*-*-v . .
 |         | 
2| 1 . 2 . 3 . 4 . 5
 |
3| . . . . . . . . .
```

Z-movement 1 is horizontal at `T=1` and vertical at `T=2`, so it is a kink. Z-movement 2 is horizontal at both `T=1` and `T=3`, so it is not a kink. Z-movement 3 is horizontal at `T=2` and vertical at `T=3`, so it is a kink.


Next, we define segments. After splitting a 3D tree into time slices, a segment is a connected tree within one time slice that contains at least one xy-plane edge. If there are multiple disconnected trees, they are considered as different segments. The example above has four segments, as shown below.

```
Segment A @ T=1
   1 2 3 4 5 6 7 8 9
  -------------------
1| . *-*-^ . . . . .
 |   | |     
2| . ^ 2 . . . . . .
 |
3| . . . . . . . . .


Segment B @ T=2
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . . . . . . . .
 |                  
2| 1-v . . . . . . .
 |
3| . . . . . . . . .

Segment C @ T=2
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . . . . . ^ . .
 |             |    
2| . . . . . . 4 . .
 |
3| . . . . . . . . .


Segment D @ T=3
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . . v-*-*-v . .
 |         | 
2| . . . . 3 . . . .
 |
3| . . . . . . . . .
```

From this perspective, the 3D graph is a tree of segments connected by z-axis movements. Segments A and B are connected by a kink at `(2,2)`. Segments A and D are connected by a non-kink z-axis movement at `(4,1)`. Segments C and D are connected by a kink at `(7,1)`. The resulting segment tree is
```
A-B
|
D-C
```

Using this segment tree, we classify the segments as even or odd. First, choose any segment with data node as the root, and assign it even parity. Here, we choose B as the root. The parity of every other segment is determined by whether the path from the root contains an even or odd number of kinks. Because the edges A–B and C–D represent kinks whereas A–D does not, the assignment is
- B: even
- A: odd
- D: odd
- C: even

We can now state the final two conditions.

- **3D Rule 2. Odd segments must contain no forks.**
- **3D Rule 3. Every operand data node must belong to even segments.**

If these two conditions are satisfied, every odd segment begins and ends with a z-axis movement. Whether the conditions hold is independent of the choice of root segment. In the example above, odd segments A and D contain data nodes and forks, so the graph violates both 3D Rule 2 and 3. A valid example follows.

```
T=1
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . *-*-* . . . .
 |     | | | 
2| 1 ^ 2 ^ 3 . 4 . 5
 |   |         |
3| . ^ . . . ^-* . .


T=2
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . . . . . . . .
 |                  
2| 1-v 2 v 3 . 4 . 5
 |       |      
3| . v-*-*-*-v . . .
```

This graph is a valid implementation of `LATTICE_SURGERY [1 2 3 4] [H V V V]`. It is a Steiner tree that touches the operand data nodes through the specified boundaries and therefore satisfies Rules 1–5. It contains no temporal forks, so it also satisfies 3D Rule 1. Its five segments are shown below.

```
Segment A @ T=1
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . . . . . . . .
 |        
2| . ^ . . . . . . .
 |   |         
3| . ^ . . . . . . .

Segment B @ T=1
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . *-*-* . . . .
 |     | | | 
2| . . 2 ^ 3 . . . .
 |             
3| . . . . . . . . .

Segment C @ T=1
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . . . . . . . .
 |         
2| . . . . . . 4 . .
 |             |
3| . . . . . ^-* . .

Segment D @ T=2
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . . . . . . . .
 |                  
2| 1-v . . . . . . .
 |             
3| . . . . . . . . .

Segment E @ T=2
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . . . . . . . .
 |                  
2| . . . v . . . . .
 |       |      
3| . v-*-*-*-v . . .
```

The segment tree of the above graph is as follows.
```
D-A-E-C
    |
    B
```
Here, the edges `(D,A)` and `(A,E)` represent kinks; the other edges do not. Thus, only segment A is odd, and all other segments are even. Odd segment A contains neither data nodes nor forks, so the graph satisfies 3D Rules 2 and 3 and is therefore valid.

The original 2D lattice-surgery definition is the special case of this formalism in which the routing graph has only one segment.


## Extension to Multi-Target CNOT

A similar construction can be used to perform a multi-target CNOT. Let `MULTI_TARGET_CNOT [2 3 4] [V V V]` denote a CNOT gates, which applies Pauli X gates on data 3 and 4 if the data 2 is True. The first data node is called a control data node, the remaining data nodes are called target data nodes, and the union of them are called operand data nodes. The instruction can be executed using any 3D routing graph that satisfies the following rules.

The five basic rules and 3D Rule 1 remain unchanged.

- **Rule 1. The routing graph must be a tree.**
- **Rule 2. Every operand node must be a leaf of the routing graph.**
- **Rule 3. Every leaf of the tree must be a data node.**
- **Rule 4. No non-operand data node may be connected.**
- **Rule 5. Every operand data node must be approached from the specified direction.**
- **3D CNOT Rule 1. The routing graph must contain no temporal forks.**

To assign parity, first assign even parity to the segment containing a target data node (any choice is okay for judging whether the routing graph satisfies the requirement), and then determine the parity of all other segments. The remaining conditions are

- **3D CNOT Rule 2. Odd segments must contain no forks.**
- **3D CNOT Rule 3. Every target data node must belong to an even segment.**
- **3D CNOT Rule 4. The control data node must belong to an odd segment.**


```
T=1
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . v . . . . . .
 |     |     
2| 1 . 2 . 3 ^ 4 . 5
 |           | |
3| . . . . . .-* . .


T=2
   1 2 3 4 5 6 7 8 9
  -------------------
1| . . ^-*-*-* . . .
 |         | |      
2| 1 . 2 . 3 v 4 . 5
 |              
3| . . . . . . . . .
```
There are three segments. The segment containing control data node 2 is odd, and the other two segments are even. The odd segment contains no fork, and all target data nodes belong to even segments. Therefore, this graph implements `MULTI_TARGET_CNOT [2 3 4] [V V V]`.


## Parallel execution of Lattice Surgery and Multi-Target CNOT

The essential rules are the same.
- **Parallel Rule 1. Routing trees must not share any empty node at the same time.**
- **Parallel Rule 2. Routing trees must not share a data node through boundaries of different orientations at the same time.**

Also, as the instruction of 3D routing can span multile time clock, we need to define requirement for the ordering.

- **3D Parallel Rule 1. If instruction A is executed after B and they share operand data node x and touch with different types of boundaries, data node x must be touched by A after B.**

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
t_1 k_1
q_{1,1} q_{1,2} ... q_{1,t_1}
p_{1,1} p_{1,2} ... p_{1,t_1}
t_2 k_2
q_{2,1} q_{2,2} ... q_{2,t_2}
p_{2,1} p_{2,2} ... p_{2,t_2}
...
t_m k_m
q_{m,1} q_{m,2} ... q_{m,t_m}
p_{m,1} p_{m,2} ... p_{m,t_m}
```

Here, `v, e, n, m, x_i, y_i, w_{i,j}, t_i, q_{i,j}, p_{i,j}` have the same meanings as in the 2D case. `k_i \in {CX, LS}` specifies whether the instruction is a multi-target CNOT or a lattice-surgery instruction. If `k_i = CX`, then `q_{i,1}` is the control data node.


### Output
The output must have the following format.
```
P_1 P_2 ... P_n
S_1
T_{1,1} R_{1,1} E_{1,1,1} E_{1,1,2} ... E_{1,1,R_{1,1}}
T_{1,2} R_{1,2} E_{1,2,1} E_{1,2,2} ... E_{1,2,R_{1,2}}
...
T_{1,S_1} R_{1,S_1} E_{1,S_1,1} E_{1,S_1,2} ... E_{1,S_1,R_{1,S_1}}
G_{1,1,1} G_{1,1,2} H_{1,1}
G_{1,2,1} G_{1,2,2} H_{1,2}
...
G_{1,S_1-1,1} G_{1,S_1-1,2} H_{1,S_1-1}
...
S_m
T_{m,1} R_{m,1} E_{m,1,1} E_{m,1,2} ... E_{m,1,R_{m,1}}
...
T_{m,S_m} R_{m,S_m} E_{m,S_m,1} E_{m,S_m,2} ... E_{m,S_m,R_{m,S_m}}
G_{m,1,1} G_{m,1,2} H_{m,1}
...
G_{m,S_m-1,1} G_{m,S_m-1,2} H_{m,S_m-1}
```

Here, `P_i` is the node at which the `i`-th qubit is located and must satisfy `1 <= P_i <= v`. Because different qubits occupy different nodes, if `i \neq i'`, then `P_i \neq P_i'`. The following block specifies an assignment for the `i`-th instruction.
```
S_i
T_{i,1} R_{i,1} E_{i,1,1} E_{i,1,2} ... E_{i,1,R_{i,1}}
T_{i,2} R_{i,2} E_{i,2,1} E_{i,2,2} ... E_{i,2,R_{i,2}}
...
T_{i,S_i} R_{i,S_i} E_{i,S_i,1} E_{i,S_i,2} ... E_{i,S_i,R_{i,S_i}}
G_{i,1,1} G_{i,1,2} H_{i,1}
G_{i,2,1} G_{i,2,2} H_{i,2}
...
G_{i,S_i-1,1} G_{i,S_i-1,2} H_{i,S_i-1}
```
`S_i` is the number of segments in the `i`-th instruction.
`T_{i,j}` is the clock cycle of the `j`-th segment in the `i`-th instruction and satisfies `T_{i,j} >= 1`
`R_{i,j}` is the number of edges in the `j`-th segment of the `i`-th instruction and satisfies `R_{i,j} >= 1`
`E_{i,j,k}` is the `k`-th edge of the `j`-th segment in the `i`-th instruction and satisfise `1 <= E_{i,j,k} <= e`
`G_{i,j,1}` and `G_{i,j,2}` are the indices of the two segments connected by the `j`-th edge of the segment tree for the `i`-th instruction and satisfies `1 <= G_{i,j,k} <= S_i` Note that since segments tree is a tree, there are always `S_i-1` edges in this tree.
`H_{i,j}` is the index of the node along which the 3D tree moves in the z direction to form the `j`-th edge of the segment tree for the `i`-th instruction, and satisfies `1 <= H_{i,j} <= v`.

The aim is to minimize `max_{i,j} T_{i,j}`.

## Problem simplification
The definition above is complex, so the problem is often simplified using the assumptions below. These assumptions are optional, but some papers use them to isolate the optimization problem.

- **Assumption 1: all single-target CNOT**

Several popular compilation schemes output only single-target CNOT gates. This is equivalent to assuming `t_i=2` and `k_i=CX`.

- **Assumption 2: all lattice surgery**

Several popular compilation schemes output only lattice-surgery instructions. This is equivalent to assuming `k_i=LS`.


## Heuristic Solution for the 3D Routing Problem

This section presents a heuristic for routing a `MULTI_TARGET_CNOT`. Lattice-surgery routing can be handled as a special case, as described below. Because the procedure is heuristic, it is not guaranteed to find a route even when a feasible route exists.

- **Step 1: Construct a 2D Steiner tree for the target data nodes.**
  - Finding a minimum Steiner tree is NP-hard, so an approximation or a greedy heuristic may be used. For example, suppose the target data nodes are `[1,2,3,...,m]`. First, find a shortest path between nodes `1` and `2`. Next, connect node `3` to the existing tree by a shortest path, and repeat this process through node `m`. Every path must also respect the boundary constraints and avoid non-operand data nodes and empty nodes that are already used by the processed instructions.

- **Step 2: Embed the 2D Steiner tree in spacetime.**
  - Assign the vertices and edges of the 2D tree to time slices, analogously to placing blocks in Tetris, while avoiding resources already occupied by previously routed instructions. See Figures 9 and 10 of [K. Hamada et al., *Efficient and High-Performance Routing of Lattice-Surgery Paths on a Three-Dimensional Lattice*](https://arxiv.org/abs/2401.15829) for its intuitive visualization. If the resulting 3D graph violates the parity conditions for odd segments, adjust the time slices of its segments and introduce or remove kinks as necessary. If no valid embedding is found within a prescribed search limit, report failure or fall back to placing the entire 2D tree in an unoccupied time slice. This fallback produces a single even segment, provided that such a time slice and spatial route are available.

- **Step 3: Attach the control data node.**
  - Find a path from the control data node to the existing tree of target data nodes. Add the path in a way that preserves the tree structure and all boundary and occupancy constraints. If the control data node does not thereby belong to an odd segment, introduce a pinch structure that changes the required parity, or increase the time clock of touching the control data node. The pinch construction is described in Figures 11 and 12 of [K. Hamada et al., *Efficient and High-Performance Routing of Lattice-Surgery Paths on a Three-Dimensional Lattice*](https://arxiv.org/abs/2401.15829). 

Apply this procedure to the instructions in order. Resources occupied by previously routed instructions and the required ordering of accesses to shared operand data nodes must be included when routing each subsequent instruction. This greedy procedure does not guarantee a globally optimal schedule.

For a `LATTICE_SURGERY` instruction, apply Steps 1 and 2 to all operand data nodes and omit Step 3. When there are exactly two operand data nodes, Step 1 reduces to a shortest-path problem. In an unweighted graph, it can be solved exactly by breadth-first search; in a weighted graph with nonnegative edge weights, Dijkstra's algorithm can be used.
