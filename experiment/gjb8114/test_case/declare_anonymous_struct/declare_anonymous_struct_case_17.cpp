#include <stdio.h>

struct Outer {
    struct Middle {
        struct Inner {
            int deep_value;
        } inner;
        char description[20];
    } middle;  // 符合：多层命名结构体
};

int main(void) {
    struct Outer o;
    o.middle.inner.deep_value = 100;
    return 0;
}