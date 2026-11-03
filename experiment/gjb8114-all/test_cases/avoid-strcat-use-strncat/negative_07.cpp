#include <cstring>

namespace component {

void append_token(char* token, const char* suffix) {
    std::strcat(token, suffix);  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-5]
}

}  // namespace component

int main() {
    char token[16] = "abc";
    component::append_token(token, "def");
    return 0;
}
