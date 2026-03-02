#include <stdio.h>

int size = 100;  // 全局变量

struct Container {
    int capacity;
    
    void set_capacity(int new_capacity) {
        int size = new_capacity;  // 违反：成员函数内局部变量与全局变量同名
        // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
        capacity = size;
    }
};

int main(void) {
    struct Container c;
    c.set_capacity(200);
    printf("Global size: %d\n", size);
    return 0;
}