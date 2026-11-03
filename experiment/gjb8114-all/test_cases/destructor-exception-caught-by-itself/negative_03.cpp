#include <stdexcept>

class Resource {
public:
    Resource() : values{1, 2, 3} {}
    ~Resource() noexcept(false);
private:
    int values[3];
};

Resource::~Resource() noexcept(false) {
    for (int i = 0; i < 3; ++i) {
        if (values[i] == 2) {
            throw std::out_of_range("bad value"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-3-2]
        }
    }
}

int main() {
    try {
        Resource r;
    } catch (const std::out_of_range&) {
    }
    return 0;
}
