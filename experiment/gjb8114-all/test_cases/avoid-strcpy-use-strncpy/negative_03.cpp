#include <cstring>

namespace {
char* copy_label(char* out, const char* label) {
    return std::strcpy(out, label); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-4]
}
}

int main() {
    char label[16]{};
    copy_label(label, "widget");
    return label[0] == 'w' ? 0 : 1;
}
