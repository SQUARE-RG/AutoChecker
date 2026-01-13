#include <stdio.h>
#include <stdlib.h>

#define FAILURE 1

struct device {
    int id;
    struct controller *parent;
};

struct controller {
    int dev_count;
    struct device *devs[];
};

static void *alloc_dev(void *dev, size_t size) {
    (void)dev;
    if (size == 0) return NULL;
    return malloc(size);
}

static int init_controller(int num_devs) {
    struct controller *ctrl;
    int i;

    ctrl = alloc_dev(NULL, sizeof(struct controller) +
                            num_devs * sizeof(struct device *));
    if (!ctrl)
        return FAILURE;

    ctrl->dev_count = num_devs;

    for (i = 0; i < num_devs; i++) {
        ctrl->devs[i] = alloc_dev(NULL, sizeof(struct device));
        if (!ctrl->devs[i])
            return FAILURE;

        ctrl->devs[i]->parent = ctrl;
        ctrl->devs[i]->id = i;
    }
    return 0;
}

int main() {
    if (init_controller(3) != 0)
        return 1;
    return 0;
}