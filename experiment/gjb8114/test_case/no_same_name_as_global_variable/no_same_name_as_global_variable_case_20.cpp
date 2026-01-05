#include <stdio.h>

int depth = 0;      // 全局变量
int max_depth = 10; // 全局变量

void recursive_function(int current_level) {  // 符合：参数与全局变量不同名
    if (current_level >= max_depth) {
        return;
    }
    
    int local_depth = current_level + 1;  // 符合：局部变量与全局变量不同名
    printf("Current level: %d, Local depth: %d, Global depth: %d\n", 
           current_level, local_depth, depth);
    
    if (local_depth < max_depth) {
        recursive_function(local_depth);
    }
}

int main(void) {
    depth = 0;
    recursive_function(0);
    return 0;
}