#include <stdio.h>
#include <stdlib.h>

struct node {
    int val;
    struct node *next;
};

static void *devm_kzalloc(size_t size) {
    return calloc(1, size);
}

static int test_case6(void) {
    struct node *node1 = NULL;
    struct node *node2 = NULL;
    
    node1 = devm_kzalloc(sizeof(struct node));
    if (!node1) return -1;
    
    node2 = devm_kzalloc(sizeof(struct node));
    // CHECK-MESSAGES: Potential NULL pointer dereference if devm_kzalloc fails
    node2->val = 200; // Bug: Missing NULL check for second allocation
    node2->next = NULL;
    
    node1->val = 100;
    node1->next = node2;
    
    free(node1);
    free(node2);
    return 0;
}

int main(void) {
    test_case6();
    return 0;
}