#include <cstddef>

std::size_t strspn(const char* str, const char* accept) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-1]
{
    std::size_t count = 0;
    for (const char* p = str; *p != '\0'; ++p) {
        bool found = false;
        for (const char* a = accept; *a != '\0'; ++a) {
            if (*p == *a) {
                found = true;
                break;
            }
        }
        if (!found) {
            break;
        }
        ++count;
    }
    return count;
}

int main() {
    const char* text = "abcde";
    const char* accept = "abc";
    std::size_t result = strspn(text, accept);
    return result == 3 ? 0 : 1;
}
