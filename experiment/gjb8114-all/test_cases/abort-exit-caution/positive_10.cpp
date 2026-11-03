#include <iostream>
#include <cstdlib>

struct ParseResult {
    bool ok;
    const char* message;
};

std::ostream& operator<<(std::ostream& out, const ParseResult& result) {
    if (result.ok) {
        return out << "ok";
    }
    return out << "error: " << result.message;
}

int main() {
    ParseResult result{false, "invalid input"};
    std::cout << result << '\n';
    return result.ok ? EXIT_SUCCESS : EXIT_FAILURE;
}
