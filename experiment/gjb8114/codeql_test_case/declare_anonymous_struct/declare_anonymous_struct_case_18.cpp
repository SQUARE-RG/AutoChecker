#include <stdio.h>

typedef struct {
    int x;
    int y;
} Point;  // 符合：typedef定义的结构体

struct Shape {
    Point start;
    Point end;
};

int main(void) {
    struct Shape s;
    s.start.x = 0;
    s.end.x = 10;
    return 0;
}