#include <iostream>

struct Error {
    int code;
};

int main() {
    try {
        throw Error{42};
    }
    catch (Error) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-3]
    {
        std::cout << "caught" << std::endl;
    }
    return 0;
}
