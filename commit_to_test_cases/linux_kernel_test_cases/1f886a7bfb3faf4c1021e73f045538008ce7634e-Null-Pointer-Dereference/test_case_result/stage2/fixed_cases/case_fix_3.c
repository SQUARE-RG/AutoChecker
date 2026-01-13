#include <stdio.h>
#include <stdlib.h>

#define ERROR 1

struct entry {
    int key;
    int val;
};

struct table {
    int capacity;
    struct entry *entries[];
};

static void *my_alloc(size_t size) {
    if (size == 0) return NULL;
    return malloc(size);
}

static int init_table(int cap) {
    struct table *t;
    int i;

    t = my_alloc(sizeof(struct table) + cap * sizeof(struct entry *));
    if (!t)
        return ERROR;

    t->capacity = cap;

    for (i = 0; i < cap; i++) {
        t->entries[i] = my_alloc(sizeof(struct entry));
        if (!t->entries[i])
            return ERROR;

        t->entries[i]->key = i;
        t->entries[i]->val = 0;
    }
    return 0;
}

int main() {
    if (init_table(5) != 0)
        return 1;
    return 0;
}