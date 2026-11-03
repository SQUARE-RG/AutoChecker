#include <cstdlib>

int main() {
    int *buffer; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-7]
    buffer = static_cast<int *>(std::calloc(4, sizeof(int)));
    if (buffer != nullptr) {
        buffer[0] = 3;
        std::free(buffer);
    } else {
        return -1;
    }
    return 0;
}
