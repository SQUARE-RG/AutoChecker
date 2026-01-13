#include <stdio.h>
#include <stdlib.h>

struct sub_item {
    int data;
};

struct item {
    int id;
    struct sub_item *sub;
};

static void *devm_kzalloc(size_t size) {
    return calloc(1, size);
}

static int test_case3(void) {
    struct item *item_ptr = NULL;
    
    item_ptr = devm_kzalloc(sizeof(struct item));
    if (!item_ptr) return -1;
    
    item_ptr->sub = devm_kzalloc(sizeof(struct sub_item));
    // CHECK-MESSAGES: Potential NULL pointer dereference if devm_kzalloc fails
    item_ptr->sub->data = 100; // Bug: No NULL validation for nested allocation
    
    free(item_ptr->sub);
    free(item_ptr);
    return 0;
}

int main(void) {
    test_case3();
    return 0;
}