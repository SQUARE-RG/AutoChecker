#include <cstdlib>

class Buffer {
public:
    void require_non_empty(int size) const {
        if (size == 0) {
            std::abort(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-3]
        }
    }
};

int main() {
    Buffer buffer;
    buffer.require_non_empty(0);
    return 0;
}
