#include <iostream>
struct MyError {
    int code;
};
typedef MyError ErrorAlias;
int main() {
    try {
        MyError err{42};
        throw err;
    } catch (ErrorAlias e) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-3]
        std::cout << e.code;
    }
    return 0;
}
