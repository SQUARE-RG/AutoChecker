#include <stdio.h>

struct Node {
    int data;
    struct Node *next;  // 符合：结构体指针成员
};

int main(void) {
    struct Node n1, n2;
    n1.data = 1;
    n2.data = 2;
    n1.next = &n2;
    return 0;
}