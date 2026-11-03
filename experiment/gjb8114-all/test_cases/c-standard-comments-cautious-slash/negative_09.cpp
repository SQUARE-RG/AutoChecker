#include <iostream>

using namespace std; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-2-3]

int main() {
    /* Use a standard C comment within the body. */
    int value = 42;
    cout << value << endl;
    return 0;
}
