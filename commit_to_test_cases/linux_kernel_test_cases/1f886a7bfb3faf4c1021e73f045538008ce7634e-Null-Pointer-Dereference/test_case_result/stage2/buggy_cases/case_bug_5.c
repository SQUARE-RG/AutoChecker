#include <stdio.h>
#include <stdlib.h>

struct config {
    int mode;
    int rate;
};

static void *devm_kzalloc(size_t size) {
    return calloc(1, size);
}

static int test_case5(void) {
    struct config *cfg = NULL;
    
    cfg = devm_kzalloc(sizeof(struct config));
    // CHECK-MESSAGES: Potential NULL pointer dereference if devm_kzalloc fails
    cfg->mode = 1; // Bug: No NULL validation after allocation
    cfg->rate = 100;
    
    free(cfg);
    return 0;
}

int main(void) {
    test_case5();
    return 0;
}