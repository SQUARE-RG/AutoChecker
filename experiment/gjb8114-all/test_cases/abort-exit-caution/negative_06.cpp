#include <cstdlib>
#include <functional>
#include <iostream>

using Handler = std::function<void(const char*)>;

void dispatch(Handler handler, const char* event) {
    handler(event);
}

int main() {
    Handler handler = [](const char* event) {
        if (event == nullptr) {
            std::cerr << "null event\n";
            std::exit(EXIT_FAILURE); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-3]
        }
        std::cout << event << "\n";
    };
    dispatch(handler, nullptr);
    return 0;
}
