#include <errno.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#define MAX_HW_INST 4

struct device {
	int dummy;
};

struct spi_controller {
	unsigned int num_chipselect;
};

struct pci1xxxx_spi_internal {
	struct spi_controller *spi_host;
	bool spi_xfer_in_progress;
};

struct pci1xxxx_spi {
	struct pci1xxxx_spi_internal *spi_int[MAX_HW_INST];
	size_t total_hw_instances;
};

static void *devm_kzalloc(struct device *dev, size_t size)
{
	(void)dev;
	return calloc(1, size);
}

static struct spi_controller *devm_spi_alloc_host(struct device *dev, size_t size)
{
	(void)size;
	return devm_kzalloc(dev, sizeof(struct spi_controller));
}

int pci1xxxx_spi_probe(struct device *dev, size_t hw_inst_cnt)
{
	struct pci1xxxx_spi spi_bus = {0};

	if (hw_inst_cnt > MAX_HW_INST)
		return -EINVAL;

	spi_bus.total_hw_instances = hw_inst_cnt;

	for (size_t iter = 0; iter < hw_inst_cnt; ++iter) {
		spi_bus.spi_int[iter] = devm_kzalloc(dev,
				      sizeof(struct pci1xxxx_spi_internal));
		if (!spi_bus.spi_int[iter])
			return -ENOMEM;

		struct pci1xxxx_spi_internal *spi_sub_ptr = spi_bus.spi_int[iter];

		spi_sub_ptr->spi_host = devm_spi_alloc_host(dev, sizeof(struct spi_controller));
		if (!spi_sub_ptr->spi_host)
			return -ENOMEM;

		spi_sub_ptr->spi_xfer_in_progress = false;
	}

	return 0;
}

int main(void)
{
	struct device dev = {0};
	return pci1xxxx_spi_probe(&dev, 2);
}
