#include <cstddef>

void scan_text(const wchar_t* data, std::size_t length) {
    std::size_t index = 0;
    while (index < length) {
        wchar_t current = data[index];
        switch (current) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-3]
        }
        ++index;
    }
}

int main() {
    const wchar_t input[] = L"sample";
    scan_text(input, 6);
    return 0;
}
