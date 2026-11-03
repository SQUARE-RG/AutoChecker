#include <iostream>

class IntArray {
public:
    IntArray() : values{1, 2, 3} {}

    int& operator[](int index) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-3]
        return values[index];
    }

private:
    int values[3];
};

int main() {
    IntArray arr;
    arr[0] = 100;
    return 0;
}
