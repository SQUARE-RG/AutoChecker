#include <iostream>

enum class ErrorCode { ok, failure };

int main() {
    try {
        throw ErrorCode::failure;
    } catch (ErrorCode code) {
        std::cout << (code == ErrorCode::failure) << std::endl;
    }
    return 0;
}
