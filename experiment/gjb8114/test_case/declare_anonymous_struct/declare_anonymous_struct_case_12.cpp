#include <stdio.h>

struct Container {
    struct Data {
        int x;
        float y;
    } data;  // 符合：有变量名的嵌套结构体
};

int main(void) {
    struct Container c;
    c.data.x = 10;
    c.data.y = 3.14;
    return 0;
}