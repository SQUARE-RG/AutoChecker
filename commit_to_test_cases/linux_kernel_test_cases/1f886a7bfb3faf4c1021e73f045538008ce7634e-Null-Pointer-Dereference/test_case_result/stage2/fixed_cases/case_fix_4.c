#include <stdio.h>
#include <stdlib.h>

#define FAILURE 1

struct child {
    int data;
    struct parent_struct *parent;
};

struct parent_struct {
    int num_children;
    struct child *children[];
};

static void *kzalloc(size_t size) {
    if (size == 0) return NULL;
    void *ptr = malloc(size);
    if (ptr)
        memset(ptr, 0, size);
    return ptr;
}

static int create_parent(int n) {
    struct parent_struct *p;
    int i;

    p = kzalloc(sizeof(struct parent_struct) + n * sizeof(struct child *));
    if (!p)
        return FAILURE;

    p->num_children = n;

    for (i = 0; i < n; i++) {
        p->children[i] = kzalloc(sizeof(struct child));
        if (!p->children[i])
            return FAILURE;

        p->children[i]->parent = p;
        p->children[i]->data = i;
    }
    return 0;
}

int main() {
    if (create_parent(3) != 0)
        return 1;
    return 0;
}