#include <stdio.h>

struct Data {
    float value;
};

int main(void) {
    struct Data d = {8.88f};
    int i;
    i = d.value;  // 违反：结构体浮点成员直接赋给int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
    return 0;
}