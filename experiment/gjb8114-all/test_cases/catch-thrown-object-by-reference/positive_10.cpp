#include <iostream>

struct AppError {
    int code;
};

using ErrorAlias = AppError;

int main() {
    try {
        throw AppError{5};
    }
    catch (ErrorAlias& e) {
        std::cout << e.code << std::endl;
    }
    return 0;
}
