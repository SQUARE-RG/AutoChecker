#include <cstdlib>

int read_config(bool file_exists) {
    if (!file_exists) {
        std::exit(1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-3]
    }
    return 0;
}

int main() {
    read_config(false);
    return 0;
}
