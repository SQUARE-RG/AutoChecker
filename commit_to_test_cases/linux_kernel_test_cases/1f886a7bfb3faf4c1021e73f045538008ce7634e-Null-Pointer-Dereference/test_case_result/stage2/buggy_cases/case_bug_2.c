#include <stdio.h>
#include <stdlib.h>

struct device {
    int status;
    char *name;
};

static void *devm_kzalloc(size_t size) {
    return NULL; // Always fail to trigger bug
}

static int test_case2(void) {
    int i = 0;
    struct device *devs[3];
    
    for (i = 0; i < 3; i++) {
        devs[i] = devm_kzalloc(sizeof(struct device));
        // CHECK-MESSAGES: Potential NULL pointer dereference if devm_kzalloc fails
        devs[i]->status = 0; // Bug: Dereferencing potential NULL
        devs[i]->name = "test";
    }
    
    return 0;
}

int main(void) {
    test_case2();
    return 0;
}