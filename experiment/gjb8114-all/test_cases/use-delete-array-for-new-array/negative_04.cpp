#include <iostream>
struct Point {
    int x;
    int y;
};
void fun() {
    Point *p = new Point[2]{{1, 2}, {3, 4}};
    std::cout << p[0].x << p[1].y;
    delete p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-2]
}
int main() {
    fun();
    return 0;
}
