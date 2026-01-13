#include <stdio.h>
#include <stdlib.h>

struct resource {
    int id;
    int value;
};

static void *devm_kzalloc(size_t size) {
    return calloc(1, size);
}

static int test_case4(void) {
    int i = 0;
    struct resource *res[5];
    
    for (i = 0; i < 5; i++) {
        res[i] = devm_kzalloc(sizeof(struct resource));
        // CHECK-MESSAGES: Potential NULL pointer dereference if devm_kzalloc fails
        res[i]->id = i; // Bug: Missing NULL check
        res[i]->value = i * 10;
    }
    
    for (i = 0; i < 5; i++) {
        free(res[i]);
    }
    
    return 0;
}

int main(void) {
    test_case4();
    return 0;
}