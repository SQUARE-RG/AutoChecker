#include <stdio.h>

void iterate_values(void) {
    int local_counter;  // 局部变量
    for (local_counter = 0; local_counter < 5; local_counter++) {  // 符合：使用局部变量作为循环控制变量
        printf("%d ", local_counter);
    }
}

int main(void) {
    iterate_values();
    return 0;
}