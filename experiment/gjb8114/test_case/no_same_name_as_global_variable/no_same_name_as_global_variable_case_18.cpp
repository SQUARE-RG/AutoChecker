#include <stdio.h>

int* global_ptr = NULL;  // 全局指针变量

void use_local_pointer(void) {
    int value = 42;
    int* local_ptr = &value;  // 符合：局部指针与全局指针不同名
    printf("Local pointer value: %d\n", *local_ptr);
    
    if (global_ptr != NULL) {
        printf("Global pointer value: %d\n", *global_ptr);
    }
}

int main(void) {
    int x = 100;
    global_ptr = &x;
    use_local_pointer();
    return 0;
}