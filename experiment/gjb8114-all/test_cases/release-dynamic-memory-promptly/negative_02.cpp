#include <cstdlib>

void fill() {
    int* buffer = static_cast<int*>(std::malloc(10 * sizeof(int))); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-3]
    if (buffer != nullptr) {
        buffer[0] = 42;
    }
}

int main() {
    fill();
    return 0;
}
