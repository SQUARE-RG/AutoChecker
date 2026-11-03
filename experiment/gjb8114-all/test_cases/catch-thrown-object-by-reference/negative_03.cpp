#include <iostream>

struct MyError {
    int code;
};

int main() {
    try {
        throw MyError{7};
    }
    catch (const MyError e) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-3]
    {
        std::cout << e.code << '\n';
    }
    return 0;
}
