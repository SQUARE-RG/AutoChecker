#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

struct spi_internal {
    int idx;
    bool in_use;
};

struct spi_bus {
    int count;
    struct spi_internal *arr[];
};

static void *devm_kzalloc(size_t size) {
    return calloc(1, size);
}

static int test_case1(void) {
    int i = 0;
    struct spi_bus *bus = NULL;
    
    bus = devm_kzalloc(sizeof(struct spi_bus) + 2 * sizeof(struct spi_internal *));
    if (!bus) return -1;
    
    bus->count = 2;
    
    for (i = 0; i < 2; i++) {
        bus->arr[i] = devm_kzalloc(sizeof(struct spi_internal));
        // CHECK-MESSAGES: Potential NULL pointer dereference if devm_kzalloc fails
        bus->arr[i]->idx = i; // Bug: No NULL validation
        bus->arr[i]->in_use = false;
    }
    
    free(bus);
    return 0;
}

int main(void) {
    test_case1();
    return 0;
}