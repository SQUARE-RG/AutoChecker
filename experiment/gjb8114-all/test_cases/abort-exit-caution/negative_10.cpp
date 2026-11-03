#include <iostream>
#include <cstdlib>

struct ParseResult {
    bool ok;
    const char* message;
};

std::ostream& operator<<(std::ostream& out, const ParseResult& result) {
    if (!result.ok) {
        out << result.message;
        std::abort(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-3]
    }
    return out << "ok";
}

int main() {
    ParseResult result{false, "invalid input"};
    std::cout << result << '\n';
    return 0;
}
