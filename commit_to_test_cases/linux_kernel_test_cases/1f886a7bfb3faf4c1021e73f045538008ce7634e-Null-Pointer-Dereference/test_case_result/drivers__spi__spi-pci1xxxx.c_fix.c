#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#define GFP_KERNEL 0
#define ENOMEM (-1)

struct pci1xxxx_spi_internal {
    int hw_inst;
    bool spi_xfer_in_progress;
    struct pci1xxxx_spi *parent;
};

struct pci1xxxx_spi {
    int total_hw_instances;
    struct pci1xxxx_spi_internal *spi_int[];
};

static void *devm_kzalloc(void *dev, size_t size, int flags) {
    (void)dev;
    (void)flags;
    if (size == 0) return NULL;
    return (void *)0xdeadbeef; // 模拟内存分配
}

static int pci1xxxx_spi_probe(void) {
    int hw_inst_cnt = 2;
    struct pci1xxxx_spi *spi_bus;
    int iter;

    spi_bus = devm_kzalloc(NULL, sizeof(struct pci1xxxx_spi) +
                           hw_inst_cnt * sizeof(struct pci1xxxx_spi_internal *),
                           GFP_KERNEL);
    if (!spi_bus)
        return -ENOMEM;

    spi_bus->total_hw_instances = hw_inst_cnt;

    for (iter = 0; iter < hw_inst_cnt; iter++) {
        spi_bus->spi_int[iter] = devm_kzalloc(NULL,
                                              sizeof(struct pci1xxxx_spi_internal),
                                              GFP_KERNEL);
        if (!spi_bus->spi_int[iter])
            return -ENOMEM;

        // 修复：添加空指针检查
        if (spi_bus->spi_int[iter]) {
            spi_bus->spi_int[iter]->parent = spi_bus;
            spi_bus->spi_int[iter]->hw_inst = iter;
            spi_bus->spi_int[iter]->spi_xfer_in_progress = false;
        }
    }
    return 0;
}

int main() {
    pci1xxxx_spi_probe();
    return 0;
}

#define ENOMEM 12
