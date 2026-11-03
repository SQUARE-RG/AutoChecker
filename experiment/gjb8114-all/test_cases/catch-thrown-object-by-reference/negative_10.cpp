#include <iostream>

struct AppError {
    int code;
};

int main() {
    auto handler = []() {
        try {
            throw AppError{7};
        }
        catch (AppError e) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-3]
            std::cout << e.code << std::endl;
        }
        return 0;
    };
    return handler();
}
