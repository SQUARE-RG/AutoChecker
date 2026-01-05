#include <stdio.h>

struct Outer {
    struct Inner {
        int a;
        int b;
    } inner;  // 符合：命名嵌套结构体
};

int main(void) {
    struct Outer o;
    o.inner.a = 1;
    o.inner.b = 2;
    return 0;
}