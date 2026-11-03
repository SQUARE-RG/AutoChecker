#include <iostream>

class Buffer {
public:
    Buffer() {
        arr[0] = 1;
        arr[1] = 2;
        arr[2] = 3;
    }

    int (&get_array())[3] { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-3]
        return arr;
    }

private:
    int arr[3];
};

int main() {
    Buffer b;
    int (&ref)[3] = b.get_array();
    ref[0] = 99;
    std::cout << ref[0] << std::endl;
    return 0;
}
