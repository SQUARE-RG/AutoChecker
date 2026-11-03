#include <stdlib.h>

int main() {
    int* ptr = (int*)malloc(sizeof(int));
    if (ptr != NULL) {
        *ptr = 7;
        free(ptr);
        ptr = NULL;
    }
    return 0;
}
