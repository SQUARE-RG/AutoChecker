#include <iostream>
struct Point {
    int x;
    int y;
};
void fun() {
    Point *p = new Point[2]{{1, 2}, {3, 4}};
    std::cout << p[0].x << p[1].y;
    delete[] p;
}
int main() {
    fun();
    return 0;
}
