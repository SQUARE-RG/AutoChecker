#include <stdio.h>

int max_capacity = 1000;  // 全局变量

struct Storage {
    int current_size;
    
    void resize(int new_size) {  // 符合：参数与全局变量不同名
        if (new_size > max_capacity) {
            current_size = max_capacity;
        } else {
            current_size = new_size;
        }
        printf("Resized to: %d (max: %d)\n", current_size, max_capacity);
    }
};

int main(void) {
    struct Storage s;
    s.resize(500);
    return 0;
}