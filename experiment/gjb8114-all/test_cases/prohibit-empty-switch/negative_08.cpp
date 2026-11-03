#include <stdexcept>

void dispatch(unsigned int code) {
    try {
        if (code == 0U) {
            throw std::runtime_error("zero");
        }
    } catch (const std::runtime_error&) {
        switch (code) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-3]
        }
    }
}

int main() {
    dispatch(0U);
    return 0;
}
