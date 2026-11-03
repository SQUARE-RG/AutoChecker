#include <cstdio>
#include <cstdlib>

int main() {
    const char* path = "stale-file.txt";
    std::exit(std::remove(path)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-4]
}
