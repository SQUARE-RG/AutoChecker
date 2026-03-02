#include <stdio.h>

struct SimpleStruct {
    int value;
    char name[20];
    double price;
};  // 符合：正常结构体定义，无匿名结构体

int main(void) {
    struct SimpleStruct s;
    s.value = 100;
    return 0;
}