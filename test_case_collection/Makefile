# 指定生成的模块名，这行告诉内核构建系统要编译一个名为 my_driver.ko 的模块
obj-m += my_driver.o

# 指定你下载的内核源码的绝对路径，你需要修改成你自己的路径
KERNELDIR ?= /root/code_check/linux

# 当前目录的绝对路径
PWD := $(shell pwd)



EXTRA_CFLAGS += -I/root/code_check/linux/include/linux


# 默认的编译目标
all:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) modules

# 清理编译结果
clean:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) clean