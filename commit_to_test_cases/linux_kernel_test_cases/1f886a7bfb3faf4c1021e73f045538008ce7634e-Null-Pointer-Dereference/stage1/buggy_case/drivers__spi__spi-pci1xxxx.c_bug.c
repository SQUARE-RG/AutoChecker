#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include "global.h"
// Stub for devm_kzalloc
static void *devm_kzalloc(size_t size) {
    return calloc(1, size);
}

struct pci1xxxx_spi_internal {
    int hw_inst;
    bool spi_xfer_in_progress;
};

struct pci1xxxx_spi {
    int total_hw_instances;
    struct pci1xxxx_spi_internal *spi_int[];
};

static int pci1xxxx_spi_probe(void) {
    int hw_inst_cnt = 2;
    int iter;
    struct pci1xxxx_spi *spi_bus;
    
    spi_bus = devm_kzalloc(sizeof(struct pci1xxxx_spi) + 
                           hw_inst_cnt * sizeof(struct pci1xxxx_spi_internal *));
    if (!spi_bus) {
        return -1;
    }
    
    spi_bus->total_hw_instances = hw_inst_cnt;
    
    for (iter = 0; iter < hw_inst_cnt; iter++) {
        spi_bus->spi_int[iter] = devm_kzalloc(sizeof(struct pci1xxxx_spi_internal));
        // CHECK-MESSAGES: Potential NULL pointer dereference if devm_kzalloc fails
        spi_bus->spi_int[iter]->hw_inst = iter; // Bug: No NULL check before dereference
        spi_bus->spi_int[iter]->spi_xfer_in_progress = false;
    }
    
    // Cleanup for demonstration
    for (iter = 0; iter < hw_inst_cnt; iter++) {
        if (spi_bus->spi_int[iter]) {
            free(spi_bus->spi_int[iter]);
        }
    }
    free(spi_bus);
    
    return 0;
}

int main() {
    // Simulate memory allocation failure for the second instance
    // This would cause a NULL pointer dereference in the original code
    printf("Testing pci1xxxx_spi_probe with potential NULL dereference\n");
    
    // In a real scenario, if devm_kzalloc fails for spi_bus->spi_int[iter],
    // the next line would dereference NULL
    pci1xxxx_spi_probe();
    
    return 0;
}