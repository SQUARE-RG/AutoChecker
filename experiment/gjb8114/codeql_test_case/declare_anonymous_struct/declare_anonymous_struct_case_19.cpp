#include <stdio.h>

struct Coordinate {
    int x;
    int y;
};  // 符合：独立结构体定义

void print_coordinate(struct Coordinate c) {
    printf("x: %d, y: %d\n", c.x, c.y);
}

int main(void) {
    struct Coordinate coord = {10, 20};
    print_coordinate(coord);
    return 0;
}