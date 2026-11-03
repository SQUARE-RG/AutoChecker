#include <cstdlib>
#include <cstring>

int main() {
    char *buffer = static_cast<char *>(std::malloc(32));
    std::strcpy(buffer, "hello"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-8]
    std::free(buffer);
    return 0;
}
