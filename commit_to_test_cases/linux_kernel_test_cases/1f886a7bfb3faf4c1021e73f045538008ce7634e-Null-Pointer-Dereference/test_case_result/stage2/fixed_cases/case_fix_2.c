#include <stdio.h>
#include <stdlib.h>

#define NOMEM 12

struct node {
    int val;
    struct list *list;
};

struct list {
    int size;
    struct node *nodes[];
};

static void *alloc_mem(void *dev, size_t size) {
    (void)dev;
    if (size == 0) return NULL;
    return malloc(size);
}

static int create_list(int n) {
    struct list *l;
    int i;

    l = alloc_mem(NULL, sizeof(struct list) + n * sizeof(struct node *));
    if (!l)
        return NOMEM;

    l->size = n;

    for (i = 0; i < n; i++) {
        l->nodes[i] = alloc_mem(NULL, sizeof(struct node));
        if (!l->nodes[i])
            return NOMEM;

        l->nodes[i]->list = l;
        l->nodes[i]->val = i;
    }
    return 0;
}

int main() {
    if (create_list(4) != 0)
        return 1;
    return 0;
}