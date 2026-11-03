#include <iostream>

struct FirstError {
    int code;
};

struct SecondError {
    int code;
};

int main() {
    int selector = 1;
    try {
        if (selector == 1) {
            throw FirstError{1};
        }
        throw SecondError{2};
    }
    catch (const FirstError &e) {
        std::cout << e.code << std::endl;
    }
    catch (SecondError e) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-3]
    {
        std::cout << e.code << std::endl;
    }
    return 0;
}
