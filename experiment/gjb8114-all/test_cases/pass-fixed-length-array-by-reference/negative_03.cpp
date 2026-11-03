#include <iostream>
using namespace std;

void fun(int p[10][20]) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-1]
{
    for (int i = 0; i < 10; ++i) {
        for (int j = 0; j < 20; ++j) {
            p[i][j] += 1;
        }
    }
}

int main() {
    int a[10][20] = {};
    fun(a);
    return 0;
}
