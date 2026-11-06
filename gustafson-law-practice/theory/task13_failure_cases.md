# Task 13: Algorithms Where Weak Scaling Can Fail

Weak scaling assumes that each processor receives approximately the same workload as the system grows.

However, some algorithms have communication, synchronization, or global coordination costs that increase faster than useful computation.

## Case 1: Global Sorting

Examples:
- Distributed merge sort.
- Sample sort.
- Distributed sorting of very large datasets.

Why weak scaling can fail:

1. Each processor sorts its local data.
2. Processors exchange splitters or partitions.
3. Data is redistributed across the system.
4. Global ordering requires communication and coordination.

As processor count increases, data exchange and synchronization may become expensive.

Even when local data size is fixed, network contention and redistribution overhead can increase.

## Case 2: Breadth-First Search on Irregular Graphs

Why weak scaling can fail:

1. Graph vertices have different numbers of neighbors.
2. Some processors receive more work than others.
3. Frontier updates require communication.
4. Duplicate detection and visited-state updates require synchronization.

Power-law graphs can create highly uneven workloads because a small number of vertices have extremely high degree.

The slowest processor can determine the completion time of each iteration.

## Comparison

| Algorithm | Main limitation |
|---|---|
| Global sorting | Data redistribution and global coordination |
| Graph BFS | Load imbalance and synchronization |

## Possible Solutions

- Improve data partitioning.
- Reduce global synchronization.
- Use asynchronous algorithms where appropriate.
- Balance workload dynamically.
- Use communication-efficient data structures.

## Conclusion

Weak scaling is not guaranteed simply because local computation remains constant. Communication, data dependencies, and load imbalance can prevent constant execution time.
