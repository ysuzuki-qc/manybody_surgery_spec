# 3D Routing Problem

## Background

This document descibes how we can extend 2D routing problems into 3D space. This is based on [K. Hamada et al., Efficient and high-performance routing of lattice-surgery paths on three-dimensional lattice](https://arxiv.org/abs/2401.15829).


## Extension to 3D Routing
Suppose many-body lattice surgery instruction `LATTICE_SUGERY [2 3] [V V]` on the following placement.
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

Instead, we can execute this instruction using two time clocks as follows.
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
Here, a symbol `^` represents a graph is connected to the graph at the next time, and the top of Z-axis movement, we put Z-movement terminator `v`. 
If we represent a coordinate `(x,y)` with a time clock `T` as `(x,y,T)`, this routing tree is `(5,2,1),(5,1,1),(4,1,1),(4,1,2),(3,1,2),(3,2,2)`. 
There are several rules in using this time-axis movement. See rules section for details.


## Application of 3D Routing
Suppose there are three sequntial instructions.
```
LATTICE_SUGERY [1 2] [V V]
LATTICE_SUGERY [2 3] [H H]
LATTICE_SUGERY [3 4 5] [V V]
```
on the following placement.
```
. . . . . . . . .

1 . 2 . 3 . 4 . 5
```

The best routing in the original problem is as follows.
```
LATTICE_SUGERY [1 2] [V V]
T=1
*-*-* . . . . . .
|   |
1 . 2 . 3 . 4 . 5

LATTICE_SUGERY [2 3] [H H]
T=2
. . . . . . . . .
         
1 . 2-*-3 . 4 . 5

LATTICE_SUGERY [3 4 5] [V V]
T=3
. . . . *-*-*-*-*
        |   |   |
1 . 2 . 3 . 4 . 5
```

By using the technique explained the above, we can reduce execution time to 2.
```
LATTICE_SUGERY [1 2] [V V]
T=1
*-*-* . . . . . .
|   |
1 . 2 . 3 . 4 . 5

LATTICE_SUGERY [2 3] [H H]
T=1
. . . . . . . . .
         
1 . 2 ^-3 . 4 . 5
T=2
. . . . . . . . .
        
1 . 2-v 3 . 4 . 5

LATTICE_SUGERY [3 4 5] [V V]
T=1
. . . . . ^-*-*-*
            |   |
1 . 2 . 3 . 4 . 5
T=2
. . . . *-v . . .
        |        
1 . 2 . 3 . 4 . 5
```

## Rules for 3D routing
When we execute a certain lattice surgery instruction, it must satisfy the following requirements. The 3D routing inherit the same requirements.

- **Rule 1. routing graph must be a tree**
- **Rule 2. Every target node must be a leaf of a routing graph**
- **Rule 3. Each leaf of a tree must be a node**
- **Rule 4. all the non-target nodes must not be connected**
- **Rule 5. all the data node must be touched from appropriate direction**

In addition, the target tree must satisfy the following conditions. To describe the condition, we need definitions of new concepts, fork, kink, and segment.
A fork is a node in a tree that has more than two edges in the 3D tree. For example, `(3,1,1), (4,1,2), (7,1,2)` are forks, and the other nodes are not fork.
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

If the fork as three edges to the spatial direction, it is called spatial fork. The other cases (i.e., fork that has edge to time-direction) is called temporal fork.
In the above example `(3,1,1)` is a spatial fork, and `(4,1,2), (7,1,2)` are temporal fork.

- **3D Rule 1. there is no temporal fork in the routing graph**

Next, we introduce a concept of kink and segment. Suppose a 3D routing tree that does not have any temporal fork.
We can find a connected subgraph of Z-axis movement. As there is no temporal fork, a sequence of `^...v` cannot branch during the Z-movement, and starts and ends to XY-plane movement.
If the first and last XY-movement goes 90 degrees or 270 degrees turned, we say that structure a is a kink.

For example, in the following example, there are three Z-axis movement.
Z-move 1: `(2,2,1), (2,2,2)`
Z-move 2: `(4,1,1), (4,1,2), (4,1,3)`
Z-move 3: `(4,2,7), (4,3,7)`

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

Here, Z-move 1 goes horizontally at T=1 and vertically at T=2, and this is a kink. 
Z-move 2 goes horizontally at T=1 and T=3, thus this is NOT a kink. 
Z-move 3 goes horizontally at T=2 and veritcally at T=3, and this is a kink.


Next, we define segments. A segment is a tree that at least has one XY-plane movement when we split 3D tree for each time slice.
In the above example, we can see there is four segments as shown below.

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

In this view, we can see a 3D graph is a segment tree that are connected by Z-axis movement.
Segment A and B are connected with kink Z-movement at `(2,2)`.
Segment A and D are connected with non-kink Z-movement at `(4,1)`.
Segment C and D are connected with kink Z-movement at `(7,1)`.
Thus, we can draw a segment tree as follows.
```
A-B
|
D-C
```

Using this segment tree, We classify all the segment into even and odd segments as follows.
First, we choose a certain leaf segment (in the above case, we choose B or C) as a root. We assigne even segment to the root segment. We choose B as a root in this explanation.
The parity of the other segment is determined whether the number of kinks from root to target is even or odd.
As edges between A-B and C-D are kinks, and an edge between A-D is non-kink, the assignment is 
- B: even
- A: odd
- D: odd
- C: even

Then, we can provide the last two conditions.

- **3D Rule 2. Odd segments have no fork**
- **3D Rule 3. Data node does belongs to even segment**

If the above two conditions are satisfied, every odd segment must start from Z-axis movement and finish with Z-axis movement.
Note that whether this condition is satisfied or not is independent of the choice of a root segment.
In the above example, odd segments A and D have data nodes and forks. Thus, the above example violates both 3D Rule 2 and 3. A valid example is as follows.

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

This is valid and works as `LATTICE_SURGERY [1 2 3 4] [H V V V]`.
We explain why this is valid. This 3D graph is a Steiner tree toucing target data nodes with appropriate boundaries, and this satisfies Rules 1-5.
This routing path does not have any temporal fork, and it satisfies 3D Rule 1. There are five segments in total as follows.

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
Here, edges between `(D,A), (A,E)` are kinks, and the others are not kink.
Thus, only segment A is a odd segment, and the other segments are even.
We can see odd segment A does not have any data node and fork, thus this satisfies 3D Rule 2 and 3.
Thus, this routing graph is valid.

Note that this formalism contains original lattice surgery definitions as a special cases where there is only a single segment.


## Extension to multi-target CNOT
We can also perform multi-target CNOT by using a similar concept. Let `MULTI_TARGET_CNOT [2 3 4] [V V V]` be a multi-control NOT get acting on data nodes 2, 3, and 4.
We say the first data node as control data node, and the other nodes are target nodes. In this instruction, control data node is 2, and 3 and 4 are target data nodes.
This instruction can be executed by assigning a 3D routing graph satisfying the following.

The basic rules and 3D rule 1 are the same.

- **Rule 1. routing graph must be a tree**
- **Rule 2. Every target node must be a leaf of a routing graph**
- **Rule 3. Each leaf of a tree must be a node**
- **Rule 4. all the non-target nodes must not be connected**
- **Rule 5. all the data node must be touched from appropriate direction**
- **3D CNOT Rule 1. there is no temporal fork in the routing graph**

When we assign even or odd parity to each segment, we assign odd segment to a segment with control data node, and determine the parity of the other segments.
Then, we can define the other conditions.

- **3D CNOT Rule 2. Odd segments have no fork**
- **3D CNOT Rule 3. Target data node does belongs to even segment**
- **3D CNOT Rule 3. Control data node belongs to an odd segment**


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
There are three segment, and a segment with control data node 2 is odd, and the others are even segments.
We can see an odd segment does not have any fork, and all the target data nodes belong to even segment.
Thus, this works as `MULTI_TARGET_CNOT [2 3 4] [V V V]`.


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
t_1 k_1
q_{1,1} q_{1,2} ... q_{1,t_1}
p_{1,1} p_{1,2} ... p_{1,t_1}
t_2 k_2
q_{2,1} q_{2,2} ... q_{2,t_1}
p_{2,1} p_{2,2} ... p_{2,t_1}
...
t_m k_m
q_{m,1} q_{m,2} ... q_{m,t_1}
p_{m,1} p_{m,2} ... p_{m,t_1}
```

Here, `v, e, n, m, x_i, y_i, w_{i,j}, t_i, q_{i,j}, p_{i,j}` are the same as 2D case.
`k_i \in {CX, LS}` specifies the target instruction is multi-target CNOT or lattice surgery.
If `k_i = CX`, the control data node is `q_{i,1}`.


### Output
The output must be writte in the following form.
```
P_1 P_2 ... P_n
S_1 E_1
T_{1,1} R_{1,1} E_{1,1,1} E_{1,1,2} ... E_{1,1,R_{1,1}}
T_{1,2} R_{1,2} E_{1,2,1} E_{1,2,2} ... E_{1,2,R_{1,2}}
...
T_{1,S_1} R_{1,S_1} E_{1,S_1,1} E_{1,S_1,2} ... E_{1,S_1,R_{1,S_1}}
G_{1,1,1} G_{1,1,2} H_{1,1}
G_{1,2,1} G_{1,2,2} H_{1,2}
...
G_{1,E_1,1} G_{1,E_1,2} H_{1,E_1}
...
S_m E_m
T_{m,1} R_{m,1} E_{m,1,1} E_{m,1,2} ... E_{m,1,R_{m,1}}
...
T_{m,S_m} R_{m,S_m} E_{m,S_m,1} E_{m,S_m,2} ... E_{m,S_m,R_{m,S_m}}
G_{m,1,1} G_{m,1,2} H_{m,1}
...
G_{m,E_m,1} G_{m,E_m,2} H_{m,E_m}
```

Here, `P_i` is the node of i-th qubit is located and must satisfy `1 <= P_i <= v`. As qubit are located in different place, if `i \neq i'` then `P_i \neq P_i'`.
A sequence of the following set specifies an assignment to the i-th instruction.
```
S_i E_i
T_{i,1} R_{i,1} E_{i,1,1} E_{i,1,2} ... E_{i,1,R_{1,1}}
T_{i,2} R_{i,2} E_{i,2,1} E_{i,2,2} ... E_{i,2,R_{1,2}}
...
T_{i,S_i} R_{i,S_i} E_{i,S_i,1} E_{i,S_i,2} ... E_{i,S_i,R_{i,S_i}}
G_{i,1,1} G_{i,1,2} H_{i,1}
G_{i,2,1} G_{i,2,2} H_{i,2}
...
G_{i,E_i,1} G_{i,E_i,2} H_{i,E_i}
```
`S_i` is the number of segments in the i-th instructions.
`E_i` is the number of Z-movement in the i-th instruction.
`T_{i,j}` is the number of time clock of j-th segment in the i-th instruction.
`R_{i,j}` is the number of edges in the j-th segment in the i-th instruction.
`E_{i,j,k}` is the k-th edge of the j-th segment in the i-th instruction.
`G_{i,j,0}` and `G_{i,j,0}` are two indices of segments that are connected with the j-th edge in the segment tree for the i-th instruction.
`H_{i,j}` is the node index that 3D tree moves along with Z-axis to connect the j-th edge in the segment tree for the i-th instruction.



## Problem simplification
The above definition is complicated, we can typically simplify the problem as follows. The following conditions are not necessarily assumed, but some papers employ them for simplifying the problem and focusing on the optimization.

- **Assumption 1: all single-target CNOT**

Several popular compilation schemes only output single-target CNOT gates. This is equal to assume `t_i=2` and `k_i=CX`.

- **Assumption 1: all lattice surgery**

Several popular compilation schemes only output multi-target lattice surgery only. This is equal to assume `k_i=LS`.
