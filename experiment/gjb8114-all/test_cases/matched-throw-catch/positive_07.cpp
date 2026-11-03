#include <iostream>

enum class ErrorCode { Bad, Worse };

int main() {
    try {
        throw ErrorCode::Bad;
    } catch (const ErrorCode&) {
        std::cout << "ErrorCode caught" << std::endl;
    }
    return 0;
}
