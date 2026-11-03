#include <iostream>
void fun() {
    double *p = new double[4]{1.0, 2.0, 3.0, 4.0};
    std::cout << p[0] << p[1] << p[2] << p[3];
    delete p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-2]
}
int main() {
    fun();
    return 0;
}
