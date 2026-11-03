#include <iostream>
using namespace std;

class A1 {
public:
    A1() {}
};

class A2 {
public:
    A2() {}
};

int main() {
    int i = 0;
    try {
        if (i > 0) {
            throw A1();
        } else {
            throw A2(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-2]
        }
    } catch (A1 &) {
        cout << "exception:A1" << endl;
    }
    return 0;
}
