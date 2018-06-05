// Invalidation of heap-stored pointers
#include <stdlib.h>
#include <stdio.h>

__attribute__ ((noinline))
void store_ptrs(int **pp, size_t numptrs) {
  for (unsigned i=0; i<numptrs; i++ )
    *(pp + i) = (int *)malloc(sizeof(int));
}

__attribute__ ((noinline))
void free_ptrs(int **pp, size_t numptrs) {
  for (unsigned i=0; i<numptrs; i++ )
    free(*(pp + i));
}

__attribute__ ((noinline))
void use_ptrs(int **pp, size_t numptrs) {
  for (unsigned i=0; i<numptrs; i++ )
    printf("%px\n", *(pp + i));
}

int main() {
  size_t numptrs = 4;
  int **arr = (int **)malloc(sizeof(int *) * numptrs);
  store_ptrs(arr, numptrs);
  use_ptrs(arr, numptrs);
  free_ptrs(arr, numptrs);
  use_ptrs(arr, numptrs);
  free(arr);
}
