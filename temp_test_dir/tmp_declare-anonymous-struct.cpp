#include <stdio.h>

struct ArrayContainer {
    int numbers[5];
    struct Element {
        int id;
        char type;
    } elements[10];  // 符合：结构体数组成员
};

int main(void) {
    struct ArrayContainer ac;
    ac.numbers[0] = 1;
    ac.elements[0].id = 100;
    return 0;
}